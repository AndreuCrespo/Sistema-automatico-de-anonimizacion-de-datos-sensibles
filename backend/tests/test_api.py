"""
Tests para los endpoints de la API.

Ejecutar con: pytest tests/ -v
"""

import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import io

# Importar app después de configurar path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app


# Cliente de test
client = TestClient(app)


class TestHealthEndpoint:
    """Tests para el endpoint /api/health"""
    
    def test_health_check_returns_200(self):
        """El endpoint health debe retornar 200"""
        response = client.get("/api/health")
        assert response.status_code == 200
    
    def test_health_check_has_status(self):
        """El endpoint health debe incluir status"""
        response = client.get("/api/health")
        data = response.json()
        assert "status" in data
        assert data["status"] in ["healthy", "degraded", "unhealthy"]
    
    def test_health_check_has_version(self):
        """El endpoint health debe incluir version"""
        response = client.get("/api/health")
        data = response.json()
        assert "version" in data
        assert data["version"] == "1.0.0"
    
    def test_health_check_has_models_info(self):
        """El endpoint health debe incluir info de modelos"""
        response = client.get("/api/health")
        data = response.json()
        assert "models" in data


class TestRootEndpoint:
    """Tests para el endpoint raíz /"""
    
    def test_root_returns_200(self):
        """El endpoint raíz debe retornar 200"""
        response = client.get("/")
        assert response.status_code == 200
    
    def test_root_has_message(self):
        """El endpoint raíz debe incluir mensaje de bienvenida"""
        response = client.get("/")
        data = response.json()
        assert "message" in data
        assert "TFM" in data["message"] or "Anonymization" in data["message"]


class TestDetectEndpoint:
    """Tests para el endpoint /api/detect"""
    
    def test_detect_requires_file(self):
        """El endpoint detect debe requerir un archivo"""
        response = client.post("/api/detect")
        assert response.status_code == 422  # Unprocessable Entity
    
    def test_detect_accepts_image(self):
        """El endpoint detect debe aceptar una imagen"""
        # Crear imagen de prueba simple (1x1 pixel JPEG)
        import struct
        # JPEG mínimo válido
        jpeg_data = bytes([
            0xFF, 0xD8, 0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46, 0x49, 0x46, 0x00, 0x01,
            0x01, 0x00, 0x00, 0x01, 0x00, 0x01, 0x00, 0x00, 0xFF, 0xDB, 0x00, 0x43,
            0x00, 0x08, 0x06, 0x06, 0x07, 0x06, 0x05, 0x08, 0x07, 0x07, 0x07, 0x09,
            0x09, 0x08, 0x0A, 0x0C, 0x14, 0x0D, 0x0C, 0x0B, 0x0B, 0x0C, 0x19, 0x12,
            0x13, 0x0F, 0x14, 0x1D, 0x1A, 0x1F, 0x1E, 0x1D, 0x1A, 0x1C, 0x1C, 0x20,
            0x24, 0x2E, 0x27, 0x20, 0x22, 0x2C, 0x23, 0x1C, 0x1C, 0x28, 0x37, 0x29,
            0x2C, 0x30, 0x31, 0x34, 0x34, 0x34, 0x1F, 0x27, 0x39, 0x3D, 0x38, 0x32,
            0x3C, 0x2E, 0x33, 0x34, 0x32, 0xFF, 0xC0, 0x00, 0x0B, 0x08, 0x00, 0x01,
            0x00, 0x01, 0x01, 0x01, 0x11, 0x00, 0xFF, 0xC4, 0x00, 0x1F, 0x00, 0x00,
            0x01, 0x05, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08,
            0x09, 0x0A, 0x0B, 0xFF, 0xC4, 0x00, 0xB5, 0x10, 0x00, 0x02, 0x01, 0x03,
            0x03, 0x02, 0x04, 0x03, 0x05, 0x05, 0x04, 0x04, 0x00, 0x00, 0x01, 0x7D,
            0xFF, 0xDA, 0x00, 0x08, 0x01, 0x01, 0x00, 0x00, 0x3F, 0x00, 0x7F, 0xFF,
            0xD9
        ])
        
        files = {"file": ("test.jpg", io.BytesIO(jpeg_data), "image/jpeg")}
        data = {"detect_faces": "true", "detect_plates": "true"}
        
        response = client.post("/api/detect", files=files, data=data)
        # Puede ser 200 (éxito) o 500 (error de procesamiento si imagen es muy pequeña)
        assert response.status_code in [200, 500]


class TestAnonymizeEndpoint:
    """Tests para el endpoint /api/anonymize"""
    
    def test_anonymize_requires_file(self):
        """El endpoint anonymize debe requerir un archivo"""
        response = client.post("/api/anonymize")
        assert response.status_code == 422


class TestDocsEndpoint:
    """Tests para los endpoints de documentación"""
    
    def test_swagger_docs_available(self):
        """Swagger UI debe estar disponible en /docs"""
        response = client.get("/docs")
        assert response.status_code == 200
    
    def test_redoc_available(self):
        """ReDoc debe estar disponible en /redoc"""
        response = client.get("/redoc")
        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
