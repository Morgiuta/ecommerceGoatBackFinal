from sqlalchemy import Column, String, Boolean  # ✅ Importar Boolean
from sqlalchemy.orm import relationship

from models.base_model import BaseModel


class ClientModel(BaseModel):
    __tablename__ = "clients"

    name = Column(String, index=True)
    lastname = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    telephone = Column(String)
    password = Column(String)
    
   
    is_admin = Column(Boolean, default=False)

    addresses = relationship("AddressModel", back_populates="client", cascade="all, delete-orphan", lazy="select")
    orders = relationship("OrderModel", back_populates="client", lazy="select")
    bills = relationship("BillModel", back_populates="client", lazy="select")