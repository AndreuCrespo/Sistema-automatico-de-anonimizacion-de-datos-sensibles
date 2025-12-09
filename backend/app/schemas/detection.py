"""
Schemas para deteccion de rostros y matriculas.
"""

from pydantic import BaseModel, Field
from typing import List, Literal


class BoundingBox(BaseModel):
    """
    Representa una bounding box de deteccion.

    Attributes:
        x1: Coordenada x superior izquierda
        y1: Coordenada y superior izquierda
        x2: Coordenada x inferior derecha
        y2: Coordenada y inferior derecha
        confidence: Confianza de la deteccion (0-1)
        class_name: Nombre de la clase ('face' o 'plate')
    """
    x1: int = Field(..., description="Coordenada x superior izquierda")
    y1: int = Field(..., description="Coordenada y superior izquierda")
    x2: int = Field(..., description="Coordenada x inferior derecha")
    y2: int = Field(..., description="Coordenada y inferior derecha")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confianza de deteccion")
    class_name: str = Field(..., description="Clase detectada")


class DetectionRequest(BaseModel):
    """
    Request para deteccion.

    Attributes:
        detect_faces: Si se deben detectar rostros
        detect_plates: Si se deben detectar matriculas
        confidence_threshold: Umbral de confianza minima (opcional)
    """
    detect_faces: bool = Field(True, description="Detectar rostros")
    detect_plates: bool = Field(True, description="Detectar matriculas")
    confidence_threshold: float = Field(
        0.5,
        ge=0.0,
        le=1.0,
        description="Umbral de confianza minima"
    )


class DetectionResponse(BaseModel):
    """
    Response de deteccion.

    Attributes:
        faces: Lista de bounding boxes de rostros detectados
        plates: Lista de bounding boxes de matriculas detectadas
        total_detections: Numero total de detecciones
        processing_time_ms: Tiempo de procesamiento en milisegundos
    """
    faces: List[BoundingBox] = Field(default_factory=list)
    plates: List[BoundingBox] = Field(default_factory=list)
    total_detections: int = Field(..., description="Numero total de detecciones")
    processing_time_ms: float = Field(..., description="Tiempo de procesamiento en ms")
