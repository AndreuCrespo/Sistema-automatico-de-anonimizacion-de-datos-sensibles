"""
Endpoint de health check.
"""

from fastapi import APIRouter
from app.schemas.health import HealthResponse
from app.core.config import settings
from app.models import get_face_detector, get_plate_detector
import logging


logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Verifica el estado del servicio y de los modelos.

    Returns:
        HealthResponse con el estado del sistema
    """
    try:
        # Intentar cargar detectores
        face_detector = get_face_detector()
        plate_detector = get_plate_detector()

        # Verificar que los modelos esten cargados
        face_model_loaded = face_detector.model is not None
        plate_model_loaded = plate_detector.model is not None

        models_status = {
            "face_detector": {
                "loaded": face_model_loaded,
                "path": str(settings.FACE_MODEL_PATH),
                "info": face_detector.get_model_info() if face_model_loaded else None
            },
            "plate_detector": {
                "loaded": plate_model_loaded,
                "path": str(settings.PLATE_MODEL_PATH),
                "info": plate_detector.get_model_info() if plate_model_loaded else None
            }
        }

        status = "healthy" if (face_model_loaded and plate_model_loaded) else "degraded"

        return HealthResponse(
            status=status,
            version=settings.APP_VERSION,
            models=models_status
        )

    except Exception as e:
        logger.error(f"Error en health check: {e}")
        return HealthResponse(
            status="unhealthy",
            version=settings.APP_VERSION,
            models={"error": str(e)}
        )
