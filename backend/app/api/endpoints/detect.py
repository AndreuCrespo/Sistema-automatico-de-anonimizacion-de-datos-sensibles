"""
Endpoint de deteccion de rostros y matriculas.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from app.schemas.detection import DetectionResponse, BoundingBox
from app.models import get_face_detector, get_plate_detector
import cv2
import numpy as np
import time
import logging
from typing import Optional


logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/detect", response_model=DetectionResponse, tags=["Detection"])
async def detect_objects(
    file: UploadFile = File(..., description="Imagen a procesar"),
    detect_faces: bool = Form(True, description="Detectar rostros"),
    detect_plates: bool = Form(True, description="Detectar matriculas"),
    confidence_threshold: float = Form(0.25, ge=0.0, le=1.0, description="Umbral de confianza")
):
    """
    Detecta rostros y/o matriculas en una imagen.

    Args:
        file: Archivo de imagen (JPG, PNG, BMP)
        detect_faces: Si se deben detectar rostros
        detect_plates: Si se deben detectar matriculas
        confidence_threshold: Umbral minimo de confianza para detecciones

    Returns:
        DetectionResponse con las detecciones encontradas

    Raises:
        HTTPException: Si hay error procesando la imagen
    """
    start_time = time.time()

    try:
        # Leer imagen
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if image is None:
            raise HTTPException(
                status_code=400,
                detail="No se pudo decodificar la imagen. Formato invalido."
            )

        logger.info(f"Imagen recibida: {image.shape}")

        faces = []
        plates = []

        # Detectar rostros
        if detect_faces:
            face_detector = get_face_detector()
            face_detector.confidence = confidence_threshold

            face_detections = face_detector.detect(image)

            for x1, y1, x2, y2, conf in face_detections:
                faces.append(BoundingBox(
                    x1=x1,
                    y1=y1,
                    x2=x2,
                    y2=y2,
                    confidence=conf,
                    class_name="face"
                ))

            logger.info(f"Detectados {len(faces)} rostros")

        # Detectar matriculas
        if detect_plates:
            plate_detector = get_plate_detector()
            plate_detector.confidence = confidence_threshold

            plate_detections = plate_detector.detect(image)

            for x1, y1, x2, y2, conf in plate_detections:
                plates.append(BoundingBox(
                    x1=x1,
                    y1=y1,
                    x2=x2,
                    y2=y2,
                    confidence=conf,
                    class_name="plate"
                ))

            logger.info(f"Detectadas {len(plates)} matriculas")

        # Calcular tiempo de procesamiento
        processing_time = (time.time() - start_time) * 1000  # ms

        return DetectionResponse(
            faces=faces,
            plates=plates,
            total_detections=len(faces) + len(plates),
            processing_time_ms=processing_time
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en deteccion: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error procesando imagen: {str(e)}"
        )
