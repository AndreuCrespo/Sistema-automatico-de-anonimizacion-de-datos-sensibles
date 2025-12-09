"""
Script para entrenar el detector de rostros con YOLOv8.

Realiza fine-tuning del modelo YOLOv8n con el dataset de rostros.
Guarda el mejor modelo entrenado en models/trained/face_detector.pt
"""

import os
from pathlib import Path
from ultralytics import YOLO
import torch


def train_face_detector():
    """Entrena el modelo de deteccion de rostros."""
    print("=" * 60)
    print("ENTRENAMIENTO DEL DETECTOR DE ROSTROS")
    print("=" * 60)
    print()

    # Configurar rutas
    project_root = Path(__file__).parent.parent
    data_yaml = project_root / 'datasets' / 'faces_yolo' / 'data.yaml'
    output_dir = project_root / 'models' / 'trained'
    output_dir.mkdir(parents=True, exist_ok=True)

    # Verificar que existe el dataset
    if not data_yaml.exists():
        print(f"[ERROR] No se encontro el archivo data.yaml en {data_yaml}")
        print("Ejecuta primero: python scripts/prepare_datasets.py")
        return

    # Verificar GPU disponible
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"[INFO] Dispositivo de entrenamiento: {device}")
    if device == 'cuda':
        print(f"[INFO] GPU detectada: {torch.cuda.get_device_name(0)}")
    print()

    # Cargar modelo base YOLOv8n
    print("[INFO] Cargando modelo base YOLOv8n...")
    model = YOLO('yolov8n.pt')
    print("[OK] Modelo base cargado")
    print()

    # Configurar parametros de entrenamiento
    print("[INFO] Configuracion de entrenamiento:")
    epochs = 100
    batch_size = 16
    img_size = 640
    patience = 20  # Early stopping

    print(f"  - Epochs: {epochs}")
    print(f"  - Batch size: {batch_size}")
    print(f"  - Image size: {img_size}x{img_size}")
    print(f"  - Early stopping patience: {patience}")
    print(f"  - Device: {device}")
    print()

    # Entrenar modelo
    print("[INFO] Iniciando entrenamiento...")
    print("=" * 60)

    results = model.train(
        data=str(data_yaml),
        epochs=epochs,
        batch=batch_size,
        imgsz=img_size,
        patience=patience,
        device=device,
        project=str(output_dir.parent),
        name='face_training',
        exist_ok=True,
        pretrained=True,
        optimizer='AdamW',
        lr0=0.001,
        verbose=True,
        plots=True,
        save=True,
        save_period=10,  # Guardar cada 10 epochs
    )

    print()
    print("=" * 60)
    print("[OK] ENTRENAMIENTO COMPLETADO")
    print("=" * 60)
    print()

    # Copiar mejor modelo al directorio final
    best_model_path = output_dir.parent / 'face_training' / 'weights' / 'best.pt'
    final_model_path = output_dir / 'face_detector.pt'

    if best_model_path.exists():
        import shutil
        shutil.copy2(best_model_path, final_model_path)
        print(f"[OK] Mejor modelo guardado en: {final_model_path}")
    else:
        print(f"[WARNING] No se encontro el modelo en {best_model_path}")

    print()
    print("Metricas finales:")
    print(f"  - mAP50: {results.results_dict.get('metrics/mAP50(B)', 'N/A')}")
    print(f"  - mAP50-95: {results.results_dict.get('metrics/mAP50-95(B)', 'N/A')}")
    print()
    print("Proximos pasos:")
    print("1. Revisar graficos de entrenamiento en models/face_training/")
    print("2. Evaluar el modelo: python scripts/evaluate_model.py --model face")
    print("3. Entrenar detector de matriculas: python scripts/train_plate_detector.py")


if __name__ == '__main__':
    train_face_detector()
