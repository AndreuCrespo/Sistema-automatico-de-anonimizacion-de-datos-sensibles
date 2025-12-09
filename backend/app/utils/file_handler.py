"""
Utilidades para manejo de archivos.

Gestion de archivos temporales, validacion y limpieza.
"""

import os
import shutil
from pathlib import Path
from typing import Optional
import uuid
import logging
from datetime import datetime, timedelta

from app.core.config import settings


logger = logging.getLogger(__name__)


class FileHandler:
    """
    Gestor de archivos para la aplicacion.

    Maneja:
    - Guardado de archivos temporales
    - Validacion de archivos
    - Limpieza de archivos antiguos
    """

    @staticmethod
    def validate_file_extension(filename: str) -> bool:
        """
        Valida que la extension del archivo sea permitida.

        Args:
            filename: Nombre del archivo

        Returns:
            True si la extension es valida
        """
        ext = Path(filename).suffix.lower()
        return ext in settings.ALLOWED_EXTENSIONS

    @staticmethod
    def validate_file_size(file_size: int) -> bool:
        """
        Valida que el tamano del archivo no exceda el limite.

        Args:
            file_size: Tamano del archivo en bytes

        Returns:
            True si el tamano es valido
        """
        max_size_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
        return file_size <= max_size_bytes

    @staticmethod
    def generate_temp_filename(original_filename: str, prefix: str = "") -> str:
        """
        Genera un nombre de archivo temporal unico.

        Args:
            original_filename: Nombre del archivo original
            prefix: Prefijo opcional

        Returns:
            Nombre de archivo temporal unico
        """
        ext = Path(original_filename).suffix
        unique_id = uuid.uuid4().hex[:12]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if prefix:
            return f"{prefix}_{timestamp}_{unique_id}{ext}"
        else:
            return f"{timestamp}_{unique_id}{ext}"

    @staticmethod
    def save_temp_file(file_bytes: bytes, filename: str) -> Path:
        """
        Guarda un archivo temporal.

        Args:
            file_bytes: Contenido del archivo
            filename: Nombre del archivo

        Returns:
            Ruta al archivo guardado
        """
        temp_path = settings.TEMP_DIR / filename

        with open(temp_path, 'wb') as f:
            f.write(file_bytes)

        logger.info(f"Archivo temporal guardado: {temp_path}")
        return temp_path

    @staticmethod
    def delete_file(file_path: Path) -> bool:
        """
        Elimina un archivo.

        Args:
            file_path: Ruta al archivo

        Returns:
            True si se elimino correctamente
        """
        try:
            if file_path.exists():
                file_path.unlink()
                logger.info(f"Archivo eliminado: {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error al eliminar archivo {file_path}: {e}")
            return False

    @staticmethod
    def cleanup_old_files(directory: Path, max_age_hours: int = 24) -> int:
        """
        Limpia archivos antiguos de un directorio.

        Args:
            directory: Directorio a limpiar
            max_age_hours: Edad maxima de archivos en horas

        Returns:
            Numero de archivos eliminados
        """
        if not directory.exists():
            return 0

        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        deleted_count = 0

        for file_path in directory.iterdir():
            if file_path.is_file():
                # Obtener tiempo de modificacion
                mtime = datetime.fromtimestamp(file_path.stat().st_mtime)

                if mtime < cutoff_time:
                    try:
                        file_path.unlink()
                        deleted_count += 1
                        logger.info(f"Archivo antiguo eliminado: {file_path}")
                    except Exception as e:
                        logger.error(f"Error al eliminar {file_path}: {e}")

        if deleted_count > 0:
            logger.info(f"Limpieza completada: {deleted_count} archivos eliminados")

        return deleted_count

    @staticmethod
    def cleanup_temp_directory(max_age_hours: int = 24) -> int:
        """
        Limpia el directorio temporal de la aplicacion.

        Args:
            max_age_hours: Edad maxima de archivos en horas

        Returns:
            Numero de archivos eliminados
        """
        return FileHandler.cleanup_old_files(settings.TEMP_DIR, max_age_hours)


# Instancia global del file handler (stateless)
file_handler = FileHandler()
