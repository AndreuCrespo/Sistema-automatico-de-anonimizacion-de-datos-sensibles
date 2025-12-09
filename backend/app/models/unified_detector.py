"""
Detector unificado de rostros y matriculas usando un solo modelo YOLOv8.

Este modulo carga el modelo unificado que detecta ambas clases:
- Clase 0: face (rostros)
- Clase 1: plate (matriculas)
"""

import numpy as np
from pathlib import Path
from typing import List, Tuple, Optional, Union, Dict
from ultralytics import YOLO
import logging

from app.core.config import settings


logger = logging.getLogger(__name__)


class UnifiedDetector:
    """
    Detector unificado de rostros y matriculas usando YOLOv8.

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
        Inicializa el detector unificado.

        Args:
            model_path: Ruta al modelo entrenado (.pt). Si None, usa el de config
            confidence: Umbral de confianza minima (0-1)
            iou: Umbral de IoU para NMS (0-1)
        """
        # Ruta al modelo unificado
        if model_path is None:
            unified_model = settings.MODELS_DIR / 'unified_detector.pt'
            if unified_model.exists():
                model_path = unified_model
            else:
                # Si no existe el modelo unificado, usar YOLOv8n base
                logger.warning("Modelo unificado no encontrado. Usando YOLOv8n base.")
                model_path = None

        self.model_path = model_path
        self.confidence = confidence
        self.iou = iou
        self.model = None

        self._load_model()

    def _load_model(self) -> None:
        """Carga el modelo YOLOv8 entrenado."""
        try:
            if self.model_path is None or not self.model_path.exists():
                logger.warning(
                    "Modelo unificado no encontrado. Usando modelo pre-entrenado base."
                )
                self.model = YOLO('yolov8n.pt')
            else:
                logger.info(f"Cargando modelo unificado desde {self.model_path}")
                self.model = YOLO(str(self.model_path))

            logger.info("Modelo unificado cargado correctamente")

        except Exception as e:
            logger.error(f"Error al cargar modelo unificado: {e}")
            raise

    def detect(
        self,
        image: Union[str, Path, np.ndarray],
        detect_faces: bool = True,
        detect_plates: bool = True
    ) -> Dict[str, List[Tuple[int, int, int, int, float]]]:
        """
        Detecta rostros y/o matriculas en una imagen.

        Args:
            image: Ruta a la imagen o array numpy (BGR)
            detect_faces: Si se deben detectar rostros
            detect_plates: Si se deben detectar matriculas

        Returns:
            Diccionario con keys 'faces' y 'plates', cada uno con lista de
            tuplas (x1, y1, x2, y2, confidence)

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
            faces = []
            plates = []

            if len(results) > 0:
                boxes = results[0].boxes

                for box in boxes:
                    # Obtener coordenadas, confianza y clase
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    conf = float(box.conf[0].cpu().numpy())
                    cls = int(box.cls[0].cpu().numpy())

                    detection = (
                        int(x1),
                        int(y1),
                        int(x2),
                        int(y2),
                        conf
                    )

                    # Clase 0: face, Clase 1: plate
                    if cls == 0 and detect_faces:
                        faces.append(detection)
                    elif cls == 1 and detect_plates:
                        plates.append(detection)

            logger.info(f"Detectados {len(faces)} rostros y {len(plates)} matriculas")

            return {
                'faces': faces,
                'plates': plates
            }

        except Exception as e:
            logger.error(f"Error en deteccion unificada: {e}")
            raise ValueError(f"Error procesando imagen: {e}")

    def detect_batch(
        self,
        images: List[Union[str, Path, np.ndarray]],
        detect_faces: bool = True,
        detect_plates: bool = True
    ) -> List[Dict[str, List[Tuple[int, int, int, int, float]]]]:
        """
        Detecta rostros y matriculas en multiples imagenes.

        Args:
            images: Lista de rutas a imagenes o arrays numpy
            detect_faces: Si se deben detectar rostros
            detect_plates: Si se deben detectar matriculas

        Returns:
            Lista de diccionarios con detecciones, uno por imagen
        """
        results = []

        for image in images:
            detections = self.detect(image, detect_faces, detect_plates)
            results.append(detections)

        return results

    def get_model_info(self) -> dict:
        """
        Obtiene informacion sobre el modelo cargado.

        Returns:
            Diccionario con informacion del modelo
        """
        return {
            "model_path": str(self.model_path) if self.model_path else "YOLOv8n base",
            "model_type": "YOLOv8 Unified",
            "task": "unified_detection",
            "confidence_threshold": self.confidence,
            "iou_threshold": self.iou,
            "classes": {
                0: "face",
                1: "plate"
            }
        }


# Instancia global del detector (singleton pattern)
_unified_detector_instance: Optional[UnifiedDetector] = None


def get_unified_detector() -> UnifiedDetector:
    """
    Obtiene la instancia global del detector unificado.

    Returns:
        Instancia de UnifiedDetector (singleton)
    """
    global _unified_detector_instance

    if _unified_detector_instance is None:
        _unified_detector_instance = UnifiedDetector(
            confidence=settings.DETECTION_CONFIDENCE,
            iou=settings.DETECTION_IOU
        )

    return _unified_detector_instance
