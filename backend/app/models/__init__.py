"""
Modelos de deteccion para rostros y matriculas.
"""

from app.models.face_detector import FaceDetector, get_face_detector
from app.models.plate_detector import PlateDetector, get_plate_detector


__all__ = [
    "FaceDetector",
    "PlateDetector",
    "get_face_detector",
    "get_plate_detector",
]
