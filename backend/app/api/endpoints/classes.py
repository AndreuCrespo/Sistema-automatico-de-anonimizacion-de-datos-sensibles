"""
Classes Endpoints
Endpoints para obtener información sobre clases disponibles para detección
"""

from fastapi import APIRouter
from typing import Dict, List
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# Clases RGPD filtradas con metadata
RGPD_CLASSES = {
    "Personas": [
        {
            "id": "face",
            "name": "Face",
            "description": "Rostros de personas",
            "source": "trained",
            "priority": "high",
            "f1_score": 90.49
        },
        {
            "id": "person",
            "name": "Person",
            "description": "Personas completas (siluetas)",
            "source": "coco",
            "priority": "medium",
            "coco_id": 0
        }
    ],
    "Vehículos": [
        {
            "id": "plate",
            "name": "License Plate",
            "description": "Matrículas de vehículos",
            "source": "trained",
            "priority": "high",
            "f1_score": 89.97
        },
        {
            "id": "car",
            "name": "Car",
            "description": "Automóviles",
            "source": "coco",
            "priority": "medium",
            "coco_id": 2
        },
        {
            "id": "motorcycle",
            "name": "Motorcycle",
            "description": "Motocicletas",
            "source": "coco",
            "priority": "medium",
            "coco_id": 3
        },
        {
            "id": "bus",
            "name": "Bus",
            "description": "Autobuses",
            "source": "coco",
            "priority": "medium",
            "coco_id": 5
        },
        {
            "id": "truck",
            "name": "Truck",
            "description": "Camiones",
            "source": "coco",
            "priority": "medium",
            "coco_id": 7
        },
        {
            "id": "bicycle",
            "name": "Bicycle",
            "description": "Bicicletas",
            "source": "coco",
            "priority": "low",
            "coco_id": 1
        }
    ],
    "Pantallas y Dispositivos": [
        {
            "id": "cell_phone",
            "name": "Cell Phone",
            "description": "Teléfonos móviles (pueden mostrar información personal)",
            "source": "coco",
            "priority": "low",
            "coco_id": 67
        },
        {
            "id": "laptop",
            "name": "Laptop",
            "description": "Portátiles (pueden mostrar información personal)",
            "source": "coco",
            "priority": "low",
            "coco_id": 63
        },
        {
            "id": "tv",
            "name": "TV/Monitor",
            "description": "Televisores y monitores (pueden mostrar información)",
            "source": "coco",
            "priority": "low",
            "coco_id": 62
        }
    ],
    "Documentos": [
        {
            "id": "book",
            "name": "Book",
            "description": "Libros (pueden contener texto sensible)",
            "source": "coco",
            "priority": "low",
            "coco_id": 73
        }
    ],
    "Objetos Personales": [
        {
            "id": "handbag",
            "name": "Handbag",
            "description": "Bolsos y carteras",
            "source": "coco",
            "priority": "low",
            "coco_id": 26
        },
        {
            "id": "backpack",
            "name": "Backpack",
            "description": "Mochilas",
            "source": "coco",
            "priority": "low",
            "coco_id": 24
        },
        {
            "id": "suitcase",
            "name": "Suitcase",
            "description": "Maletas",
            "source": "coco",
            "priority": "low",
            "coco_id": 28
        }
    ],
    "Otros": [
        {
            "id": "clock",
            "name": "Clock",
            "description": "Relojes (información temporal)",
            "source": "coco",
            "priority": "low",
            "coco_id": 74
        }
    ]
}


@router.get("/classes")
async def get_available_classes():
    """
    Obtiene todas las clases disponibles para detección organizadas por categorías

    Returns:
        JSON con clases organizadas por categorías y metadata
    """
    logger.info("Obteniendo clases disponibles")

    # Calcular totales
    total_classes = sum(len(classes) for classes in RGPD_CLASSES.values())
    trained_classes = sum(
        1 for category in RGPD_CLASSES.values()
        for cls in category
        if cls["source"] == "trained"
    )
    coco_classes = total_classes - trained_classes

    return {
        "success": True,
        "categories": RGPD_CLASSES,
        "stats": {
            "total_classes": total_classes,
            "trained_classes": trained_classes,
            "coco_classes": coco_classes,
            "total_categories": len(RGPD_CLASSES)
        },
        "defaults": {
            "recommended": ["face", "plate"],  # Clases recomendadas por defecto
            "high_priority": [
                cls["id"] for category in RGPD_CLASSES.values()
                for cls in category
                if cls.get("priority") == "high"
            ]
        }
    }


@router.get("/classes/flat")
async def get_classes_flat():
    """
    Obtiene todas las clases disponibles en formato plano (sin categorías)

    Returns:
        JSON con lista plana de todas las clases
    """
    logger.info("Obteniendo clases disponibles (formato plano)")

    all_classes = []
    for category_name, classes in RGPD_CLASSES.items():
        for cls in classes:
            class_data = cls.copy()
            class_data["category"] = category_name
            all_classes.append(class_data)

    return {
        "success": True,
        "classes": all_classes,
        "total": len(all_classes)
    }


@router.get("/classes/{class_id}")
async def get_class_info(class_id: str):
    """
    Obtiene información detallada de una clase específica

    Args:
        class_id: ID de la clase

    Returns:
        JSON con información de la clase
    """
    logger.info(f"Obteniendo información de clase: {class_id}")

    # Buscar clase
    for category_name, classes in RGPD_CLASSES.items():
        for cls in classes:
            if cls["id"] == class_id:
                return {
                    "success": True,
                    "class": {**cls, "category": category_name}
                }

    return {
        "success": False,
        "error": f"Clase '{class_id}' no encontrada"
    }


@router.get("/classes/category/{category_name}")
async def get_classes_by_category(category_name: str):
    """
    Obtiene todas las clases de una categoría específica

    Args:
        category_name: Nombre de la categoría

    Returns:
        JSON con clases de la categoría
    """
    logger.info(f"Obteniendo clases de categoría: {category_name}")

    if category_name not in RGPD_CLASSES:
        return {
            "success": False,
            "error": f"Categoría '{category_name}' no encontrada",
            "available_categories": list(RGPD_CLASSES.keys())
        }

    return {
        "success": True,
        "category": category_name,
        "classes": RGPD_CLASSES[category_name],
        "total": len(RGPD_CLASSES[category_name])
    }
