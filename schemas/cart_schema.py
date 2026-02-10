from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from schemas.product_schema import ProductSchema

class CartItemBase(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)

class CartItemResponse(CartItemBase):
    id_key: int
    product: Optional[ProductSchema] = None
    
    # Nuevo campo: Mensaje de ajuste (ej: "Ajustado de 5 a 2 por falta de stock")
    adjustment_message: Optional[str] = None 
    
    model_config = ConfigDict(from_attributes=True)

class CartResponse(BaseModel):
    id_key: int
    client_id: int
    items: List[CartItemResponse] = []
    total: float = 0.0
    
    # Bandera global para saber si hubo cambios en algún item
    has_adjustments: bool = False
    
    model_config = ConfigDict(from_attributes=True)