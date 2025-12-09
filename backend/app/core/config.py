"""
Configuracion central de la aplicacion.

Define paths, parametros de modelos, y configuraciones globales.
"""

from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Configuracion de la aplicacion."""

    # Informacion de la aplicacion
    APP_NAME: str = "TFM Anonymization System"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "Sistema automatico de anonimizacion de rostros y matriculas"

    # Configuracion del servidor
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True

    # Paths
    PROJECT_ROOT: Path = Path(__file__).parent.parent.parent.parent
    MODELS_DIR: Path = PROJECT_ROOT / "models" / "trained"
    TEMP_DIR: Path = PROJECT_ROOT / "temp"
    OUTPUTS_DIR: Path = PROJECT_ROOT / "outputs"

    # Modelos
    FACE_MODEL_PATH: Optional[Path] = MODELS_DIR / "face_detector.pt"
    PLATE_MODEL_PATH: Optional[Path] = MODELS_DIR / "plate_detector.pt"

    # Parametros de deteccion YOLOv8
    DETECTION_CONFIDENCE: float = 0.5  # Confianza minima para detecciones
    DETECTION_IOU: float = 0.45  # IoU threshold para NMS

    # Parametros de anonimizacion
    BLUR_KERNEL_SIZE: int = 99  # Tamano del kernel para Gaussian Blur
    PIXELATE_BLOCKS: int = 10  # Numero de bloques para pixelacion

    # Limites de archivos
    MAX_FILE_SIZE_MB: int = 10
    ALLOWED_EXTENSIONS: set = {".jpg", ".jpeg", ".png", ".bmp"}

    # Configuración Ollama (LLM para análisis de texto)
    OLLAMA_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen3:8b"

    class Config:
        env_file = ".env"
        case_sensitive = True


# Instancia global de configuracion
settings = Settings()

# Crear directorios si no existen
settings.TEMP_DIR.mkdir(parents=True, exist_ok=True)
settings.OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
settings.MODELS_DIR.mkdir(parents=True, exist_ok=True)
