from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from models.base_model import BaseModel

class ProductModel(BaseModel):
    __tablename__ = "products"

    name = Column(String(200), nullable=False)
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    image_url = Column(String, nullable=True)
    active = Column(Boolean, default=True) # ✅ Nuevo campo para borrado lógico

    category_id = Column(Integer, ForeignKey("categories.id_key"))
    category = relationship("CategoryModel", back_populates="products")
    
    reviews = relationship("ReviewModel", back_populates="product", cascade="all, delete-orphan")
    order_details = relationship("OrderDetailModel", back_populates="product")