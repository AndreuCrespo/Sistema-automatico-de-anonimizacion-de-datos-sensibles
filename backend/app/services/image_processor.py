"""
Servicio de procesamiento de imagenes.

Integra deteccion y anonimizacion en un pipeline completo.
"""

import cv2
import numpy as np
from typing import List, Tuple, Literal, Optional
import logging
import time

from app.models import get_face_detector, get_plate_detector
from app.models.unified_detector import get_unified_detector
from app.services.anonymizer import anonymizer, AnonymizationMethod


logger = logging.getLogger(__name__)


class ImageProcessor:
    """
    Procesador de imagenes que combina deteccion y anonimizacion.

    Este servicio coordina todo el pipeline:
    1. Detectar rostros/matriculas (con modelo unificado si esta disponible)
    2. Aplicar anonimizacion
    3. Devolver imagen procesada y metadatos
    """

    def __init__(self, use_unified: bool = True):
        """
        Inicializa el procesador de imagenes.

        Args:
            use_unified: Si True, intenta usar detector unificado primero
        """
        self.use_unified = use_unified

        # Intentar cargar detector unificado
        if use_unified:
            try:
                self.unified_detector = get_unified_detector()
                logger.info("Usando detector unificado")
            except Exception as e:
                logger.warning(f"No se pudo cargar detector unificado: {e}")
                self.unified_detector = None
                self.face_detector = get_face_detector()
                self.plate_detector = get_plate_detector()
        else:
            self.unified_detector = None
            self.face_detector = get_face_detector()
            self.plate_detector = get_plate_detector()

    def process_image(
        self,
        image: np.ndarray,
        detect_faces: bool = True,
        detect_plates: bool = True,
        anonymization_method: AnonymizationMethod = "blur",
        confidence_threshold: float = 0.5,
        blur_kernel_size: int = 99,
        pixelate_blocks: int = 10,
        mask_color: Tuple[int, int, int] = (0, 0, 0)
    ) -> Tuple[np.ndarray, dict]:
        """
        Procesa una imagen: detecta y anonimiza.

        Args:
            image: Imagen original (BGR)
            detect_faces: Si detectar rostros
            detect_plates: Si detectar matriculas
            anonymization_method: Metodo de anonimizacion
            confidence_threshold: Umbral de confianza para detecciones
            blur_kernel_size: Tamano del kernel para blur
            pixelate_blocks: Numero de bloques para pixelacion
            mask_color: Color para masking en formato BGR

        Returns:
            Tupla (imagen_anonimizada, metadatos)
        """
        start_time = time.time()

        # Copiar imagen original
        result = image.copy()

        # Listas para almacenar detecciones
        face_boxes = []
        plate_boxes = []

        # Usar detector unificado si está disponible
        if self.unified_detector is not None:
            self.unified_detector.confidence = confidence_threshold
            detections = self.unified_detector.detect(
                image,
                detect_faces=detect_faces,
                detect_plates=detect_plates
            )

            # Convertir a formato (x1, y1, x2, y2)
            face_boxes = [(x1, y1, x2, y2) for x1, y1, x2, y2, _ in detections['faces']]
            plate_boxes = [(x1, y1, x2, y2) for x1, y1, x2, y2, _ in detections['plates']]

            logger.info(f"Detector unificado: {len(face_boxes)} rostros, {len(plate_boxes)} matriculas")

        else:
            # Usar detectores separados como fallback
            if detect_faces:
                self.face_detector.confidence = confidence_threshold
                face_detections = self.face_detector.detect(image)
                face_boxes = [(x1, y1, x2, y2) for x1, y1, x2, y2, _ in face_detections]
                logger.info(f"Detectados {len(face_boxes)} rostros")

            if detect_plates:
                self.plate_detector.confidence = confidence_threshold
                plate_detections = self.plate_detector.detect(image)
                plate_boxes = [(x1, y1, x2, y2) for x1, y1, x2, y2, _ in plate_detections]
                logger.info(f"Detectadas {len(plate_boxes)} matriculas")

        # Combinar todas las bounding boxes
        all_boxes = face_boxes + plate_boxes

        # Aplicar anonimizacion
        if all_boxes:
            if anonymization_method == "blur":
                result = anonymizer.blur(result, all_boxes, kernel_size=blur_kernel_size)
            elif anonymization_method == "pixelate":
                result = anonymizer.pixelate(result, all_boxes, blocks=pixelate_blocks)
            elif anonymization_method == "mask":
                result = anonymizer.mask(result, all_boxes, color=mask_color)
            else:
                raise ValueError(f"Metodo de anonimizacion invalido: {anonymization_method}")

            logger.info(f"Anonimizacion aplicada: {anonymization_method}")
        else:
            logger.warning("No se detectaron objetos para anonimizar")

        # Calcular tiempo de procesamiento
        processing_time = (time.time() - start_time) * 1000  # ms

        # Metadatos
        metadata = {
            "faces_detected": len(face_boxes),
            "plates_detected": len(plate_boxes),
            "total_detections": len(all_boxes),
            "anonymization_method": anonymization_method,
            "processing_time_ms": processing_time,
            "image_size": {
                "width": image.shape[1],
                "height": image.shape[0]
            }
        }

        return result, metadata

    def process_image_bytes(
        self,
        image_bytes: bytes,
        **kwargs
    ) -> Tuple[np.ndarray, dict]:
        """
        Procesa una imagen desde bytes.

        Args:
            image_bytes: Imagen en bytes
            **kwargs: Parametros adicionales para process_image

        Returns:
            Tupla (imagen_anonimizada, metadatos)

        Raises:
            ValueError: Si no se puede decodificar la imagen
        """
        # Decodificar imagen
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if image is None:
            raise ValueError("No se pudo decodificar la imagen")

        return self.process_image(image, **kwargs)


# Instancia global del procesador
_image_processor_instance: Optional[ImageProcessor] = None


def get_image_processor() -> ImageProcessor:
    """
    Obtiene la instancia global del procesador de imagenes.

    Returns:
        Instancia de ImageProcessor (singleton)
    """
    global _image_processor_instance

    if _image_processor_instance is None:
        _image_processor_instance = ImageProcessor()

    return _image_processor_instance
