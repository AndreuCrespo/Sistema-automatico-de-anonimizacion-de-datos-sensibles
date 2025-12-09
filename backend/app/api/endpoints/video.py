"""
Video Processing Endpoints
Endpoints para procesamiento de videos con anonimización
"""

from fastapi import APIRouter, File, UploadFile, WebSocket, WebSocketDisconnect, Form, HTTPException
from fastapi.responses import FileResponse
from typing import Optional
import logging
import tempfile
import os
from pathlib import Path
import time
import asyncio
import base64

from app.services.video_processor import VideoProcessor

router = APIRouter()
logger = logging.getLogger(__name__)

# Instancia del procesador de video (singleton)
_video_processor = None


def get_video_processor() -> VideoProcessor:
    """Obtiene instancia singleton del procesador de video"""
    global _video_processor
    if _video_processor is None:
        _video_processor = VideoProcessor()
        logger.info("VideoProcessor inicializado")
    return _video_processor


@router.post("/process-video")
async def process_video(
    file: UploadFile = File(...),
    detect_faces: bool = Form(True),
    detect_plates: bool = Form(True),
    anonymization_method: str = Form("blur"),
    blur_kernel_size: int = Form(51),
    pixelate_blocks: int = Form(10)
):
    """
    Procesa un video aplicando detección y anonimización

    Args:
        file: Archivo de video (MP4, AVI, MOV)
        detect_faces: Si detectar rostros
        detect_plates: Si detectar matrículas
        anonymization_method: Método de anonimización (blur, pixelate, mask)
        blur_kernel_size: Tamaño kernel para blur (impar, ej: 51)
        pixelate_blocks: Número de bloques para pixelate (ej: 10)

    Returns:
        FileResponse con el video procesado
    """
    logger.info(f"Recibida solicitud de procesamiento de video: {file.filename}")
    logger.info(f"Detectar rostros: {detect_faces}, Detectar matrículas: {detect_plates}")
    logger.info(f"Método: {anonymization_method}")

    start_time = time.time()

    # Validar tipo de archivo
    allowed_extensions = ['.mp4', '.avi', '.mov', '.mkv']
    file_extension = Path(file.filename).suffix.lower()

    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de archivo no soportado. Permitidos: {', '.join(allowed_extensions)}"
        )

    # Crear archivos temporales
    temp_input = tempfile.NamedTemporaryFile(delete=False, suffix=file_extension)
    temp_output = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')

    try:
        # Guardar video subido
        content = await file.read()
        temp_input.write(content)
        temp_input.close()

        logger.info(f"Video guardado temporalmente: {temp_input.name}")

        # Obtener procesador
        processor = get_video_processor()

        # Obtener info del video
        video_info = processor.get_video_info(temp_input.name)
        logger.info(f"Info del video: {video_info}")

        # Procesar video
        result = processor.process_video(
            video_path=temp_input.name,
            output_path=temp_output.name,
            detect_faces=detect_faces,
            detect_plates=detect_plates,
            anonymization_method=anonymization_method,
            blur_kernel_size=blur_kernel_size,
            pixelate_blocks=pixelate_blocks
        )

        processing_time = time.time() - start_time
        logger.info(f"Video procesado en {processing_time:.2f}s")

        # Preparar respuesta
        output_filename = f"anonymized_{Path(file.filename).stem}.mp4"

        return FileResponse(
            path=temp_output.name,
            media_type="video/mp4",
            filename=output_filename,
            headers={
                "X-Processing-Time": str(round(processing_time, 2)),
                "X-Total-Faces": str(result['stats']['total_faces']),
                "X-Total-Plates": str(result['stats']['total_plates']),
                "X-Frames-Processed": str(result['stats']['frames_processed']),
                "X-Frames-With-Detections": str(result['stats']['frames_with_detections'])
            }
        )

    except Exception as e:
        logger.error(f"Error procesando video: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # Limpiar archivo de entrada
        try:
            if os.path.exists(temp_input.name):
                os.unlink(temp_input.name)
        except Exception as e:
            logger.warning(f"No se pudo eliminar archivo temporal: {e}")


@router.post("/video-info")
async def get_video_info(file: UploadFile = File(...)):
    """
    Obtiene información de un video sin procesarlo

    Args:
        file: Archivo de video

    Returns:
        JSON con información del video (fps, frames, dimensiones, duración)
    """
    logger.info(f"Obteniendo info de video: {file.filename}")

    # Validar extensión
    allowed_extensions = ['.mp4', '.avi', '.mov', '.mkv']
    file_extension = Path(file.filename).suffix.lower()

    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de archivo no soportado. Permitidos: {', '.join(allowed_extensions)}"
        )

    # Crear archivo temporal
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=file_extension)

    try:
        # Guardar video
        content = await file.read()
        temp_file.write(content)
        temp_file.close()

        # Obtener info
        processor = get_video_processor()
        info = processor.get_video_info(temp_file.name)

        return {
            'success': True,
            'filename': file.filename,
            'info': info
        }

    except Exception as e:
        logger.error(f"Error obteniendo info del video: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        try:
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)
        except Exception as e:
            logger.warning(f"No se pudo eliminar archivo temporal: {e}")


@router.websocket("/ws/process-video")
async def websocket_process_video(websocket: WebSocket):
    """
    WebSocket endpoint para procesamiento de video con actualizaciones en tiempo real

    El cliente debe enviar:
    {
        "video_data": "base64_encoded_video",
        "filename": "video.mp4",
        "detect_faces": true,
        "detect_plates": true,
        "anonymization_method": "blur",
        "blur_kernel_size": 51,
        "pixelate_blocks": 10
    }

    El servidor enviará actualizaciones de progreso:
    {
        "type": "progress",
        "frame": 45,
        "total_frames": 300,
        "progress_percent": 15.0,
        "faces_in_frame": 2,
        "plates_in_frame": 1
    }

    Y resultado final:
    {
        "type": "complete",
        "result": {...}
    }
    """
    await websocket.accept()
    logger.info("WebSocket conectado para procesamiento de video")

    temp_input = None
    temp_output = None

    try:
        # Recibir datos del video
        data = await websocket.receive_json()

        logger.info(f"Recibidos datos por WebSocket: {data.get('filename')}")

        # Extraer parámetros
        video_base64 = data.get('video_data')
        filename = data.get('filename', 'video.mp4')
        detect_faces = data.get('detect_faces', True)
        detect_plates = data.get('detect_plates', True)
        anonymization_method = data.get('anonymization_method', 'blur')
        blur_kernel_size = data.get('blur_kernel_size', 51)
        pixelate_blocks = data.get('pixelate_blocks', 10)
        enable_preview = data.get('enable_preview', True) 
        if not video_base64:
            await websocket.send_json({
                'type': 'error',
                'message': 'No se recibió video_data'
            })
            return

        # Decodificar video base64
        import base64
        video_bytes = base64.b64decode(video_base64)

        # Crear archivos temporales
        file_extension = Path(filename).suffix or '.mp4'
        temp_input = tempfile.NamedTemporaryFile(delete=False, suffix=file_extension)
        temp_output = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')

        temp_input.write(video_bytes)
        temp_input.close()

        # Enviar confirmación
        await websocket.send_json({
            'type': 'info',
            'message': 'Video recibido, iniciando procesamiento...'
        })

        # Obtener procesador
        processor = get_video_processor()

        # Procesar con streaming
        result = await processor.process_video_stream(
            video_path=temp_input.name,
            output_path=temp_output.name,
            websocket=websocket,
            detect_faces=detect_faces,
            detect_plates=detect_plates,
            anonymization_method=anonymization_method,
            blur_kernel_size=blur_kernel_size,
            pixelate_blocks=pixelate_blocks,
            send_preview_frames=enable_preview
        )

        # Dar tiempo a que todos los mensajes de progreso se envíen
        await asyncio.sleep(1.0)

        # Leer video procesado
        with open(temp_output.name, 'rb') as f:
            processed_video = f.read()

        # Enviar video procesado (en chunks si es muy grande)
        processed_base64 = base64.b64encode(processed_video).decode('utf-8')

        await websocket.send_json({
            'type': 'video',
            'video_data': processed_base64,
            'stats': result['stats']
        })

        logger.info("Procesamiento completado y enviado por WebSocket")

    except WebSocketDisconnect:
        logger.info("Cliente desconectado")

    except Exception as e:
        logger.error(f"Error en WebSocket: {e}", exc_info=True)
        try:
            await websocket.send_json({
                'type': 'error',
                'message': str(e)
            })
        except:
            pass

    finally:
        # Limpiar archivos temporales
        try:
            if temp_input and os.path.exists(temp_input.name):
                os.unlink(temp_input.name)
            if temp_output and os.path.exists(temp_output.name):
                os.unlink(temp_output.name)
        except Exception as e:
            logger.warning(f"No se pudo eliminar archivos temporales: {e}")
