"""
app/main.py
============
FastAPI application entry point.

Responsibilities:
    - Initialize the FastAPI application
    - Register lifespan events (startup: load model / shutdown: cleanup)
    - Register CORS middleware
    - Register global exception handlers
    - Mount the v1 API router
"""
import logging
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.router import router as api_router
from app.config import settings
from app.core.vision.loader import ModelLoader
from app.core.vision.predictor import DiseasePredictor
from app.utils.exceptions import ImageValidationError, ModelLoadError, PredictionError

# ------------------------------------------------------------------ Logging
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


# ------------------------------------------------------------------ Lifespan
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application startup and shutdown events.

    Startup:
        - Load model artifacts (weights, labels, metadata)
        - Initialize DiseasePredictor (singleton for all requests)
        - Record startup time for uptime calculation

    Shutdown:
        - Release resources (placeholder for future cleanup)
    """
    logger.info("Starting up %s v%s ...", settings.app_name, settings.app_version)
    startup_start = time.perf_counter()

    # Load model artifacts
    loader = ModelLoader(
        model_path=settings.model_path,
        labels_path=settings.labels_path,
        metadata_path=settings.metadata_path,
    )
    artifacts = loader.load()
    predictor = DiseasePredictor(artifacts)

    # Initialize database tables (Phase 2)
    from app.db.base import Base
    from app.db.session import engine
    from app.models.history import DetectionHistory  # Register models without shadowing app parameter
    from app.models.setting import AppSetting
    import os

    # Ensure database directory exists for SQLite
    if settings.database_url.startswith("sqlite"):
        try:
            # Parse path out of e.g. sqlite+aiosqlite:///./db_data/rice_disease.db
            db_path = settings.database_url.split(":///")[1]
            db_dir = os.path.dirname(db_path)
            if db_dir:
                os.makedirs(db_dir, exist_ok=True)
        except Exception as exc:
            logger.error("Failed to pre-create SQLite database directory: %s", str(exc))

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Initialize LLM engine and explainer (Phase 2)
    from app.core.llm.engine import LLMEngine
    from app.core.llm.cot import ChainOfThoughtExplainer
    
    llm_engine = LLMEngine(
        api_key=settings.openai_api_key,
        model=settings.openai_model,
    )
    explainer = ChainOfThoughtExplainer(llm_engine)

    # Store shared state accessible from all request handlers
    app.state.artifacts = artifacts
    app.state.predictor = predictor
    app.state.settings = settings
    app.state.startup_time = datetime.now(timezone.utc)
    app.state.explainer = explainer

    elapsed = (time.perf_counter() - startup_start) * 1000
    logger.info(
        "Application startup complete | %.1f ms | classes=%d | device=%s",
        elapsed,
        artifacts.num_classes,
        artifacts.device,
    )

    yield  # Application is now running

    # Shutdown
    logger.info("Shutting down %s ...", settings.app_name)


# ------------------------------------------------------------------ App Init
def create_application() -> FastAPI:
    """Factory function for the FastAPI application instance.

    Returns:
        Configured FastAPI application.
    """
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "REST API for early detection of rice diseases using MobileNetV2. "
            "Designed for researchers, academics, and agri-tech developers."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # ---- CORS Middleware ------------------------------------------------
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ---- Global Exception Handlers -------------------------------------
    @app.exception_handler(ImageValidationError)
    async def image_validation_handler(
        request: Request, exc: ImageValidationError
    ) -> JSONResponse:
        return JSONResponse(status_code=422, content={"detail": exc.message})

    @app.exception_handler(ModelLoadError)
    async def model_load_handler(
        request: Request, exc: ModelLoadError
    ) -> JSONResponse:
        logger.critical("ModelLoadError: %s", exc.message)
        return JSONResponse(status_code=503, content={"detail": exc.message})

    @app.exception_handler(PredictionError)
    async def prediction_error_handler(
        request: Request, exc: PredictionError
    ) -> JSONResponse:
        logger.error("PredictionError: %s", exc.message)
        return JSONResponse(
            status_code=500,
            content={"detail": "Prediction failed. Please try again."},
        )

    # ---- API Router ----------------------------------------------------
    app.include_router(api_router, prefix="/api/v1")

    # ---- Static Files Mounting -----------------------------------------
    from fastapi.staticfiles import StaticFiles
    import os
    os.makedirs("uploads", exist_ok=True)
    app.mount("/static/uploads", StaticFiles(directory="uploads"), name="static")

    return app


app = create_application()
