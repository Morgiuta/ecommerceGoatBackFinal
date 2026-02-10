from sqlalchemy import Column, Integer, ForeignKey, DateTime, Float, Enum
from sqlalchemy.orm import relationship
from datetime import datetime

from models.base_model import BaseModel
from models.enums import DeliveryMethod, Status

class OrderModel(BaseModel):
    __tablename__ = "orders"

    date = Column(DateTime, default=datetime.utcnow)
    total = Column(Float, nullable=False)
    delivery_method = Column(Enum(DeliveryMethod), nullable=False)
    status = Column(Enum(Status), default=Status.PENDING)
    
    client_id = Column(Integer, ForeignKey("clients.id_key"))
    bill_id = Column(Integer, ForeignKey("bills.id_key"))

    client = relationship("ClientModel", back_populates="orders")
    bill = relationship("BillModel", back_populates="order")
    details = relationship("OrderDetailModel", back_populates="order", cascade="all, delete-orphan")