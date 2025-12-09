"""
Detector de matriculas de vehiculos usando YOLOv8.

Este modulo carga el modelo fine-tuned de YOLOv8 para detectar matriculas
en imagenes y devuelve las coordenadas de las bounding boxes.
"""

import numpy as np
from pathlib import Path
from typing import List, Tuple, Optional, Union
from ultralytics import YOLO
import logging

from app.core.config import settings


logger = logging.getLogger(__name__)


class PlateDetector:
    """
    Detector de matriculas usando YOLOv8.

    Attributes:
        model: Modelo YOLOv8 cargado
        confidence: Umbral de confianza minima para detecciones
        iou: Umbral de IoU para Non-Maximum Suppression
    """

    def __init__(
        self,
        model_path: Optional[Path] = None,
        confidence: float = 0.5,
        iou: float = 0.45
    ):
        """
        Inicializa el detector de matriculas.

        Args:
            model_path: Ruta al modelo entrenado (.pt). Si None, usa el de config
            confidence: Umbral de confianza minima (0-1)
            iou: Umbral de IoU para NMS (0-1)
        """
        self.model_path = model_path or settings.PLATE_MODEL_PATH
        self.confidence = confidence
        self.iou = iou
        self.model = None

        self._load_model()

    def _load_model(self) -> None:
        """Carga el modelo YOLOv8 entrenado."""
        try:
            if not self.model_path.exists():
                logger.warning(
                    f"Modelo de matriculas no encontrado en {self.model_path}. "
                    "Usando modelo pre-entrenado base."
                )
                # Si no existe el modelo entrenado, usar YOLOv8n base
                self.model = YOLO('yolov8n.pt')
            else:
                logger.info(f"Cargando modelo de matriculas desde {self.model_path}")
                self.model = YOLO(str(self.model_path))

            logger.info("Modelo de matriculas cargado correctamente")

        except Exception as e:
            logger.error(f"Error al cargar modelo de matriculas: {e}")
            raise

    def detect(
        self,
        image: Union[str, Path, np.ndarray]
    ) -> List[Tuple[int, int, int, int, float]]:
        """
        Detecta matriculas en una imagen.

        Args:
            image: Ruta a la imagen o array numpy (BGR)

        Returns:
            Lista de tuplas (x1, y1, x2, y2, confidence) para cada matricula detectada
            Coordenadas en pixeles absolutos.

        Raises:
            ValueError: Si la imagen no es valida
        """
        try:
            # Realizar inferencia
            results = self.model(
                image,
                conf=self.confidence,
                iou=self.iou,
                verbose=False
            )

            # Extraer bounding boxes
            detections = []

            if len(results) > 0:
                boxes = results[0].boxes

                for box in boxes:
                    # Obtener coordenadas y confianza
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    conf = float(box.conf[0].cpu().numpy())

                    detections.append((
                        int(x1),
                        int(y1),
                        int(x2),
                        int(y2),
                        conf
                    ))

            logger.info(f"Detectadas {len(detections)} matriculas")
            return detections

        except Exception as e:
            logger.error(f"Error en deteccion de matriculas: {e}")
            raise ValueError(f"Error procesando imagen: {e}")

    def detect_batch(
        self,
        images: List[Union[str, Path, np.ndarray]]
    ) -> List[List[Tuple[int, int, int, int, float]]]:
        """
        Detecta matriculas en multiples imagenes.

        Args:
            images: Lista de rutas a imagenes o arrays numpy

        Returns:
            Lista de listas de detecciones, una por imagen
        """
        results = []

        for image in images:
            detections = self.detect(image)
            results.append(detections)

        return results

    def get_model_info(self) -> dict:
        """
        Obtiene informacion sobre el modelo cargado.

        Returns:
            Diccionario con informacion del modelo
        """
        return {
            "model_path": str(self.model_path),
            "model_type": "YOLOv8",
            "task": "plate_detection",
            "confidence_threshold": self.confidence,
            "iou_threshold": self.iou,
            "classes": ["plate"]
        }


# Instancia global del detector (singleton pattern)
_plate_detector_instance: Optional[PlateDetector] = None


def get_plate_detector() -> PlateDetector:
    """
    Obtiene la instancia global del detector de matriculas.

    Returns:
        Instancia de PlateDetector (singleton)
    """
    global _plate_detector_instance

    if _plate_detector_instance is None:
        _plate_detector_instance = PlateDetector(
            confidence=settings.DETECTION_CONFIDENCE,
            iou=settings.DETECTION_IOU
        )

    return _plate_detector_instance
