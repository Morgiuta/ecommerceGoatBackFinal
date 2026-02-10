"""OrderDetail service with foreign key validation and stock management."""
import logging
from sqlalchemy.orm import Session
from sqlalchemy import select

from models.order_detail import OrderDetailModel
from models.product import ProductModel
from repositories.order_detail_repository import OrderDetailRepository
from repositories.order_repository import OrderRepository
from repositories.product_repository import ProductRepository
from repositories.base_repository_impl import InstanceNotFoundError
from schemas.order_detail_schema import OrderDetailSchema
from services.base_service_impl import BaseServiceImpl
from utils.logging_utils import get_sanitized_logger

logger = get_sanitized_logger(__name__)


class OrderDetailService(BaseServiceImpl):
    """Service for OrderDetail entity with validation and stock management."""

    def __init__(self, db: Session):
        super().__init__(
            repository_class=OrderDetailRepository,
            model=OrderDetailModel,
            schema=OrderDetailSchema,
            db=db
        )
        # Inicializamos repositorios auxiliares
        self._order_repository = OrderRepository(db)
        self._product_repository = ProductRepository(db)

    def save(self, schema: OrderDetailSchema) -> OrderDetailSchema:
        """
        Create a new order detail and subtract stock atomically.
        """
       
        try:
            self._order_repository.find(schema.order_id)
        except InstanceNotFoundError:
            logger.error(f"Order with id {schema.order_id} not found")
            raise InstanceNotFoundError(f"Order with id {schema.order_id} not found")

        
        stmt = select(ProductModel).where(
            ProductModel.id_key == schema.product_id
        ).with_for_update()

        product_model = self._product_repository.session.execute(stmt).scalar_one_or_none()

        if product_model is None:
            logger.error(f"Product with id {schema.product_id} not found")
            raise InstanceNotFoundError(f"Product with id {schema.product_id} not found")

        
        if product_model.stock < schema.quantity:
            error_msg = f"Stock insuficiente para {product_model.name}. Solicitado: {schema.quantity}, Disponible: {product_model.stock}"
            logger.error(error_msg)
            raise ValueError(error_msg)

      
        if schema.price is None:
            schema.price = product_model.price
        

        product_model.stock -= schema.quantity
        
        logger.info(f"Descontando {schema.quantity} unidades de producto {schema.product_id}. Nuevo stock: {product_model.stock}")

  
        try:
           
            return super().save(schema)
        except Exception as e:
            logger.error(f"Error saving order detail: {e}")
            raise

    def update(self, id_key: int, schema: OrderDetailSchema) -> OrderDetailSchema:
        """
        Update order detail quantity and adjust stock accordingly.
        """
  
        existing_detail = self._repository.find(id_key)
        
   
        if schema.quantity is not None and schema.quantity != existing_detail.quantity:
            
            product_id = existing_detail.product_id
            
            stmt = select(ProductModel).where(ProductModel.id_key == product_id).with_for_update()
            product_model = self._product_repository.session.execute(stmt).scalar_one_or_none()
            
            if not product_model:
                raise InstanceNotFoundError("Product not found")

         
            diff = schema.quantity - existing_detail.quantity
            
            # Si necesito más stock, valido que haya
            if diff > 0 and product_model.stock < diff:
                raise ValueError(f"Stock insuficiente para aumentar cantidad. Disponible: {product_model.stock}")

            product_model.stock -= diff
            logger.info(f"Ajustando stock producto {product_id} en {diff*-1}")

        return super().update(id_key, schema)

    def delete(self, id_key: int) -> None:
        """
        Delete order detail and RESTORE stock.
        """
       
        try:
            detail = self._repository.find(id_key)
        except InstanceNotFoundError:
            raise

        stmt = select(ProductModel).where(ProductModel.id_key == detail.product_id).with_for_update()
        product_model = self._product_repository.session.execute(stmt).scalar_one_or_none()

        if product_model:
           
            product_model.stock += detail.quantity
            logger.info(f"Restaurando {detail.quantity} unidades al producto {detail.product_id}")

        
        super().delete(id_key)