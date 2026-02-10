from typing import Optional
from pydantic import BaseModel

class BaseSchema(BaseModel):
    class Config:
        from_attributes = True

    id_key: Optional[int] = None
