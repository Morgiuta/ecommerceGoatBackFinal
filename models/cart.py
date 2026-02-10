from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from models.base_model import BaseModel
# Importamos modelos relacionados para evitar errores de referencia circular en strings
from models.client import ClientModel
from models.product import ProductModel

class CartModel(BaseModel):
    __tablename__ = "carts"
    
    # Relación 1 a 1: Un cliente tiene un único carrito
    client_id = Column(Integer, ForeignKey("clients.id_key"), unique=True, index=True)
    
    # Relación con items: Si borras el carrito, se borran sus items
    items = relationship("CartItemModel", back_populates="cart", cascade="all, delete-orphan", lazy="selectin")
    
    # Relación inversa con cliente
    client = relationship("ClientModel", lazy="joined")

class CartItemModel(BaseModel):
    __tablename__ = "cart_items"

    cart_id = Column(Integer, ForeignKey("carts.id_key"), index=True)
    product_id = Column(Integer, ForeignKey("products.id_key"))
    quantity = Column(Integer, default=1)

    cart = relationship("CartModel", back_populates="items")
    product = relationship("ProductModel", lazy="joined") # Carga los datos del producto (precio, nombre, imagen)

    # Constraint: Evita tener dos filas para el mismo producto en el mismo carrito (se debe sumar cantidad)
    __table_args__ = (UniqueConstraint('cart_id', 'product_id', name='uix_cart_product'),)