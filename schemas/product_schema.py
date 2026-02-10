from typing import Optional, List, TYPE_CHECKING
from pydantic import Field, ConfigDict
from schemas.base_schema import BaseSchema
from schemas.category_schema import CategoryBaseSchema

if TYPE_CHECKING:
    from schemas.review_schema import ReviewSchema

# ✅ ESQUEMA BASE: Solo datos simples (sin objetos complejos)
class ProductBaseSchema(BaseSchema):
    name: str = Field(..., min_length=1, max_length=200)
    price: float = Field(..., gt=0)
    stock: int = Field(default=0, ge=0)
    image_url: Optional[str] = Field(None)
    category_id: Optional[int] = Field(None)
    active: bool = True # Vital para el borrado lógico

# ✅ ESQUEMA DE LECTURA: Aquí sí incluimos los objetos anidados
class ProductSchema(ProductBaseSchema):
    model_config = ConfigDict(from_attributes=True)
    
    # Estos campos son solo para mostrar datos, no para guardar
    category: Optional[CategoryBaseSchema] = None 
    reviews: Optional[List['ReviewSchema']] = []

# ✅ ESQUEMAS DE ESCRITURA: Limpios (heredan de Base)
class ProductCreateSchema(ProductBaseSchema):
    pass

class ProductUpdateSchema(ProductBaseSchema):
    pass

class ProductAdminSchema(ProductBaseSchema):
    pass