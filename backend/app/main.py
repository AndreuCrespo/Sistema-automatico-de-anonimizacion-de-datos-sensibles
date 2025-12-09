"""
Aplicacion principal de FastAPI.

Sistema automatico de anonimizacion de rostros y matriculas en imagenes.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging_config import get_logger
from app.api.endpoints import health, detect, anonymize, video, classes, text


logger = get_logger(__name__)


# Crear aplicacion FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)


# Configurar CORS (para permitir peticiones desde el frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=[
        "X-Faces-Detected",
        "X-Plates-Detected", 
        "X-Total-Detections",
        "X-Processing-Time-Ms",
        "X-Anonymization-Method",
        "X-Total-Faces",
        "X-Total-Plates",
        "X-Processing-Time",
        "X-Frames-Processed",
        "X-Frames-With-Detections",
        "Content-Disposition"
    ],
)


# Registrar routers
app.include_router(health.router, prefix="/api")
app.include_router(detect.router, prefix="/api")
app.include_router(anonymize.router, prefix="/api")
app.include_router(video.router, prefix="/api")
app.include_router(classes.router, prefix="/api")
app.include_router(text.router, prefix="/api")


@app.on_event("startup")
async def startup_event():
    """Evento de inicio de la aplicacion."""
    logger.info("=" * 60)
    logger.info(f"{settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info("=" * 60)
    logger.info(f"Servidor iniciando en http://{settings.HOST}:{settings.PORT}")
    logger.info(f"Documentacion en http://{settings.HOST}:{settings.PORT}/docs")
    logger.info("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """Evento de cierre de la aplicacion."""
    logger.info("Servidor detenido")


@app.get("/", tags=["Root"])
async def root():
    """Endpoint raiz."""
    return {
        "message": f"Bienvenido a {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/api/health"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
