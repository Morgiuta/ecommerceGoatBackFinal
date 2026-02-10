from fastapi import APIRouter
from sqlalchemy import inspect
from config.database import engine

router = APIRouter()

@router.get("/debug/tables")
def debug_tables():
    inspector = inspect(engine)
    return {"tables": inspector.get_table_names()}
