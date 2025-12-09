"""
Endpoint de anonimizacion de imagenes.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import StreamingResponse
from app.services.image_processor import get_image_processor
import cv2
import numpy as np
import io
import logging
from typing import Literal


logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/anonymize", tags=["Anonymization"])
async def anonymize_image(
    file: UploadFile = File(..., description="Imagen a anonimizar"),
    detect_faces: bool = Form(True, description="Detectar rostros"),
    detect_plates: bool = Form(True, description="Detectar matriculas"),
    method: Literal["blur", "pixelate", "mask"] = Form("blur", description="Metodo de anonimizacion"),
    confidence_threshold: float = Form(0.25, ge=0.0, le=1.0, description="Umbral de confianza"),
    blur_kernel_size: int = Form(99, description="Tamano del kernel para blur"),
    pixelate_blocks: int = Form(10, description="Numero de bloques para pixelacion")
):
    """
    Anonimiza rostros y/o matriculas en una imagen.

    Args:
        file: Archivo de imagen
        detect_faces: Si detectar rostros
        detect_plates: Si detectar matriculas
        method: Metodo de anonimizacion ('blur', 'pixelate', 'mask')
        confidence_threshold: Umbral de confianza para detecciones
        blur_kernel_size: Tamano del kernel para Gaussian Blur
        pixelate_blocks: Numero de bloques para pixelacion

    Returns:
        Imagen anonimizada (formato original)

    Raises:
        HTTPException: Si hay error procesando la imagen
    """
    try:
        # Leer imagen
        contents = await file.read()

        # Obtener procesador
        processor = get_image_processor()

        # Procesar imagen
        result_image, metadata = processor.process_image_bytes(
            contents,
            detect_faces=detect_faces,
            detect_plates=detect_plates,
            anonymization_method=method,
            confidence_threshold=confidence_threshold,
            blur_kernel_size=blur_kernel_size,
            pixelate_blocks=pixelate_blocks
        )

        logger.info(f"Imagen procesada: {metadata}")

        # Codificar imagen de vuelta a bytes
        # Intentar mantener el formato original
        ext = file.filename.split('.')[-1].lower() if '.' in file.filename else 'jpg'

        if ext in ['jpg', 'jpeg']:
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 95]
            success, encoded_image = cv2.imencode('.jpg', result_image, encode_param)
            media_type = 'image/jpeg'
        elif ext == 'png':
            encode_param = [int(cv2.IMWRITE_PNG_COMPRESSION), 3]
            success, encoded_image = cv2.imencode('.png', result_image, encode_param)
            media_type = 'image/png'
        else:
            # Por defecto, usar JPEG
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 95]
            success, encoded_image = cv2.imencode('.jpg', result_image, encode_param)
            media_type = 'image/jpeg'

        if not success:
            raise HTTPException(
                status_code=500,
                detail="Error al codificar la imagen anonimizada"
            )

        # Convertir a bytes
        image_bytes = encoded_image.tobytes()

        # Crear nombre de archivo de salida
        output_filename = f"anonymized_{file.filename}"

        # Headers con metadatos
        headers = {
            'Content-Disposition': f'attachment; filename="{output_filename}"',
            'X-Faces-Detected': str(metadata['faces_detected']),
            'X-Plates-Detected': str(metadata['plates_detected']),
            'X-Total-Detections': str(metadata['total_detections']),
            'X-Processing-Time-Ms': str(metadata['processing_time_ms']),
            'X-Anonymization-Method': metadata['anonymization_method']
        }

        # Devolver imagen como stream
        return StreamingResponse(
            io.BytesIO(image_bytes),
            media_type=media_type,
            headers=headers
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en anonimizacion: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error procesando imagen: {str(e)}"
        )
