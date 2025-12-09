"""
Configuración de logging estructurado con Loguru.

Proporciona logging JSON para producción y formato legible para desarrollo.
"""

import sys
from pathlib import Path
from loguru import logger

from app.core.config import settings


def setup_logging():
    """
    Configura el sistema de logging con Loguru.
    
    Características:
    - Formato JSON para producción
    - Formato legible para desarrollo
    - Rotación de archivos por tamaño
    - Niveles configurables
    """
    # Remover handler por defecto
    logger.remove()
    
    # Determinar formato según modo
    if settings.DEBUG:
        # Formato legible para desarrollo
        log_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        )
        
        # Handler de consola con colores
        logger.add(
            sys.stderr,
            format=log_format,
            level="DEBUG",
            colorize=True,
            backtrace=True,
            diagnose=True
        )
    else:
        # Formato JSON para producción
        logger.add(
            sys.stderr,
            format="{message}",
            level="INFO",
            serialize=True,  # Salida JSON
            backtrace=False,
            diagnose=False
        )
    
    # Archivo de log con rotación
    log_dir = settings.PROJECT_ROOT / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    logger.add(
        log_dir / "app_{time:YYYY-MM-DD}.log",
        rotation="10 MB",  # Rotar cuando llegue a 10MB
        retention="7 days",  # Mantener 7 días
        compression="zip",  # Comprimir logs antiguos
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        level="INFO",
        encoding="utf-8"
    )
    
    # Log de errores separado
    logger.add(
        log_dir / "errors_{time:YYYY-MM-DD}.log",
        rotation="10 MB",
        retention="30 days",
        compression="zip",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        level="ERROR",
        encoding="utf-8"
    )
    
    logger.info("Sistema de logging configurado correctamente")
    
    return logger


# Configurar logging al importar el módulo
app_logger = setup_logging()


def get_logger(name: str = None):
    """
    Obtiene un logger con contexto específico.
    
    Args:
        name: Nombre del módulo o contexto
        
    Returns:
        Logger configurado
    """
    if name:
        return logger.bind(name=name)
    return logger
