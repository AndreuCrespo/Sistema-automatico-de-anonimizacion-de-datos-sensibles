"""
Schema para health check.
"""

from pydantic import BaseModel
from typing import Dict, Any


class HealthResponse(BaseModel):
    """
    Response del endpoint de health.

    Attributes:
        status: Estado del servicio ('healthy' o 'unhealthy')
        version: Version de la API
        models: Estado de los modelos cargados
    """
    status: str
    version: str
    models: Dict[str, Any]
