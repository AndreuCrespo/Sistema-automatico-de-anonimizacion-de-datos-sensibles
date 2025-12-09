"""
Script para crear un video de prueba simple
"""
import cv2
import numpy as np
from pathlib import Path

def create_test_video():
    """Crea un video de prueba corto para probar el sistema"""

    # Configuración
    output_path = Path(__file__).parent.parent / "test_video.mp4"
    width, height = 640, 480
    fps = 30
    duration_seconds = 3  # Video corto de 3 segundos
    total_frames = fps * duration_seconds

    # Crear video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))

    print(f"Creando video de prueba: {output_path}")
    print(f"Resolución: {width}x{height}")
    print(f"FPS: {fps}")
    print(f"Duración: {duration_seconds}s ({total_frames} frames)")

    for frame_num in range(total_frames):
        # Crear frame con fondo blanco
        frame = np.ones((height, width, 3), dtype=np.uint8) * 255

        # Añadir gradiente de color
        gradient = np.linspace(0, 255, width, dtype=np.uint8)
        frame[:, :, 0] = gradient  # Canal azul
        frame[:, :, 1] = 128  # Canal verde

        # Añadir círculo que se mueve
        center_x = int(width / 2 + 100 * np.sin(frame_num * 0.1))
        center_y = int(height / 2 + 50 * np.cos(frame_num * 0.15))
        cv2.circle(frame, (center_x, center_y), 30, (0, 255, 0), -1)

        # Añadir rectángulo que simula una "cara"
        face_x = int(width / 3 + 50 * np.cos(frame_num * 0.08))
        face_y = int(height / 3)
        cv2.rectangle(frame,
                     (face_x - 40, face_y - 50),
                     (face_x + 40, face_y + 50),
                     (255, 200, 200), -1)

        # Añadir "ojos" al rectángulo
        cv2.circle(frame, (face_x - 15, face_y - 10), 8, (0, 0, 0), -1)
        cv2.circle(frame, (face_x + 15, face_y - 10), 8, (0, 0, 0), -1)

        # Añadir texto simulando una "matrícula"
        plate_text = "ABC-1234"
        plate_x = int(2 * width / 3)
        plate_y = int(2 * height / 3)
        cv2.rectangle(frame,
                     (plate_x - 60, plate_y - 20),
                     (plate_x + 60, plate_y + 20),
                     (255, 255, 255), -1)
        cv2.rectangle(frame,
                     (plate_x - 60, plate_y - 20),
                     (plate_x + 60, plate_y + 20),
                     (0, 0, 0), 2)
        cv2.putText(frame, plate_text, (plate_x - 50, plate_y + 5),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

        # Añadir contador de frame
        cv2.putText(frame, f"Frame: {frame_num + 1}/{total_frames}",
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

        # Escribir frame
        out.write(frame)

        if (frame_num + 1) % 30 == 0:
            print(f"  Procesado {frame_num + 1}/{total_frames} frames...")

    out.release()
    print(f"\n✅ Video creado exitosamente: {output_path}")
    print(f"   Tamaño: {output_path.stat().st_size / 1024:.1f} KB")

    return str(output_path)

if __name__ == "__main__":
    create_test_video()
