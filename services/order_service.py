import logging
from sqlalchemy.orm import Session
from datetime import datetime

from models.order import OrderModel
from repositories.order_repository import OrderRepository
from repositories.client_repository import ClientRepository
from repositories.bill_repository import BillRepository
from repositories.base_repository_impl import InstanceNotFoundError
from schemas.order_schema import OrderSchema
from services.base_service_impl import BaseServiceImpl
from utils.logging_utils import get_sanitized_logger
from models.enums import Status

logger = get_sanitized_logger(__name__)


class OrderService(BaseServiceImpl):

    def __init__(self, db: Session):
        super().__init__(
            repository_class=OrderRepository,
            model=OrderModel,
            schema=OrderSchema,
            db=db
        )
        self._client_repository = ClientRepository(db)
        self._bill_repository = BillRepository(db)

    def save(self, schema) -> OrderSchema:
        
        # Convert to dict to check fields safely
        order_data = schema.model_dump(exclude_unset=True)

        if "client_id" not in order_data or order_data["client_id"] is None:
            raise ValueError("client_id is required")
        if "bill_id" not in order_data or order_data["bill_id"] is None:
            raise ValueError("bill_id is required")
        if "total" not in order_data or order_data["total"] is None:
            raise ValueError("total is required")
        if "delivery_method" not in order_data or order_data["delivery_method"] is None:
            raise ValueError("delivery_method is required")
        
        client_id = order_data["client_id"]
        bill_id = order_data["bill_id"]

        try:
            self._client_repository.find(client_id)
        except InstanceNotFoundError:
            logger.error(f"Client with id {client_id} not found")
            raise InstanceNotFoundError(f"Client with id {client_id} not found")

        try:
            self._bill_repository.find(bill_id)
        except InstanceNotFoundError:
            logger.error(f"Bill with id {bill_id} not found")
            raise InstanceNotFoundError(f"Bill with id {bill_id} not found")

        # Create Model directly to inject defaults safely
        final_data = order_data.copy()
        if "date" not in final_data:
            final_data["date"] = datetime.utcnow()
        if "status" not in final_data:
            final_data["status"] = Status.PENDING

        logger.info(f"Creating order for client {client_id}")
        
        item = self._model(**final_data)
        
        return self._repository.save(item)

    def update(self, id_key: int, schema: OrderSchema) -> OrderSchema:
        if schema.client_id is not None:
            try:
                self._client_repository.find(schema.client_id)
            except InstanceNotFoundError:
                logger.error(f"Client with id {schema.client_id} not found")
                raise InstanceNotFoundError(f"Client with id {schema.client_id} not found")

        if schema.bill_id is not None:
            try:
                self._bill_repository.find(schema.bill_id)
            except InstanceNotFoundError:
                logger.error(f"Bill with id {schema.bill_id} not found")
                raise InstanceNotFoundError(f"Bill with id {schema.bill_id} not found")

        if schema.total is not None and schema.total < 0:
            raise ValueError("total must be >= 0")

        logger.info(f"Updating order {id_key}")
        return super().update(id_key, schema)