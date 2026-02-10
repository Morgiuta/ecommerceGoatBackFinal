"""Category repository with controlled relationship loading."""
from typing import List
from sqlalchemy.orm import Session, selectinload
from models.category import CategoryModel
from repositories.base_repository_impl import BaseRepositoryImpl
from schemas.category_schema import CategorySchema


class CategoryRepository(BaseRepositoryImpl):
    """Repository for Category entity with optimized relationship loading."""

    def __init__(self, db: Session):
        super().__init__(CategoryModel, CategorySchema, db)

    def find_all(self, skip: int = 0, limit: int = 100) -> List[CategorySchema]:
        """
        Get all categories with products but WITHOUT nested order_details.
        This prevents the cyclic reference issue.
        """
        categories = (
            self.session.query(CategoryModel)
            .options(
                # ✅ Carga products pero NO sus order_details
                selectinload(CategoryModel.products).lazyload('*')
            )
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        # ✅ Convertir a schema usando model_validate
        return [CategorySchema.model_validate(category) for category in categories]

    def find(self, id_key: int) -> CategorySchema:
        """Get single category with products but without nested relations."""
        category = (
            self.session.query(CategoryModel)
            .options(
                selectinload(CategoryModel.products).lazyload('*')
            )
            .filter(CategoryModel.id_key == id_key)
            .first()
        )
        
        if not category:
            from repositories.base_repository_impl import InstanceNotFoundError
            raise InstanceNotFoundError(
                f"Category with id {id_key} not found"
            )
        
        return CategorySchema.model_validate(category)