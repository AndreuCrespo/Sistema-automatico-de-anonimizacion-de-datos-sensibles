"""
Detector multi-modelo que combina:
1. Modelo unificado entrenado (faces + plates) - Alta precision
2. YOLOv8n base (COCO 80 clases) - Deteccion general

Permite seleccionar dinamicamente que clases detectar.
"""

import numpy as np
from pathlib import Path
from typing import List, Tuple, Optional, Union, Dict, Set
from ultralytics import YOLO
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


# Clases COCO organizadas por categorías
COCO_CLASSES = {
    # Personas
    'person': 0,

    # Vehículos
    'bicycle': 1,
    'car': 2,
    'motorcycle': 3,
    'airplane': 4,
    'bus': 5,
    'train': 6,
    'truck': 7,
    'boat': 8,

    # Señales y urbano
    'traffic light': 9,
    'fire hydrant': 10,
    'stop sign': 11,
    'parking meter': 12,

    # Mobiliario
    'bench': 13,

    # Animales
    'bird': 14,
    'cat': 15,
    'dog': 16,
    'horse': 17,
    'sheep': 18,
    'cow': 19,
    'elephant': 20,
    'bear': 21,
    'zebra': 22,
    'giraffe': 23,

    # Objetos personales
    'backpack': 24,
    'umbrella': 25,
    'handbag': 26,
    'tie': 27,
    'suitcase': 28,

    # Deportes
    'frisbee': 29,
    'skis': 30,
    'snowboard': 31,
    'sports ball': 32,
    'kite': 33,
    'baseball bat': 34,
    'baseball glove': 35,
    'skateboard': 36,
    'surfboard': 37,
    'tennis racket': 38,

    # Cocina/Comida
    'bottle': 39,
    'wine glass': 40,
    'cup': 41,
    'fork': 42,
    'knife': 43,
    'spoon': 44,
    'bowl': 45,
    'banana': 46,
    'apple': 47,
    'sandwich': 48,
    'orange': 49,
    'broccoli': 50,
    'carrot': 51,
    'hot dog': 52,
    'pizza': 53,
    'donut': 54,
    'cake': 55,

    # Muebles
    'chair': 56,
    'couch': 57,
    'potted plant': 58,
    'bed': 59,
    'dining table': 60,
    'toilet': 61,

    # Electrónica
    'tv': 62,
    'laptop': 63,
    'mouse': 64,
    'remote': 65,
    'keyboard': 66,
    'cell phone': 67,

    # Electrodomésticos
    'microwave': 68,
    'oven': 69,
    'toaster': 70,
    'sink': 71,
    'refrigerator': 72,

    # Otros
    'book': 73,
    'clock': 74,
    'vase': 75,
    'scissors': 76,
    'teddy bear': 77,
    'hair drier': 78,
    'toothbrush': 79
}

# Categorías para organizar en UI
COCO_CATEGORIES = {
    'sensitive': {
        'name': 'Datos Sensibles',
        'icon': '🎭',
        'classes': ['face', 'plate'],  # Estas vienen del modelo unificado
        'model': 'unified'
    },
    'vehicles': {
        'name': 'Vehículos',
        'icon': '🚗',
        'classes': ['car', 'motorcycle', 'bus', 'truck', 'bicycle', 'boat', 'airplane', 'train'],
        'model': 'coco'
    },
    'people': {
        'name': 'Personas',
        'icon': '👥',
        'classes': ['person'],
        'model': 'coco'
    },
    'electronics': {
        'name': 'Electrónica',
        'icon': '📱',
        'classes': ['cell phone', 'laptop', 'tv', 'keyboard', 'mouse'],
        'model': 'coco'
    },
    'animals': {
        'name': 'Animales',
        'icon': '🐾',
        'classes': ['dog', 'cat', 'bird', 'horse', 'cow', 'sheep'],
        'model': 'coco'
    }
}


class MultiDetector:
    """
    Detector multi-modelo que combina modelo unificado + YOLO base.

    Permite detectar:
    - Rostros y matrículas con alta precisión (modelo entrenado)
    - Cualquier clase COCO adicional (YOLOv8n base)
    """

    def __init__(
        self,
        unified_model_path: Optional[Path] = None,
        confidence: float = 0.5,
        iou: float = 0.45
    ):
        """
        Inicializa el detector multi-modelo.

        Args:
            unified_model_path: Ruta al modelo unificado. Si None, usa configuración
            confidence: Umbral de confianza mínima (0-1)
            iou: Umbral de IoU para NMS (0-1)
        """
        self.confidence = confidence
        self.iou = iou

        # Modelo unificado (faces + plates)
        self.unified_model = None
        if unified_model_path is None:
            unified_model_path = settings.MODELS_DIR / 'unified_detector.pt'

        if unified_model_path and unified_model_path.exists():
            logger.info(f"Cargando modelo unificado: {unified_model_path}")
            self.unified_model = YOLO(str(unified_model_path))
        else:
            logger.warning("Modelo unificado no encontrado")

        # Modelo COCO base (80 clases)
        logger.info("Cargando YOLOv8n base (COCO)")
        self.coco_model = YOLO('yolov8n.pt')

        logger.info("MultiDetector inicializado correctamente")

    def detect(
        self,
        image: Union[str, Path, np.ndarray],
        classes_to_detect: Optional[List[str]] = None
    ) -> Dict[str, List[Tuple[int, int, int, int, float]]]:
        """
        Detecta objetos en una imagen usando los modelos apropiados.

        Args:
            image: Ruta a la imagen o array numpy (BGR)
            classes_to_detect: Lista de clases a detectar. Si None, detecta faces + plates
                              Ejemplos: ['face', 'plate', 'car', 'person']

        Returns:
            Diccionario con detecciones por clase:
            {
                'face': [(x1, y1, x2, y2, conf), ...],
                'plate': [(x1, y1, x2, y2, conf), ...],
                'car': [(x1, y1, x2, y2, conf), ...],
                ...
            }
        """
        if classes_to_detect is None:
            classes_to_detect = ['face', 'plate']

        detections = {cls: [] for cls in classes_to_detect}

        # Separar clases por modelo
        unified_classes = [cls for cls in classes_to_detect if cls in ['face', 'plate']]
        coco_classes = [cls for cls in classes_to_detect if cls in COCO_CLASSES]

        # Detectar con modelo unificado (faces + plates)
        if unified_classes and self.unified_model:
            unified_results = self.unified_model(
                image,
                conf=self.confidence,
                iou=self.iou,
                verbose=False
            )

            if len(unified_results) > 0:
                boxes = unified_results[0].boxes

                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    conf = float(box.conf[0].cpu().numpy())
                    cls_id = int(box.cls[0].cpu().numpy())

                    detection = (int(x1), int(y1), int(x2), int(y2), conf)

                    # Clase 0: face, Clase 1: plate
                    if cls_id == 0 and 'face' in unified_classes:
                        detections['face'].append(detection)
                    elif cls_id == 1 and 'plate' in unified_classes:
                        detections['plate'].append(detection)

        # Detectar con modelo COCO (otras clases)
        if coco_classes:
            # Obtener IDs de clases COCO a detectar
            coco_class_ids = [COCO_CLASSES[cls] for cls in coco_classes]

            coco_results = self.coco_model(
                image,
                conf=self.confidence,
                iou=self.iou,
                classes=coco_class_ids,  # Filtrar solo las clases solicitadas
                verbose=False
            )

            if len(coco_results) > 0:
                boxes = coco_results[0].boxes

                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    conf = float(box.conf[0].cpu().numpy())
                    cls_id = int(box.cls[0].cpu().numpy())

                    detection = (int(x1), int(y1), int(x2), int(y2), conf)

                    # Encontrar nombre de la clase
                    class_name = None
                    for name, coco_id in COCO_CLASSES.items():
                        if coco_id == cls_id:
                            class_name = name
                            break

                    if class_name and class_name in coco_classes:
                        detections[class_name].append(detection)

        # Log de resultados
        total_detections = sum(len(dets) for dets in detections.values())
        logger.info(f"Total detecciones: {total_detections}")
        for cls, dets in detections.items():
            if dets:
                logger.info(f"  - {cls}: {len(dets)}")

        return detections

    def get_available_classes(self) -> Dict[str, any]:
        """
        Obtiene todas las clases disponibles organizadas por categorías.

        Returns:
            Diccionario con categorías y clases disponibles
        """
        return COCO_CATEGORIES

    def get_model_info(self) -> dict:
        """
        Obtiene información sobre los modelos cargados.

        Returns:
            Diccionario con información de modelos
        """
        return {
            "type": "MultiDetector",
            "unified_model": {
                "loaded": self.unified_model is not None,
                "classes": ["face", "plate"],
                "f1_scores": {
                    "face": 0.9049,
                    "plate": 0.8997
                }
            },
            "coco_model": {
                "loaded": True,
                "classes": list(COCO_CLASSES.keys()),
                "total_classes": len(COCO_CLASSES)
            },
            "confidence_threshold": self.confidence,
            "iou_threshold": self.iou
        }


# Instancia global del detector (singleton pattern)
_multi_detector_instance: Optional[MultiDetector] = None


def get_multi_detector() -> MultiDetector:
    """
    Obtiene la instancia global del multi-detector.

    Returns:
        Instancia de MultiDetector (singleton)
    """
    global _multi_detector_instance

    if _multi_detector_instance is None:
        _multi_detector_instance = MultiDetector(
            confidence=settings.DETECTION_CONFIDENCE,
            iou=settings.DETECTION_IOU
        )

    return _multi_detector_instance
