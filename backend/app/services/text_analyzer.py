"""
Text Analyzer Service
Detecta y anonimiza datos sensibles en texto usando patrones regex y/o LLM local
"""

import re
import json
import requests
import os
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class TextAnalyzer:
    """
    Analizador de texto para detectar datos sensibles
    Soporta 3 modos: regex, llm, both
    """

    def __init__(self, ollama_url: str = None, model: str = None):
        """
        Inicializa el analizador con patrones regex y configuración LLM

        Args:
            ollama_url: URL del servidor Ollama
            model: Modelo LLM a usar (default: qwen3:8b)
        """
        from app.core.config import settings
        
        self.ollama_url = ollama_url or settings.OLLAMA_URL
        self.model = model or settings.OLLAMA_MODEL
        self.ollama_available = self._check_ollama_availability()

        # Patrones regex (disponibles siempre)
        self.regex_patterns = {
            'phone': {
                'name': 'Teléfono',
                'patterns': [
                    # Formato español: +34 612 345 678 o 612 345 678
                    r'\b(?:\+34\s?)?[6-9]\d{2}[\s.-]?\d{3}[\s.-]?\d{3}\b',
                    # Formato español con grupos de 2: 612 34 56 78
                    r'\b(?:\+34\s?)?[6-9]\d{2}[\s.-]?\d{2}[\s.-]?\d{2}[\s.-]?\d{2}\b',
                    # Fijos españoles: 91 555 12 34 o 915 555 123
                    r'\b9[1-9]\d[\s.-]?\d{3}[\s.-]?\d{3}\b',
                    r'\b9[1-9]\d[\s.-]?\d{2}[\s.-]?\d{2}[\s.-]?\d{2}\b',
                ],
                'mode': 'regex'
            },
            'email': {
                'name': 'Email',
                'patterns': [
                    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                ],
                'mode': 'regex'
            },
            'dni_nie': {
                'name': 'DNI/NIE',
                'patterns': [
                    r'\b[0-9]{8}[A-Z]\b',
                    r'\b[XYZ][0-9]{7}[A-Z]\b',
                ],
                'mode': 'regex'
            },
            'credit_card': {
                'name': 'Tarjeta de Crédito',
                'patterns': [
                    r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
                ],
                'mode': 'regex'
            },
            'iban': {
                'name': 'IBAN',
                'patterns': [
                    r'\bES\d{2}\s?\d{4}\s?\d{4}\s?\d{4}\s?\d{4}\s?\d{4}\b',
                ],
                'mode': 'regex'
            },
            'passport': {
                'name': 'Pasaporte',
                'patterns': [
                    r'\b[A-Z]{3}\d{6}\b',
                ],
                'mode': 'regex'
            },
            'social_security': {
                'name': 'Número Seguridad Social',
                'patterns': [
                    r'\b\d{2}/\d{8}/\d{2}\b',
                    r'\b\d{12}\b',
                ],
                'mode': 'regex'
            },
            'ip_address': {
                'name': 'Dirección IP',
                'patterns': [
                    r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
                ],
                'mode': 'regex'
            },
            'date': {
                'name': 'Fecha',
                'patterns': [
                    r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
                    r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b',
                ],
                'mode': 'regex'
            },
            'postal_code': {
                'name': 'Código Postal',
                'patterns': [
                    r'\b\d{5}\b',
                ],
                'mode': 'regex'
            }
        }

        # Categorías adicionales solo disponibles con LLM
        self.llm_categories = {
            'person_name': {
                'name': 'Nombre de Persona',
                'mode': 'llm'
            },
            'location': {
                'name': 'Localización',
                'mode': 'llm'
            },
            'organization': {
                'name': 'Organización',
                'mode': 'llm'
            },
            'vehicle_plate': {
                'name': 'Matrícula',
                'mode': 'llm'
            },
            'medical_info': {
                'name': 'Información Médica',
                'mode': 'llm'
            }
        }

    def _check_ollama_availability(self) -> bool:
        """Verifica si Ollama está disponible"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=2)
            available = response.status_code == 200
            if available:
                logger.info("Ollama detectado y disponible")
            return available
        except:
            logger.warning("Ollama no disponible - solo modo regex")
            return False

    def get_available_modes(self) -> List[str]:
        """Retorna los modos disponibles según si Ollama está activo"""
        if self.ollama_available:
            return ['regex', 'llm', 'both']
        else:
            return ['regex']

    def get_available_categories(self, mode: str = 'regex') -> Dict[str, str]:
        """
        Obtiene las categorías disponibles según el modo

        Args:
            mode: Modo de detección ('regex', 'llm', 'both')

        Returns:
            Dict con id -> nombre de categoría
        """
        categories = {}

        if mode in ['regex', 'both']:
            categories.update({
                cat_id: info['name']
                for cat_id, info in self.regex_patterns.items()
            })

        if mode in ['llm', 'both'] and self.ollama_available:
            categories.update({
                cat_id: info['name']
                for cat_id, info in self.llm_categories.items()
            })

        return categories

    def detect_with_regex(
        self,
        text: str,
        categories: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Detecta datos sensibles usando patrones regex

        Args:
            text: Texto a analizar
            categories: Categorías específicas a detectar

        Returns:
            Lista de detecciones
        """
        if categories is None:
            categories = list(self.regex_patterns.keys())

        detections = []

        for category in categories:
            if category not in self.regex_patterns:
                continue

            category_info = self.regex_patterns[category]

            for pattern_str in category_info['patterns']:
                pattern = re.compile(pattern_str, re.IGNORECASE)

                for match in pattern.finditer(text):
                    detection = {
                        'type': category,
                        'type_name': category_info['name'],
                        'text': match.group(),
                        'start': match.start(),
                        'end': match.end(),
                        'confidence': self._calculate_confidence(category, match.group()),
                        'source': 'regex'
                    }
                    detections.append(detection)

        return detections

    def detect_with_llm(
        self,
        text: str,
        categories: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Detecta datos sensibles usando LLM local (Ollama)

        Args:
            text: Texto a analizar
            categories: Categorías específicas a detectar

        Returns:
            Lista de detecciones
        """
        if not self.ollama_available:
            logger.warning("Ollama no disponible, no se puede usar detección LLM")
            return []

        if categories is None:
            # En modo both, LLM busca TODAS las categorías (regex + llm)
            categories = list(self.llm_categories.keys()) + list(self.regex_patterns.keys())

        # Aceptar tanto categorías LLM como regex
        valid_cats = [c for c in categories if c in self.llm_categories or c in self.regex_patterns]

        if not valid_cats:
            return []

        try:
            # Descripción de categorías para el prompt (incluir regex y llm)
            all_categories = {}
            for cat in valid_cats:
                if cat in self.llm_categories:
                    all_categories[cat] = self.llm_categories[cat]['name']
                elif cat in self.regex_patterns:
                    all_categories[cat] = self.regex_patterns[cat]['name']
            
            categories_desc = "\n".join([
                f"- {cat}: {name}"
                for cat, name in all_categories.items()
            ])

            # System prompt
            system_prompt = """Eres un experto en Procesamiento de Lenguaje Natural (NLP) y cumplimiento de GDPR. Tu tarea es analizar textos y extraer entidades de información personal (PII) en formato JSON estricto.

INSTRUCCIONES DE EXTRACCIÓN:
1. Literalidad: Extrae el texto EXACTO tal como aparece en el documento. No corrijas erratas ni normalices el texto.
2. Exhaustividad: Si tienes dudas sobre si algo es un nombre, extráelo. Es preferible un falso positivo a perder un dato sensible.
3. Contexto:
   - Nombres (person_name): Busca patrones como "Fdo:", "D./Dña.", "Sr./Sra.", nombres en firmas, destinatarios de emails y menciones en el cuerpo del texto.
   - Ubicaciones (location): Incluye ciudades (Madrid, Barcelona), países, provincias y direcciones completas.

DEFINICIÓN DE ENTIDADES:
- person_name: Nombres y apellidos de personas físicas (Ej: "Juan Pérez", "María García López").
- location: Ciudades, países, regiones o direcciones físicas (Ej: "Sevilla", "Calle Alcala 20", "España").
- organization: Empresas, instituciones o entidades legales.
- phone: Números de teléfono fijos o móviles.
- email: Direcciones de correo electrónico.
- dni_nie: Documentos de identidad (DNI, NIE, Pasaporte).
- credit_card: Números de tarjeta de crédito.
- iban: Cuentas bancarias IBAN.
- date: Fechas específicas.

EJEMPLOS (Sigue este patrón):

Input: "El cliente D. Carlos Ruiz con dni 12345678Z reside en Valencia. Contactar con soporte@empresa.com."
Output: {"detections": [{"type": "person_name", "text": "Carlos Ruiz"}, {"type": "dni_nie", "text": "12345678Z"}, {"type": "location", "text": "Valencia"}, {"type": "email", "text": "soporte@empresa.com"}]}

Input: "Atentamente, Lucía Fernández. Oficina de Madrid."
Output: {"detections": [{"type": "person_name", "text": "Lucía Fernández"}, {"type": "location", "text": "Madrid"}]}

FORMATO DE RESPUESTA:
Devuelve ÚNICAMENTE un objeto JSON válido. No incluyas texto antes ni después, ni bloques de código markdown (```json)."""

            # User prompt con el texto a analizar
            user_prompt = f"""Analiza el siguiente texto y extrae todas las entidades PII:

TEXTO:
\"\"\"{text}\"\"\"

Responde con JSON válido."""

            # Llamar a Ollama con Chat API
            response = requests.post(
                f"{self.ollama_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "stream": False,
                    "format": "json",
                    "options": {
                        "temperature": 0.2,
                        "top_p": 0.9
                    }
                },
                timeout=60
            )


            if response.status_code != 200:
                logger.error(f"Error en Ollama: {response.status_code}")
                return []

            result = response.json()
            # Chat API devuelve la respuesta en message.content
            llm_response = result.get('message', {}).get('content', '{}')

            # Parse respuesta
            try:
                parsed = json.loads(llm_response)
            except json.JSONDecodeError as e:
                logger.warning(f"Error parseando JSON del LLM: {e}")
                logger.debug(f"Respuesta raw: {llm_response[:500]}")
                return []
                
            detections = []

            for det in parsed.get('detections', []):
                entity_type = det.get('type')
                entity_text = det.get('text', '').strip()

                # Validar que la categoría existe (en llm_categories O regex_patterns)
                if entity_type not in self.llm_categories and entity_type not in self.regex_patterns:
                    logger.warning(f"LLM devolvió categoría inválida: {entity_type}")
                    continue

                # Validar que el texto no esté vacío
                if not entity_text or len(entity_text) < 2:
                    logger.debug(f"LLM devolvió texto vacío o muy corto: '{entity_text}'")
                    continue

                # Validar que el texto existe en el original (case-insensitive)
                if entity_text.lower() not in text.lower():
                    logger.warning(f"LLM devolvió '{entity_text}' que no existe en el texto original")
                    continue

                # Buscar TODAS las ocurrencias usando regex (case-insensitive)
                # Escapamos caracteres especiales de regex para búsqueda literal
                pattern = re.escape(entity_text)

                logger.debug(f"Buscando entidad LLM: '{entity_text}' (tipo: {entity_type})")

                for match in re.finditer(pattern, text, re.IGNORECASE):
                    # Usar el texto REAL del match, no el del LLM
                    actual_text = match.group()

                    # Obtener nombre del tipo desde llm_categories o regex_patterns
                    type_name = (
                        self.llm_categories.get(entity_type, {}).get('name') or
                        self.regex_patterns.get(entity_type, {}).get('name', entity_type)
                    )

                    detection = {
                        'type': entity_type,
                        'type_name': type_name,
                        'text': actual_text,  # Texto real del documento
                        'start': match.start(),
                        'end': match.end(),
                        'confidence': 0.75,  # LLM tiene menor confianza por naturaleza
                        'source': 'llm'
                    }
                    detections.append(detection)
                    logger.debug(f"  → Detectado en posición {match.start()}-{match.end()}: '{actual_text}'")

            return detections

        except Exception as e:
            logger.error(f"Error en detección LLM: {e}", exc_info=True)
            return []

    def detect_sensitive_data(
        self,
        text: str,
        categories: Optional[List[str]] = None,
        mode: str = 'regex'
    ) -> List[Dict]:
        """
        Detecta datos sensibles en el texto según el modo seleccionado

        Args:
            text: Texto a analizar
            categories: Categorías específicas a detectar (None = todas)
            mode: Modo de detección ('regex', 'llm', 'both')

        Returns:
            Lista de detecciones con posición, tipo y texto detectado
        """
        detections = []

        if mode in ['regex', 'both']:
            regex_cats = [c for c in (categories or self.regex_patterns.keys())
                         if c in self.regex_patterns]
            detections.extend(self.detect_with_regex(text, regex_cats))

        if mode in ['llm', 'both'] and self.ollama_available:
            # En modo 'both', el LLM busca TODAS las categorías (llm + regex) como segunda pasada
            if mode == 'both':
                all_cats = list(self.llm_categories.keys()) + list(self.regex_patterns.keys())
                llm_cats = [c for c in (categories or all_cats)]
            else:
                llm_cats = [c for c in (categories or self.llm_categories.keys())
                           if c in self.llm_categories]
            detections.extend(self.detect_with_llm(text, llm_cats))

        # Ordenar por posición
        detections.sort(key=lambda x: x['start'])

        # Eliminar duplicados solapados
        detections = self._remove_overlapping(detections)

        return detections

    def _calculate_confidence(self, category: str, text: str) -> float:
        """Calcula confianza de la detección con validaciones adicionales"""
        confidence = 0.85

        if category == 'dni_nie':
            if self._validate_dni(text):
                confidence = 0.95

        elif category == 'credit_card':
            if self._validate_credit_card(text):
                confidence = 0.90

        return confidence

    def _validate_dni(self, dni: str) -> bool:
        """Valida DNI/NIE español con letra de control"""
        try:
            letters = 'TRWAGMYFPDXBNJZSQVHLCKE'

            if dni[0] in 'XYZ':
                number = int(dni[1:8])
            else:
                number = int(dni[:8])

            expected_letter = letters[number % 23]
            return dni[-1].upper() == expected_letter
        except:
            return False

    def _validate_credit_card(self, card: str) -> bool:
        """Valida tarjeta de crédito con algoritmo de Luhn"""
        try:
            digits = re.sub(r'[-\s]', '', card)

            if not digits.isdigit():
                return False

            total = 0
            reverse_digits = digits[::-1]

            for i, digit in enumerate(reverse_digits):
                n = int(digit)
                if i % 2 == 1:
                    n *= 2
                    if n > 9:
                        n -= 9
                total += n

            return total % 10 == 0
        except:
            return False

    def _remove_overlapping(self, detections: List[Dict]) -> List[Dict]:
        """Elimina detecciones solapadas, manteniendo la de mayor confianza"""
        if not detections:
            return []

        result = [detections[0]]

        for detection in detections[1:]:
            last = result[-1]

            if detection['start'] >= last['end']:
                result.append(detection)
            elif detection['confidence'] > last['confidence']:
                result[-1] = detection

        return result

    def _normalize_value_for_token(self, value: str) -> str:
        """
        Normaliza un valor para asignación de tokens consistente

        Args:
            value: Valor a normalizar

        Returns:
            Valor normalizado
        """
        # Convertir a lowercase
        normalized = value.lower()
        # Eliminar espacios múltiples
        normalized = re.sub(r'\s+', ' ', normalized)
        # Strip
        normalized = normalized.strip()
        # Eliminar caracteres no imprimibles
        normalized = ''.join(char for char in normalized if char.isprintable())

        return normalized

    def _create_consistent_tokens(
        self,
        detections: List[Dict]
    ) -> Tuple[List[Dict], Dict[str, Dict[str, str]]]:
        """
        Crea tokens numerados consistentes para las detecciones

        Si el mismo valor aparece múltiples veces, usa el mismo token.
        Ejemplo: "Valencia" -> [LOCATION-1] en todas las ocurrencias

        Args:
            detections: Lista de detecciones

        Returns:
            Tupla de (detecciones con tokens, mapa de valores -> tokens)
        """
        # Mapa de tipo -> valor normalizado -> token
        value_to_token = defaultdict(dict)
        # Contador de tokens por tipo
        token_counters = defaultdict(int)

        for detection in detections:
            dtype = detection['type']
            value = detection['text']

            # Normalizar el valor para comparación agresiva
            normalized_value = self._normalize_value_for_token(value)

            logger.debug(f"Tokenizando: '{value}' -> normalizado: '{normalized_value}' (tipo: {dtype})")

            # Si este valor normalizado ya tiene un token asignado, reutilizarlo
            if normalized_value in value_to_token[dtype]:
                token = value_to_token[dtype][normalized_value]
                logger.debug(f"  → Reutilizando token existente: {token}")
            else:
                # Crear nuevo token
                token_counters[dtype] += 1
                token = f"[{dtype.upper()}-{token_counters[dtype]}]"
                value_to_token[dtype][normalized_value] = token
                logger.debug(f"  → Creando nuevo token: {token}")

            detection['replacement'] = token

        return detections, value_to_token

    def anonymize_text(
        self,
        text: str,
        categories: Optional[List[str]] = None,
        method: str = 'replace',
        mode: str = 'regex'
    ) -> Dict:
        """
        Anonimiza texto detectando y reemplazando datos sensibles

        Args:
            text: Texto original
            categories: Categorías a anonimizar (None = todas)
            method: Método de anonimización ('replace', 'mask', 'remove')
            mode: Modo de detección ('regex', 'llm', 'both')

        Returns:
            Dict con texto anonimizado, detecciones y estadísticas
        """
        # Detectar datos sensibles
        detections = self.detect_sensitive_data(text, categories, mode)

        # Crear tokens consistentes
        detections, value_map = self._create_consistent_tokens(detections)

        # Aplicar anonimización
        anonymized_text = text
        offset = 0

        for detection in detections:
            start = detection['start'] + offset
            end = detection['end'] + offset
            original = detection['text']

            if method == 'replace':
                replacement = detection['replacement']
            elif method == 'mask':
                replacement = '*' * len(original)
            elif method == 'remove':
                replacement = ''
            else:
                replacement = detection['replacement']

            anonymized_text = anonymized_text[:start] + replacement + anonymized_text[end:]
            offset += len(replacement) - len(original)

        # Estadísticas
        stats = {}
        for detection in detections:
            dtype = detection['type']
            stats[dtype] = stats.get(dtype, 0) + 1

        return {
            'original_text': text,
            'anonymized_text': anonymized_text,
            'detections': detections,
            'total_detections': len(detections),
            'stats': stats,
            'method': method,
            'mode': mode,
            'value_map': dict(value_map)  # Para referencia
        }
