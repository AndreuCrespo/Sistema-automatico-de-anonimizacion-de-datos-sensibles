"""
Schemas para anonimizacion de imagenes.
"""

from pydantic import BaseModel, Field
from typing import Literal


class AnonymizationRequest(BaseModel):
    """
    Request para anonimizacion.

    Attributes:
        detect_faces: Si detectar rostros
        detect_plates: Si detectar matriculas
        method: Metodo de anonimizacion
        confidence_threshold: Umbral de confianza
        blur_kernel_size: Tamano del kernel para blur
        pixelate_blocks: Numero de bloques para pixelacion
    """
    detect_faces: bool = Field(True, description="Detectar rostros")
    detect_plates: bool = Field(True, description="Detectar matriculas")
    method: Literal["blur", "pixelate", "mask"] = Field("blur", description="Metodo de anonimizacion")
    confidence_threshold: float = Field(0.5, ge=0.0, le=1.0, description="Umbral de confianza")
    blur_kernel_size: int = Field(99, ge=3, description="Tamano del kernel para blur (impar)")
    pixelate_blocks: int = Field(10, ge=2, le=50, description="Numero de bloques para pixelacion")


class AnonymizationResponse(BaseModel):
    """
    Response de anonimizacion.

    Attributes:
        faces_detected: Numero de rostros detectados
        plates_detected: Numero de matriculas detectadas
        total_detections: Numero total de detecciones
        anonymization_method: Metodo de anonimizacion aplicado
        processing_time_ms: Tiempo de procesamiento en ms
        image_size: Dimensiones de la imagen
    """
    faces_detected: int
    plates_detected: int
    total_detections: int
    anonymization_method: str
    processing_time_ms: float
    image_size: dict
