from sqlalchemy.orm import Session
from models.client import ClientModel
from repositories.client_repository import ClientRepository
from schemas.client_schema import ClientSchema
from services.base_service_impl import BaseServiceImpl


class ClientService(BaseServiceImpl):
    def __init__(self, db: Session):
        super().__init__(
            repository_class=ClientRepository,
            model=ClientModel,
            schema=ClientSchema,
            db=db
        )

    def authenticate(self, email: str, password: str):
        """Authenticate a client by email and password."""
        client = self.repository.get_by_email(email)
        if client and client.password == password:
            return client
        return None

