"""
Schemas de datos para la API (DTOs con Pydantic).
"""

from app.schemas.detection import DetectionRequest, DetectionResponse, BoundingBox
from app.schemas.health import HealthResponse


__all__ = [
    "DetectionRequest",
    "DetectionResponse",
    "BoundingBox",
    "HealthResponse",
]
