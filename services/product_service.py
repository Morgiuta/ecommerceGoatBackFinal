import logging
import os
from typing import List, Optional
from sqlalchemy.orm import Session

from models.product import ProductModel
from repositories.product_repository import ProductRepository
from schemas.product_schema import ProductSchema
from services.base_service_impl import BaseServiceImpl
from services.cache_service import cache_service
from utils.logging_utils import get_sanitized_logger

logger = get_sanitized_logger(__name__)


class ProductService(BaseServiceImpl):
    def __init__(self, db: Session):
        super().__init__(
            repository_class=ProductRepository,
            model=ProductModel,
            schema=ProductSchema,
            db=db
        )
        self.cache = cache_service
        self.cache_prefix = "products"

    def _delete_image_file(self, image_url: str):
        if not image_url:
            return
        try:
            file_path = image_url.lstrip('/')
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Deleted old product image: {file_path}")
        except Exception as e:
            logger.error(f"Failed to delete image {image_url}: {e}")

    def get_all(self, skip: int = 0, limit: int = 100, include_inactive: bool = False) -> List[ProductSchema]:
        cache_key = self.cache.build_key(
            self.cache_prefix,
            "list",
            skip=skip,
            limit=limit,
            inactive=str(include_inactive)
        )

        cached_products = self.cache.get(cache_key)
        if cached_products is not None:
            logger.debug(f"Cache HIT: {cache_key}")
            return [ProductSchema(**p) for p in cached_products]

        logger.debug(f"Cache MISS: {cache_key}")
        
        products = self._repository.find_all(skip, limit, include_inactive)

        products_dict = [p.model_dump() for p in products]
        self.cache.set(cache_key, products_dict)

        return products

    def get_one(self, id_key: int) -> ProductSchema:
        cache_key = self.cache.build_key(self.cache_prefix, "id", id=id_key)

        cached_product = self.cache.get(cache_key)
        if cached_product is not None:
            logger.debug(f"Cache HIT: {cache_key}")
            return ProductSchema(**cached_product)

        logger.debug(f"Cache MISS: {cache_key}")
        product = super().get_one(id_key)

        self.cache.set(cache_key, product.model_dump())

        return product

    def save(self, schema: ProductSchema) -> ProductSchema:
        product = super().save(schema)
        self._invalidate_list_cache()
        return product

    def update(self, id_key: int, schema: ProductSchema) -> ProductSchema:
        cache_key = self.cache.build_key(self.cache_prefix, "id", id=id_key)

        try:
            # ⚠️ CORRECCIÓN AQUÍ: Usamos .find() en lugar de .get_by_id()
            # porque ProductRepository usa 'find' para manejar lazyloads.
            old_product = self._repository.find(id_key)
            old_image = old_product.image_url if old_product else None

            product = super().update(id_key, schema)

            self.cache.delete(cache_key)
            self._invalidate_list_cache()
            self._invalidate_filter_cache()

            if old_image and product.image_url != old_image:
                self._delete_image_file(old_image)

            logger.info(f"Product {id_key} updated successfully")
            return product

        except Exception as e:
            logger.error(f"Failed to update product {id_key}: {e}")
            raise

    def delete(self, id_key: int) -> None:
        logger.info(f"Soft deleting (deactivating) product {id_key}")

        # Soft delete: solo actualizamos active = False
        self._repository.update(id_key, {"active": False})

        cache_key = self.cache.build_key(self.cache_prefix, "id", id=id_key)
        self.cache.delete(cache_key)
        self._invalidate_list_cache()
        self._invalidate_filter_cache()
        
    def filter_products(
        self,
        search: Optional[str] = None,
        category_id: Optional[int] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        in_stock_only: bool = False,
        active: Optional[bool] = True,
        sort_by: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[ProductSchema]:
        cache_key = self.cache.build_key(
            self.cache_prefix,
            "filter",
            search=search or "",
            category_id=category_id or "",
            min_price=min_price or "",
            max_price=max_price or "",
            in_stock_only=str(in_stock_only),
            active=str(active),
            sort_by=sort_by or "",
            skip=skip,
            limit=limit
        )

        cached_products = self.cache.get(cache_key)
        if cached_products is not None:
            logger.debug(f"Cache HIT: {cache_key}")
            return [ProductSchema(**p) for p in cached_products]

        logger.debug(f"Cache MISS: {cache_key}")
        products = self._repository.filter_products(
            search=search,
            category_id=category_id,
            min_price=min_price,
            max_price=max_price,
            in_stock_only=in_stock_only,
            active=active,
            sort_by=sort_by,
            skip=skip,
            limit=limit
        )

        products_dict = [p.model_dump() for p in products]
        self.cache.set(cache_key, products_dict)

        return products

    def _invalidate_list_cache(self):
        pattern = f"{self.cache_prefix}:list:*"
        self.cache.delete_pattern(pattern)

    def _invalidate_filter_cache(self):
        pattern = f"{self.cache_prefix}:filter:*"
        self.cache.delete_pattern(pattern)
            
    def get_by_id(self, id_key: int):
        return self.get_one(id_key)