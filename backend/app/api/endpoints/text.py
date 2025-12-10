"""
Text Analysis Endpoints
Endpoints para análisis y anonimización de texto
"""

import time
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import logging

from app.services.text_analyzer import TextAnalyzer

router = APIRouter()
logger = logging.getLogger(__name__)

# Instancia del analizador de texto (singleton)
_text_analyzer = None


def get_text_analyzer() -> TextAnalyzer:
    """Obtiene instancia singleton del analizador de texto"""
    global _text_analyzer
    if _text_analyzer is None:
        _text_analyzer = TextAnalyzer()
        logger.info("TextAnalyzer inicializado")
    return _text_analyzer


# Modelos Pydantic
class TextAnalysisRequest(BaseModel):
    """Request para análisis de texto"""
    text: str
    categories: Optional[List[str]] = None  # None = todas
    anonymization_method: str = 'replace'  # replace, mask, remove
    detection_mode: str = 'regex'  # regex, llm, both


class TextAnalysisResponse(BaseModel):
    """Response con texto anonimizado y detecciones"""
    success: bool
    original_text: str
    anonymized_text: str
    detections: List[dict]
    total_detections: int
    stats: dict
    method: str
    mode: str
    value_map: dict


@router.get("/text/categories")
async def get_text_categories(mode: str = 'regex'):
    """
    Obtiene las categorías de datos sensibles disponibles para texto

    Args:
        mode: Modo de detección ('regex', 'llm', 'both')

    Returns:
        JSON con categorías disponibles según el modo
    """
    logger.info(f"Obteniendo categorías de texto para modo: {mode}")

    analyzer = get_text_analyzer()

    # Obtener modos disponibles
    available_modes = analyzer.get_available_modes()

    # Obtener categorías según el modo
    categories = analyzer.get_available_categories(mode)

    # Organizar por grupos
    organized = {}

    # Grupos Regex
    if mode in ['regex', 'both']:
        organized["Identificación Personal"] = {
            k: v for k, v in [
                ("dni_nie", categories.get("dni_nie")),
                ("passport", categories.get("passport")),
                ("social_security", categories.get("social_security")),
            ] if v is not None
        }
        organized["Contacto"] = {
            k: v for k, v in [
                ("phone", categories.get("phone")),
                ("email", categories.get("email")),
                ("postal_code", categories.get("postal_code")),
            ] if v is not None
        }
        organized["Datos Financieros"] = {
            k: v for k, v in [
                ("credit_card", categories.get("credit_card")),
                ("iban", categories.get("iban")),
            ] if v is not None
        }
        organized["Otros"] = {
            k: v for k, v in [
                ("ip_address", categories.get("ip_address")),
                ("date", categories.get("date")),
            ] if v is not None
        }

    # Grupos adicionales LLM
    if mode in ['llm', 'both']:
        organized["Entidades Contextuales (LLM)"] = {
            k: v for k, v in [
                ("person_name", categories.get("person_name")),
                ("location", categories.get("location")),
                ("organization", categories.get("organization")),
                ("vehicle_plate", categories.get("vehicle_plate")),
                ("medical_info", categories.get("medical_info")),
            ] if v is not None
        }

    return {
        "success": True,
        "available_modes": available_modes,
        "current_mode": mode,
        "ollama_available": analyzer.ollama_available,
        "categories": organized,
        "flat_categories": categories,
        "total": len(categories)
    }


@router.post("/analyze-text")
async def analyze_text(request: TextAnalysisRequest):
    """
    Analiza texto y detecta/anonimiza datos sensibles

    Args:
        request: TextAnalysisRequest con texto y opciones

    Returns:
        TextAnalysisResponse con texto anonimizado y detecciones
    """
    start_time = time.perf_counter()
    
    logger.info(f"Analizando texto de {len(request.text)} caracteres")
    logger.info(f"Categorías solicitadas: {request.categories or 'todas'}")
    logger.info(f"Método: {request.anonymization_method}")

    if not request.text or len(request.text.strip()) == 0:
        raise HTTPException(status_code=400, detail="El texto no puede estar vacío")

    if len(request.text) > 100000:  # Límite de 100k caracteres
        raise HTTPException(
            status_code=400,
            detail="El texto es demasiado largo (máximo 100,000 caracteres)"
        )

    try:
        analyzer = get_text_analyzer()

        # Analizar y anonimizar
        result = analyzer.anonymize_text(
            text=request.text,
            categories=request.categories,
            method=request.anonymization_method,
            mode=request.detection_mode
        )

        processing_time_ms = (time.perf_counter() - start_time) * 1000
        
        logger.info(f"Análisis completado: {result['total_detections']} detecciones en {processing_time_ms:.2f}ms")
        logger.info(f"Estadísticas: {result['stats']}")
        logger.info(f"Modo usado: {result['mode']}")

        response_data = {
            "success": True,
            "original_text": result['original_text'],
            "anonymized_text": result['anonymized_text'],
            "detections": result['detections'],
            "total_detections": result['total_detections'],
            "stats": result['stats'],
            "method": result['method'],
            "mode": result['mode'],
            "value_map": result['value_map'],
            "processing_time_ms": round(processing_time_ms, 2)
        }
        
        return JSONResponse(
            content=response_data,
            headers={"X-Processing-Time-Ms": str(round(processing_time_ms, 2))}
        )

    except Exception as e:
        logger.error(f"Error analizando texto: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/detect-text")
async def detect_text_only(request: TextAnalysisRequest):
    """
    Solo detecta datos sensibles sin anonimizar (para preview)

    Args:
        request: TextAnalysisRequest con texto y categorías

    Returns:
        JSON con detecciones
    """
    logger.info(f"Detectando en texto de {len(request.text)} caracteres")

    if not request.text or len(request.text.strip()) == 0:
        raise HTTPException(status_code=400, detail="El texto no puede estar vacío")

    try:
        analyzer = get_text_analyzer()

        # Solo detectar
        detections = analyzer.detect_sensitive_data(
            text=request.text,
            categories=request.categories,
            mode=request.detection_mode
        )

        # Estadísticas
        stats = {}
        for detection in detections:
            dtype = detection['type']
            stats[dtype] = stats.get(dtype, 0) + 1

        return {
            "success": True,
            "detections": detections,
            "total_detections": len(detections),
            "stats": stats,
            "mode": request.detection_mode
        }

    except Exception as e:
        logger.error(f"Error detectando en texto: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
