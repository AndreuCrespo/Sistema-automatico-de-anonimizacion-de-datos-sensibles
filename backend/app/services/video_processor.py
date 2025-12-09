"""
Video Processor Service
Procesa videos frame por frame con detección y anonimización
Soporta streaming en tiempo real via WebSocket
"""

import cv2
import numpy as np
from typing import Dict, List, Optional, Callable
import logging
from pathlib import Path
import tempfile
import os
import base64

from app.models.unified_detector import UnifiedDetector
from app.models.face_detector import FaceDetector
from app.models.plate_detector import PlateDetector
from app.services.anonymizer import Anonymizer

logger = logging.getLogger(__name__)


class VideoProcessor:
    """
    Procesa videos frame por frame aplicando detección y anonimización
    """

    def __init__(self):
        """Inicializa el procesador de video"""
        # Intentar cargar detector unificado, sino usar detectores separados
        self.unified_detector = None
        try:
            self.unified_detector = UnifiedDetector()
            logger.info("Usando detector unificado para videos")
        except Exception as e:
            logger.warning(f"No se pudo cargar detector unificado: {e}")
            self.face_detector = FaceDetector()
            self.plate_detector = PlateDetector()
            logger.info("Usando detectores separados para videos")

        self.anonymizer = Anonymizer()

    def get_video_info(self, video_path: str) -> Dict:
        """
        Obtiene información del video

        Args:
            video_path: Ruta al archivo de video

        Returns:
            Dict con información del video (fps, frames, dimensiones, duración)
        """
        try:
            cap = cv2.VideoCapture(video_path)

            if not cap.isOpened():
                raise ValueError(f"No se pudo abrir el video: {video_path}")

            fps = int(cap.get(cv2.CAP_PROP_FPS))
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration_seconds = frame_count / fps if fps > 0 else 0

            cap.release()

            info = {
                'fps': fps,
                'frame_count': frame_count,
                'width': width,
                'height': height,
                'duration_seconds': round(duration_seconds, 2),
                'duration_formatted': self._format_duration(duration_seconds)
            }

            logger.info(f"Video info: {info}")
            return info

        except Exception as e:
            logger.error(f"Error obteniendo información del video: {e}")
            raise

    def _format_duration(self, seconds: float) -> str:
        """Formatea duración en HH:MM:SS"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)

        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"

    def process_video(
        self,
        video_path: str,
        output_path: str,
        detect_faces: bool = True,
        detect_plates: bool = True,
        anonymization_method: str = "blur",
        blur_kernel_size: int = 51,
        pixelate_blocks: int = 10,
        callback: Optional[Callable[[int, int, Dict], None]] = None
    ) -> Dict:
        """
        Procesa un video completo frame por frame

        Args:
            video_path: Ruta al video de entrada
            output_path: Ruta para guardar video procesado
            detect_faces: Si detectar rostros
            detect_plates: Si detectar matrículas
            anonymization_method: Método de anonimización (blur, pixelate, mask)
            blur_kernel_size: Tamaño kernel para blur
            pixelate_blocks: Número de bloques para pixelate
            callback: Función callback para progreso (frame_actual, total_frames, stats)

        Returns:
            Dict con estadísticas del procesamiento
        """
        logger.info(f"Iniciando procesamiento de video: {video_path}")
        logger.info(f"Método anonimización: {anonymization_method}")

        try:
            # Abrir video de entrada
            cap = cv2.VideoCapture(video_path)

            if not cap.isOpened():
                raise ValueError(f"No se pudo abrir el video: {video_path}")

            # Obtener propiedades del video
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

            # Configurar video de salida
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

            # Estadísticas
            stats = {
                'total_faces': 0,
                'total_plates': 0,
                'frames_processed': 0,
                'frames_with_detections': 0
            }

            frame_number = 0

            # Procesar frame por frame
            while True:
                ret, frame = cap.read()

                if not ret:
                    break

                frame_number += 1

                # Detectar objetos en el frame
                detections = self._detect_in_frame(frame, detect_faces, detect_plates)

                faces = detections['faces']
                plates = detections['plates']

                # Actualizar estadísticas
                stats['total_faces'] += len(faces)
                stats['total_plates'] += len(plates)
                stats['frames_processed'] += 1

                if len(faces) > 0 or len(plates) > 0:
                    stats['frames_with_detections'] += 1

                # Anonimizar frame
                if faces or plates:
                    # Combinar todas las detecciones en una sola lista
                    all_boxes = faces + plates

                    # Preparar kwargs según el método
                    kwargs = {}
                    if anonymization_method == 'blur':
                        kwargs['kernel_size'] = blur_kernel_size
                    elif anonymization_method == 'pixelate':
                        kwargs['blocks'] = pixelate_blocks

                    frame = self.anonymizer.anonymize(
                        frame,
                        all_boxes,
                        method=anonymization_method,
                        **kwargs
                    )

                # Escribir frame procesado
                out.write(frame)

                # Callback de progreso (enviar frame cada 3 frames para no saturar el WebSocket)
                if callback:
                    # Codificar frame si es cada 3 frames
                    frame_base64 = None
                    if frame_number % 3 == 0:
                        # Codificar frame procesado a JPEG
                        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                        frame_base64 = buffer.tobytes()

                    callback(frame_number, total_frames, {
                        'faces_in_frame': len(faces),
                        'plates_in_frame': len(plates),
                        'frame_data': frame_base64
                    })

                # Log cada 10% de progreso
                if frame_number % max(1, total_frames // 10) == 0:
                    progress = (frame_number / total_frames) * 100
                    logger.info(f"Progreso: {progress:.1f}% ({frame_number}/{total_frames})")

            # Cerrar archivos
            cap.release()
            out.release()

            logger.info(f"Video procesado correctamente: {output_path}")
            logger.info(f"Estadísticas: {stats}")

            return {
                'success': True,
                'output_path': output_path,
                'stats': stats,
                'video_info': {
                    'fps': fps,
                    'width': width,
                    'height': height,
                    'total_frames': total_frames
                }
            }

        except Exception as e:
            logger.error(f"Error procesando video: {e}", exc_info=True)
            raise

        finally:
            if 'cap' in locals():
                cap.release()
            if 'out' in locals():
                out.release()

    def _detect_in_frame(
        self,
        frame: np.ndarray,
        detect_faces: bool,
        detect_plates: bool
    ) -> Dict[str, List]:
        """
        Detecta objetos en un frame

        Args:
            frame: Frame a procesar
            detect_faces: Si detectar rostros
            detect_plates: Si detectar matrículas

        Returns:
            Dict con listas de bounding boxes para faces y plates
        """
        # Usar detector unificado si está disponible
        if self.unified_detector is not None:
            detections = self.unified_detector.detect(
                frame,
                detect_faces=detect_faces,
                detect_plates=detect_plates
            )

            # Convertir formato (x1, y1, x2, y2, conf) -> (x1, y1, x2, y2)
            faces = [(x1, y1, x2, y2) for x1, y1, x2, y2, _ in detections['faces']]
            plates = [(x1, y1, x2, y2) for x1, y1, x2, y2, _ in detections['plates']]

        else:
            # Usar detectores separados
            faces = []
            plates = []

            if detect_faces:
                faces = self.face_detector.detect(frame)

            if detect_plates:
                plates = self.plate_detector.detect(frame)

        return {'faces': faces, 'plates': plates}

    async def process_video_stream(
        self,
        video_path: str,
        output_path: str,
        websocket,
        detect_faces: bool = True,
        detect_plates: bool = True,
        anonymization_method: str = "blur",
        blur_kernel_size: int = 51,
        pixelate_blocks: int = 10,
        send_preview_frames: bool = True
    ) -> Dict:
        """
        Procesa video con streaming de progreso via WebSocket

        Args:
            video_path: Ruta al video de entrada
            output_path: Ruta para guardar video procesado
            websocket: WebSocket para enviar actualizaciones
            detect_faces: Si detectar rostros
            detect_plates: Si detectar matrículas
            anonymization_method: Método de anonimización
            blur_kernel_size: Tamaño kernel para blur
            pixelate_blocks: Número de bloques para pixelate
            send_preview_frames: Si enviar frames de preview en tiempo real

        Returns:
            Dict con estadísticas del procesamiento
        """
        import asyncio
        import concurrent.futures

        # Obtener el loop actual para usarlo desde el thread del procesamiento
        loop = asyncio.get_running_loop()
        
        # Queue para comunicar mensajes de progreso
        progress_queue = asyncio.Queue()
        
        async def send_progress_messages():
            """Tarea async que envía mensajes de progreso desde la queue"""
            while True:
                try:
                    message = await asyncio.wait_for(progress_queue.get(), timeout=0.1)
                    if message is None:  # Señal de terminación
                        break
                    await websocket.send_json(message)
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    logger.warning(f"Error enviando progreso: {e}")
                    break

        def sync_callback(frame_number: int, total_frames: int, frame_stats: Dict):
            """Callback sincrónico que encola mensajes de progreso"""
            try:
                progress_data = {
                    'type': 'progress',
                    'frame': frame_number,
                    'total_frames': total_frames,
                    'progress_percent': round((frame_number / total_frames) * 100, 2),
                    'faces_in_frame': frame_stats.get('faces_in_frame', 0),
                    'plates_in_frame': frame_stats.get('plates_in_frame', 0)
                }

                # Agregar frame si preview está activado
                if send_preview_frames and frame_stats.get('frame_data') is not None:
                    frame_base64 = base64.b64encode(frame_stats['frame_data']).decode('utf-8')
                    progress_data['current_frame'] = frame_base64

                # Encolar mensaje
                asyncio.run_coroutine_threadsafe(
                    progress_queue.put(progress_data),
                    loop
                )
            except Exception as e:
                logger.warning(f"Error en callback de progreso: {e}")

        # Iniciar tarea de envío de mensajes
        sender_task = asyncio.create_task(send_progress_messages())

        try:
            # Ejecutar procesamiento en thread pool
            with concurrent.futures.ThreadPoolExecutor() as executor:
                result = await loop.run_in_executor(
                    executor,
                    lambda: self.process_video(
                        video_path=video_path,
                        output_path=output_path,
                        detect_faces=detect_faces,
                        detect_plates=detect_plates,
                        anonymization_method=anonymization_method,
                        blur_kernel_size=blur_kernel_size,
                        pixelate_blocks=pixelate_blocks,
                        callback=sync_callback
                    )
                )
        finally:
            # Finalizar sender task
            await progress_queue.put(None)
            await sender_task

        return result

