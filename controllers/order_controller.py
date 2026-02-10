from typing import List
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, desc

from config.database import get_db
from controllers.base_controller_impl import BaseControllerImpl
from schemas.order_schema import OrderSchema, OrderCreateSchema, OrderUpdateSchema, OrderStatusUpdate
from services.order_service import OrderService
from models.order import OrderModel
from models.enums import Status
# ✅ Importamos la excepción para capturarla
from repositories.base_repository_impl import InstanceNotFoundError

class OrderController(BaseControllerImpl):
    def __init__(self):
        super().__init__(
            schema=OrderSchema,
            create_schema=OrderCreateSchema,
            update_schema=OrderUpdateSchema,
            service_factory=lambda db: OrderService(db),
            tags=["Orders"]
        )
        self._register_custom_routes()

    def _register_custom_routes(self):
        
        @self.router.get("/client/{client_id}", response_model=List[OrderSchema])
        async def get_orders_by_client(client_id: int, db: Session = Depends(get_db)):
            stmt = (
                select(OrderModel)
                .where(OrderModel.client_id == client_id)
                .order_by(desc(OrderModel.date))
            )
            orders = db.execute(stmt).scalars().all()
            return orders

        @self.router.patch("/id/{id}/status", response_model=OrderSchema)
        async def update_order_status(id: int, status_data: OrderStatusUpdate, db: Session = Depends(get_db)):
            service = self.service_factory(db)
            
            try:
                # Convertimos el entero (ej: 2) al Enum (Status.IN_PROGRESS)
                new_status = Status(status_data.status)
                
                # ✅ SOLUCIÓN DEFINITIVA: 
                # Usamos el repositorio directamente para actualizar.
                # service.repository.update(id, cambios) se encarga de buscar, 
                # actualizar el modelo, hacer commit y devolver el schema actualizado.
                updated_order = service.repository.update(id, {"status": new_status})
                
                return updated_order

            except ValueError:
                # Si el status no es válido (ej: enviar 99)
                raise HTTPException(status_code=400, detail="Invalid status value")
            except InstanceNotFoundError:
                # Si el ID no existe
                raise HTTPException(status_code=404, detail="Order not found")