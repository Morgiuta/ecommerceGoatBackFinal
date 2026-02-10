from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from pydantic import Field, ConfigDict
from schemas.base_schema import BaseSchema
from models.enums import DeliveryMethod, Status

if TYPE_CHECKING:
    from schemas.client_schema import ClientSchema
    from schemas.bill_schema import BillSchema
    from schemas.order_detail_schema import OrderDetailSchema

# 1. BASE
class OrderBaseSchema(BaseSchema):
    total: float = Field(..., ge=0, description="Total amount")
    delivery_method: DeliveryMethod = Field(..., description="Delivery method")
    client_id: int = Field(..., description="Client ID")
    bill_id: int = Field(..., description="Bill ID")

# 2. CREATE
class OrderCreateSchema(OrderBaseSchema):
    pass

# 3. UPDATE (✅ ESTO ES LO QUE NECESITAS)
# Permite enviar solo el status sin obligar a enviar el resto
class OrderUpdateSchema(BaseSchema):
    total: Optional[float] = None
    delivery_method: Optional[DeliveryMethod] = None
    status: Optional[Status] = None 

# 4. RESPONSE
class OrderSchema(OrderBaseSchema):
    id_key: int
    date: datetime
    status: Status
    
    client: Optional["ClientSchema"] = None
    bill: Optional["BillSchema"] = None
    details: List["OrderDetailSchema"] = []
    
    model_config = ConfigDict(from_attributes=True)
    
class OrderStatusUpdate(BaseSchema):
    status: int