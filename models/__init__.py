"""
This is the __init__.py file for the models package.

It imports all the models for easier access.
"""

from models.base_model import BaseModel
from models.address import AddressModel
from models.bill import BillModel
from models.category import CategoryModel
from models.client import ClientModel
from models.order import OrderModel
from models.order_detail import OrderDetailModel
from models.product import ProductModel
from models.review import ReviewModel

# ✅ Nuevos modelos de Carrito agregados
from models.cart import CartModel, CartItemModel