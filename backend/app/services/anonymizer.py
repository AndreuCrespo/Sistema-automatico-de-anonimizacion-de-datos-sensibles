"""
Servicio de anonimizacion de imagenes.

Implementa tecnicas de anonimizacion: Gaussian Blur, Pixelacion y Masking.
"""

import cv2
import numpy as np
from typing import List, Tuple, Literal
import logging


logger = logging.getLogger(__name__)


AnonymizationMethod = Literal["blur", "pixelate", "mask"]


class Anonymizer:
    """
    Clase para aplicar tecnicas de anonimizacion a regiones de una imagen.

    Metodos disponibles:
    - blur: Gaussian Blur
    - pixelate: Pixelacion
    - mask: Cuadro solido negro
    """

    @staticmethod
    def blur(
        image: np.ndarray,
        boxes: List[Tuple[int, int, int, int]],
        kernel_size: int = 99
    ) -> np.ndarray:
        """
        Aplica Gaussian Blur a las regiones especificadas.

        Args:
            image: Imagen original (BGR)
            boxes: Lista de bounding boxes (x1, y1, x2, y2)
            kernel_size: Tamano del kernel (debe ser impar)

        Returns:
            Imagen con regiones difuminadas
        """
        if kernel_size % 2 == 0:
            kernel_size += 1  # Asegurar que sea impar

        result = image.copy()

        for x1, y1, x2, y2 in boxes:
            # Extraer region
            roi = result[y1:y2, x1:x2]

            # Aplicar Gaussian Blur
            blurred = cv2.GaussianBlur(roi, (kernel_size, kernel_size), 0)

            # Reemplazar region
            result[y1:y2, x1:x2] = blurred

        logger.info(f"Aplicado blur a {len(boxes)} regiones")
        return result

    @staticmethod
    def pixelate(
        image: np.ndarray,
        boxes: List[Tuple[int, int, int, int]],
        blocks: int = 10
    ) -> np.ndarray:
        """
        Aplica pixelacion a las regiones especificadas.

        Args:
            image: Imagen original (BGR)
            boxes: Lista de bounding boxes (x1, y1, x2, y2)
            blocks: Numero de bloques por dimension

        Returns:
            Imagen con regiones pixeladas
        """
        result = image.copy()

        for x1, y1, x2, y2 in boxes:
            # Extraer region
            roi = result[y1:y2, x1:x2]
            h, w = roi.shape[:2]

            if h == 0 or w == 0:
                continue

            # Reducir tamano
            temp = cv2.resize(roi, (blocks, blocks), interpolation=cv2.INTER_LINEAR)

            # Ampliar de nuevo
            pixelated = cv2.resize(temp, (w, h), interpolation=cv2.INTER_NEAREST)

            # Reemplazar region
            result[y1:y2, x1:x2] = pixelated

        logger.info(f"Aplicado pixelate a {len(boxes)} regiones")
        return result

    @staticmethod
    def mask(
        image: np.ndarray,
        boxes: List[Tuple[int, int, int, int]],
        color: Tuple[int, int, int] = (0, 0, 0)
    ) -> np.ndarray:
        """
        Aplica un cuadro solido (negro por defecto) a las regiones especificadas.

        Args:
            image: Imagen original (BGR)
            boxes: Lista de bounding boxes (x1, y1, x2, y2)
            color: Color del cuadro en formato BGR

        Returns:
            Imagen con regiones enmascaradas
        """
        result = image.copy()

        for x1, y1, x2, y2 in boxes:
            cv2.rectangle(result, (x1, y1), (x2, y2), color, -1)

        logger.info(f"Aplicado mask a {len(boxes)} regiones")
        return result

    @staticmethod
    def anonymize(
        image: np.ndarray,
        boxes: List[Tuple[int, int, int, int]],
        method: AnonymizationMethod = "blur",
        **kwargs
    ) -> np.ndarray:
        """
        Aplica anonimizacion a las regiones especificadas.

        Args:
            image: Imagen original (BGR)
            boxes: Lista de bounding boxes (x1, y1, x2, y2)
            method: Metodo de anonimizacion ('blur', 'pixelate', 'mask')
            **kwargs: Parametros adicionales para el metodo

        Returns:
            Imagen anonimizada

        Raises:
            ValueError: Si el metodo no es valido
        """
        if not boxes:
            logger.warning("No hay regiones para anonimizar")
            return image.copy()

        if method == "blur":
            return Anonymizer.blur(image, boxes, **kwargs)
        elif method == "pixelate":
            return Anonymizer.pixelate(image, boxes, **kwargs)
        elif method == "mask":
            return Anonymizer.mask(image, boxes, **kwargs)
        else:
            raise ValueError(f"Metodo de anonimizacion invalido: {method}")


# Instancia global del anonimizador (stateless, no necesita singleton)
anonymizer = Anonymizer()
