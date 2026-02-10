"""Client schema for request/response validation."""
from typing import Optional
from pydantic import EmailStr, Field, ConfigDict
from schemas.base_schema import BaseSchema

# 1. BASE: Hacemos name y lastname OPCIONALES
class ClientBaseSchema(BaseSchema):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    lastname: Optional[str] = Field(None, min_length=1, max_length=100)
    email: EmailStr = Field(...)
    telephone: Optional[str] = Field(None)
    is_admin: bool = Field(default=False)

# 2. RESPONSE (GET)
class ClientSchema(ClientBaseSchema):
    id_key: int
    model_config = ConfigDict(from_attributes=True)

# 3. CREATE (POST): Solo password y email son obligatorios ahora
class ClientCreateSchema(ClientBaseSchema):
    password: str = Field(..., min_length=1, description="Password required")

# 4. UPDATE (PUT)
class ClientUpdateSchema(BaseSchema):
    name: Optional[str] = None
    lastname: Optional[str] = None
    email: Optional[EmailStr] = None
    telephone: Optional[str] = None
    password: Optional[str] = None
    is_admin: Optional[bool] = None