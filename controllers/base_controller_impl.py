from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from config.database import get_db
from repositories.base_repository_impl import InstanceNotFoundError
from typing import Type, Callable, Optional


class BaseControllerImpl:
    """
    Controlador genérico base para CRUD.
    Permite definir:
    - schema → respuesta
    - create_schema → POST
    - update_schema → PUT
    """

    def __init__(
        self,
        schema: Type,
        service_factory: Callable,
        create_schema: Optional[Type] = None,
        update_schema: Optional[Type] = None,
        tags=None
    ):
        self.schema = schema
        self.create_schema = create_schema or schema
        self.update_schema = update_schema or schema
        self.service_factory = service_factory
        self.tags = tags or []
        self.router = APIRouter(tags=self.tags)
        self._register_routes()

    def _register_routes(self):
        # GET por ID
        @self.router.get("/id/{id_key}", response_model=self.schema)
        async def get_by_id(id_key: int, db: Session = Depends(get_db)):
            try:
                service = self.service_factory(db)
                # ✅ CORRECCIÓN: Usamos .get_one() (el nombre correcto en tus servicios)
                return service.get_one(id_key) 
            except InstanceNotFoundError:
                raise HTTPException(404, f"Entidad con ID {id_key} no encontrada")
            except Exception as e:
                raise HTTPException(500, f"Error interno: {str(e)}")

        # GET lista
        @self.router.get("/", response_model=list[self.schema])
        async def get_all(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
            try:
                service = self.service_factory(db)
                return service.get_all(skip=skip, limit=limit)
            except Exception as e:
                raise HTTPException(500, f"Error al obtener entidades: {str(e)}")

        # POST crear
        @self.router.post("/", response_model=self.schema)
        async def create(entity: self.create_schema, db: Session = Depends(get_db)):
            try:
                service = self.service_factory(db)
                return service.save(entity)
            except Exception as e:
                raise HTTPException(400, f"Error al crear: {str(e)}")

        # PUT actualizar
        @self.router.put("/id/{id_key}", response_model=self.schema)
        async def update(id_key: int, entity: self.update_schema, db: Session = Depends(get_db)):
            try:
                service = self.service_factory(db)
                return service.update(id_key, entity)
            except InstanceNotFoundError:
                raise HTTPException(404, f"Entidad con ID {id_key} no encontrada")
            except Exception as e:
                raise HTTPException(400, f"Error al actualizar: {str(e)}")

        # DELETE eliminar
        @self.router.delete("/id/{id_key}")
        async def delete(id_key: int, db: Session = Depends(get_db)):
            try:
                service = self.service_factory(db)
                service.delete(id_key)
                return {"deleted": True}
            except InstanceNotFoundError:
                raise HTTPException(404, f"Entidad con ID {id_key} no encontrada")
            except Exception as e:
                raise HTTPException(400, f"Error al eliminar: {str(e)}")