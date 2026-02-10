"""Client repository for database operations."""
from sqlalchemy.orm import Session
from typing import Optional

from models.client import ClientModel
from repositories.base_repository_impl import BaseRepositoryImpl
from schemas.client_schema import ClientSchema


class ClientRepository(BaseRepositoryImpl):
    """Repository for Client entity database operations."""

    def __init__(self, db: Session):
        super().__init__(ClientModel, ClientSchema, db)

    def get_by_email(self, email: str) -> Optional[ClientModel]:
        """Get client by email."""
        return self.session.query(ClientModel).filter(ClientModel.email == email).first()
