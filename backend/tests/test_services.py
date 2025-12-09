"""
Tests para los servicios de anonimización.

Ejecutar con: pytest tests/ -v
"""

import pytest
import numpy as np
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.anonymizer import Anonymizer, anonymizer


class TestAnonymizer:
    """Tests para el servicio de anonimización"""
    
    def test_anonymizer_instance_exists(self):
        """Debe existir una instancia global del anonimizador"""
        assert anonymizer is not None
        assert isinstance(anonymizer, Anonymizer)
    
    def test_blur_returns_same_shape(self):
        """Blur debe retornar imagen del mismo tamaño"""
        # Crear imagen de prueba 100x100 BGR
        image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        boxes = [(10, 10, 50, 50)]
        
        result = Anonymizer.blur(image, boxes, kernel_size=15)
        
        assert result.shape == image.shape
    
    def test_pixelate_returns_same_shape(self):
        """Pixelate debe retornar imagen del mismo tamaño"""
        image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        boxes = [(10, 10, 50, 50)]
        
        result = Anonymizer.pixelate(image, boxes, blocks=5)
        
        assert result.shape == image.shape
    
    def test_mask_returns_same_shape(self):
        """Mask debe retornar imagen del mismo tamaño"""
        image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        boxes = [(10, 10, 50, 50)]
        
        result = Anonymizer.mask(image, boxes, color=(0, 0, 0))
        
        assert result.shape == image.shape
    
    def test_mask_applies_color(self):
        """Mask debe aplicar el color especificado"""
        image = np.ones((100, 100, 3), dtype=np.uint8) * 255  # Imagen blanca
        boxes = [(10, 10, 50, 50)]
        color = (0, 0, 255)  # Rojo en BGR
        
        result = Anonymizer.mask(image, boxes, color=color)
        
        # Verificar que la región está coloreada
        assert np.array_equal(result[20, 20], np.array(color))
    
    def test_anonymize_with_empty_boxes(self):
        """Anonymize con lista vacía debe retornar copia de imagen"""
        image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        boxes = []
        
        result = Anonymizer.anonymize(image, boxes, method="blur")
        
        assert result.shape == image.shape
    
    def test_anonymize_invalid_method_raises_error(self):
        """Anonymize con método inválido debe lanzar ValueError"""
        image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        boxes = [(10, 10, 50, 50)]
        
        with pytest.raises(ValueError):
            Anonymizer.anonymize(image, boxes, method="invalid_method")
    
    def test_blur_kernel_size_always_odd(self):
        """Blur debe asegurar kernel_size impar"""
        image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        boxes = [(10, 10, 50, 50)]
        
        # Kernel par (14) debe funcionar sin error
        result = Anonymizer.blur(image, boxes, kernel_size=14)
        assert result.shape == image.shape


class TestAnonymizerMethods:
    """Tests para verificar que cada método modifica la imagen"""
    
    def test_blur_modifies_region(self):
        """Blur debe modificar la región especificada"""
        image = np.ones((100, 100, 3), dtype=np.uint8) * 128
        # Poner valores distintos en la región a difuminar
        image[20:40, 20:40] = 255
        
        boxes = [(20, 20, 40, 40)]
        result = Anonymizer.blur(image, boxes, kernel_size=15)
        
        # La región debe haber sido modificada
        # (el promedio debería ser diferente debido al blur)
        assert not np.array_equal(result[20:40, 20:40], image[20:40, 20:40])
    
    def test_pixelate_modifies_region(self):
        """Pixelate debe modificar la región especificada"""
        # Crear imagen con gradiente
        image = np.zeros((100, 100, 3), dtype=np.uint8)
        for i in range(100):
            image[i, :] = i * 2
        
        boxes = [(20, 20, 60, 60)]
        original_region = image[20:60, 20:60].copy()
        result = Anonymizer.pixelate(image, boxes, blocks=4)
        
        # La región debe haber sido modificada
        assert not np.array_equal(result[20:60, 20:60], original_region)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
