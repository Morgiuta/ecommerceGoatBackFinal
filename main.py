import logging
import os
import uvicorn

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette import status
from starlette.responses import JSONResponse

# ---- LOGGING ----
from config.logging_config import setup_logging
setup_logging()
logger = logging.getLogger(__name__)

# ---- ALEMBIC ----
from alembic.config import Config
from alembic import command

# ---- CONTROLLERS ----
from controllers.address_controller import AddressController
from controllers.bill_controller import BillController
from controllers.category_controller import CategoryController
from controllers.client_controller import ClientController
from controllers.order_controller import OrderController
from controllers.order_detail_controller import OrderDetailController
from controllers.product_controller import ProductController
from controllers.review_controller import ReviewController
from controllers.health_check import router as health_check_controller
from controllers.cart_controller import CartController

# ---- CONFIG ----
from config.database import create_tables, engine
from config.redis_config import redis_config, check_redis_connection

# ---- MIDDLEWARE ----
from middleware.rate_limiter import RateLimiterMiddleware
from middleware.request_id_middleware import RequestIDMiddleware

# ---- EXCEPTIONS ----
from repositories.base_repository_impl import InstanceNotFoundError

def run_migrations():
    logger.info("📦 Running Alembic migrations...")
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("script_location", "alembic")
    command.upgrade(alembic_cfg, "head")
    logger.info("✅ Alembic migrations completed.")


# ==========================================================
def create_fastapi_app() -> FastAPI:
    fastapi_app = FastAPI(
        title="E-commerce REST API",
        description="FastAPI REST API for e-commerce system with PostgreSQL",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )

    @fastapi_app.exception_handler(InstanceNotFoundError)
    async def instance_not_found_exception_handler(request, exc):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": str(exc)},
        )

    static_dir = "static"
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)
    
    fastapi_app.mount("/static", StaticFiles(directory=static_dir), name="static")

    # ✅ CORREGIDO: Todas las rutas bajo /api/v1 para consistencia
    fastapi_app.include_router(CartController().router, prefix="/api/v1/cart")  
    fastapi_app.include_router(ClientController().router, prefix="/api/v1/clients")
    fastapi_app.include_router(OrderController().router, prefix="/api/v1/orders")
    fastapi_app.include_router(ProductController().router, prefix="/api/v1/products")
    fastapi_app.include_router(AddressController().router, prefix="/api/v1/addresses")
    fastapi_app.include_router(BillController().router, prefix="/api/v1/bills")
    fastapi_app.include_router(OrderDetailController().router, prefix="/api/v1/order_details")
    fastapi_app.include_router(ReviewController().router, prefix="/api/v1/reviews")
    fastapi_app.include_router(CategoryController().router, prefix="/api/v1/categories")
    
    fastapi_app.include_router(health_check_controller, prefix="/health_check")
    
    # Debug router (si existe en tu proyecto)
    try:
        from debug_router import router as debug_router
        fastapi_app.include_router(debug_router)
    except ImportError:
        pass

    fastapi_app.add_middleware(     
        CORSMiddleware,
        allow_origins=["https://frontecommercefinal.vercel.app"],  
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    logger.info("✅ CORS enabled")

    fastapi_app.add_middleware(RequestIDMiddleware)
    logger.info("✅ Request ID middleware enabled")

    fastapi_app.add_middleware(RateLimiterMiddleware, calls=100, period=60)
    logger.info("✅ Rate limiting middleware enabled")

    @fastapi_app.on_event("startup")
    async def startup_event():
        logger.info("🚀 Starting FastAPI E-commerce API...")

        create_tables()
        if check_redis_connection():
            logger.info("✅ Redis cache available")
        else:
            logger.warning("⚠️ Redis NOT available")

    @fastapi_app.on_event("shutdown")
    async def shutdown_event():
        logger.info("👋 Shutting down API...")

        try:
            redis_config.close()
        except Exception as e:
            logger.error(f"❌ Error closing Redis: {e}")

        try:
            engine.dispose()
        except Exception as e:
            logger.error(f"❌ Error disposing DB engine: {e}")

        logger.info("✅ Shutdown complete")

    return fastapi_app

# ==========================================================
def run_app(fastapi_app: FastAPI):
    uvicorn.run(fastapi_app, host="0.0.0.0", port=8000)


app = create_fastapi_app()

if __name__ == "__main__":
    run_app(app)