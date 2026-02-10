from sqlalchemy import Column, Integer, ForeignKey, Float
from sqlalchemy.orm import relationship
from models.base_model import BaseModel

class OrderDetailModel(BaseModel):
    __tablename__ = "order_details"

    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    
    order_id = Column(Integer, ForeignKey("orders.id_key"))
    product_id = Column(Integer, ForeignKey("products.id_key"))

    # ✅ IMPORTANTE: Usa strings "OrderModel" y "ProductModel"
    # No hagas: from models.order import OrderModel
    order = relationship("OrderModel", back_populates="details")
    product = relationship("ProductModel")