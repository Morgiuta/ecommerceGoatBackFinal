"""Category schema with validation."""
from typing import Optional, List, TYPE_CHECKING
from pydantic import Field

from schemas.base_schema import BaseSchema

if TYPE_CHECKING:
    from schemas.product_schema import ProductSchema


class CategoryBaseSchema(BaseSchema):
    """
    Schema básico de categoría SIN productos.
    Usado para evitar referencias cíclicas en ProductSchema.
    """
    name: str = Field(..., min_length=1, max_length=100, description="Category name (required, unique)")


class CategorySchema(CategoryBaseSchema):
    """
    Schema completo de categoría CON productos.
    Solo usar cuando explícitamente necesites la lista de productos.
    """
    products: Optional[List['ProductSchema']] = []


class CategoryListSchema(CategoryBaseSchema):
    """
    Schema para LISTAR categorías SIN productos anidados.
    Úsalo en GET /categories/ para evitar ciclos.
    """
    products_count: Optional[int] = Field(None, description="Number of products in category")