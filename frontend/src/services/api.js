/**
 * Servicio de API para comunicacion con el backend.
 *
 * Endpoints disponibles:
 * - GET /api/health: Health check
 * - POST /api/detect: Deteccion de rostros/matriculas
 * - POST /api/anonymize: Anonimizacion de imagen
 * - POST /api/process-video: Procesamiento de video
 * - POST /api/video-info: Informacion de video
 * - WS /api/ws/process-video: Procesamiento de video con streaming
 */

import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  }
});

/**
 * Verifica el estado del servicio.
 * @returns {Promise} Estado del servicio
 */
export const healthCheck = async () => {
  const response = await api.get('/api/health');
  return response.data;
};

/**
 * Detecta rostros y/o matriculas en una imagen.
 * @param {File} file - Archivo de imagen
 * @param {Object} options - Opciones de deteccion
 * @returns {Promise} Resultado de deteccion
 */
export const detectObjects = async (file, options = {}) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('detect_faces', options.detectFaces ?? true);
  formData.append('detect_plates', options.detectPlates ?? true);
  formData.append('confidence_threshold', options.confidenceThreshold ?? 0.5);

  const response = await api.post('/api/detect', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    }
  });

  return response.data;
};

/**
 * Anonimiza una imagen.
 * @param {File} file - Archivo de imagen
 * @param {Object} options - Opciones de anonimizacion
 * @returns {Promise} Imagen anonimizada (Blob)
 */
export const anonymizeImage = async (file, options = {}) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('detect_faces', options.detectFaces ?? true);
  formData.append('detect_plates', options.detectPlates ?? true);
  formData.append('method', options.method || 'blur');
  formData.append('confidence_threshold', options.confidenceThreshold ?? 0.5);
  formData.append('blur_kernel_size', options.blurKernelSize || 99);
  formData.append('pixelate_blocks', options.pixelateBlocks || 10);

  const response = await api.post('/api/anonymize', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    responseType: 'blob'
  });

  // Extraer metadatos de headers
  const metadata = {
    facesDetected: parseInt(response.headers['x-faces-detected'] || 0),
    platesDetected: parseInt(response.headers['x-plates-detected'] || 0),
    totalDetections: parseInt(response.headers['x-total-detections'] || 0),
    processingTime: parseFloat(response.headers['x-processing-time-ms'] || 0),
    method: response.headers['x-anonymization-method'] || options.method
  };

  return {
    blob: response.data,
    metadata
  };
};

/**
 * Obtiene informacion de un video sin procesarlo
 * @param {File} file - Archivo de video
 * @returns {Promise} Informacion del video
 */
export const getVideoInfo = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post('/api/video-info', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    timeout: 60000, // 60 segundos para videos grandes
  });

  return response.data;
};

/**
 * Procesa un video aplicando anonimizacion
 * @param {File} file - Archivo de video
 * @param {Object} options - Opciones de procesamiento
 * @param {Function} onProgress - Callback para progreso (opcional)
 * @returns {Promise} Video procesado (Blob) y metadata
 */
export const processVideo = async (file, options = {}, onProgress = null) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('detect_faces', options.detectFaces ?? true);
  formData.append('detect_plates', options.detectPlates ?? true);
  formData.append('anonymization_method', options.method || 'blur');
  formData.append('blur_kernel_size', options.blurKernelSize || 51);
  formData.append('pixelate_blocks', options.pixelateBlocks || 10);

  const response = await api.post('/api/process-video', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    responseType: 'blob',
    timeout: 600000, // 10 minutos para videos largos
    onUploadProgress: (progressEvent) => {
      if (onProgress && progressEvent.total) {
        const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        onProgress({ type: 'upload', percent: percentCompleted });
      }
    },
  });

  // Extraer metadata de headers
  const metadata = {
    processingTime: parseFloat(response.headers['x-processing-time'] || 0),
    totalFaces: parseInt(response.headers['x-total-faces'] || 0),
    totalPlates: parseInt(response.headers['x-total-plates'] || 0),
    framesProcessed: parseInt(response.headers['x-frames-processed'] || 0),
    framesWithDetections: parseInt(response.headers['x-frames-with-detections'] || 0),
  };

  return {
    blob: response.data,
    metadata
  };
};

/**
 * Procesa video con WebSocket para actualizaciones en tiempo real
 * @param {File} file - Archivo de video
 * @param {Object} options - Opciones de procesamiento
 * @param {Function} onProgress - Callback para progreso
 * @param {Function} onComplete - Callback para finalizacion
 * @param {Function} onError - Callback para errores
 * @returns {WebSocket} Conexion WebSocket
 */
export const processVideoWithWebSocket = (file, options = {}, onProgress, onComplete, onError) => {
  const wsUrl = API_BASE_URL.replace('http', 'ws') + '/api/ws/process-video';
  const ws = new WebSocket(wsUrl);

  ws.onopen = async () => {
    console.log('WebSocket conectado');

    // Leer archivo como base64
    const reader = new FileReader();
    reader.onload = () => {
      const base64 = reader.result.split(',')[1]; // Remover prefijo data:

      const data = {
        video_data: base64,
        filename: file.name,
        detect_faces: options.detectFaces ?? true,
        detect_plates: options.detectPlates ?? true,
        anonymization_method: options.method || 'blur',
        blur_kernel_size: options.blurKernelSize || 51,
        pixelate_blocks: options.pixelateBlocks || 10,
        enable_preview: options.enablePreview ?? true,
      };

      ws.send(JSON.stringify(data));
    };

    reader.readAsDataURL(file);
  };

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);

      if (data.type === 'progress' && onProgress) {
        onProgress(data);
      } else if (data.type === 'complete' && onComplete) {
        onComplete(data.result);
      } else if (data.type === 'video' && onComplete) {
        // Convertir base64 a Blob
        const videoBlob = base64ToBlob(data.video_data, 'video/mp4');
        onComplete({
          blob: videoBlob,
          stats: data.stats
        });
        ws.close();
      } else if (data.type === 'error' && onError) {
        onError(new Error(data.message));
        ws.close();
      }
    } catch (e) {
      console.error('Error procesando mensaje WebSocket:', e);
      if (onError) onError(e);
    }
  };

  ws.onerror = (error) => {
    console.error('Error en WebSocket:', error);
    if (onError) onError(error);
  };

  ws.onclose = () => {
    console.log('WebSocket desconectado');
  };

  return ws;
};

/**
 * Convierte base64 a Blob
 * @param {string} base64 - String base64
 * @param {string} mimeType - Tipo MIME
 * @returns {Blob} Blob
 */
const base64ToBlob = (base64, mimeType) => {
  const byteCharacters = atob(base64);
  const byteNumbers = new Array(byteCharacters.length);

  for (let i = 0; i < byteCharacters.length; i++) {
    byteNumbers[i] = byteCharacters.charCodeAt(i);
  }

  const byteArray = new Uint8Array(byteNumbers);
  return new Blob([byteArray], { type: mimeType });
};

/**
 * Obtiene las categorías de datos sensibles disponibles para texto
 * @param {string} mode - Modo de detección (regex, llm, both)
 * @returns {Promise} Categorías de texto
 */
export const getTextCategories = async (mode = 'regex') => {
  const response = await api.get('/api/text/categories', {
    params: { mode }
  });
  return response.data;
};

/**
 * Analiza y anonimiza texto
 * @param {string} text - Texto a analizar
 * @param {Array} categories - Categorías a detectar
 * @param {string} method - Método de anonimización (replace, mask, remove)
 * @param {string} mode - Modo de detección (regex, llm, both)
 * @returns {Promise} Resultado del análisis
 */
export const analyzeText = async (text, categories = null, method = 'replace', mode = 'regex') => {
  const response = await api.post('/api/analyze-text', {
    text,
    categories,
    anonymization_method: method,
    detection_mode: mode
  });
  return response.data;
};

/**
 * Solo detecta datos sensibles sin anonimizar
 * @param {string} text - Texto a analizar
 * @param {Array} categories - Categorías a detectar
 * @param {string} mode - Modo de detección (regex, llm, both)
 * @returns {Promise} Detecciones
 */
export const detectText = async (text, categories = null, mode = 'regex') => {
  const response = await api.post('/api/detect-text', {
    text,
    categories,
    detection_mode: mode
  });
  return response.data;
};

export default api;
