"""
Script para entrenar el modelo unificado.
"""

import os
from pathlib import Path
from ultralytics import YOLO
import torch


def train_unified_model():
    """Entrena el modelo unificado de deteccion."""
    print("=" * 60)
    print("ENTRENAMIENTO DEL MODELO UNIFICADO (FACES + PLATES)")
    print("=" * 60)
    print()

    # Configurar rutas
    project_root = Path(__file__).parent.parent
    data_yaml = project_root / 'datasets' / 'unified_yolo' / 'data.yaml'
    output_dir = project_root / 'models' / 'trained'
    output_dir.mkdir(parents=True, exist_ok=True)

    # Verificar GPU disponible
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"[INFO] Dispositivo: {device}")
    if device == 'cuda':
        print(f"[INFO] GPU: {torch.cuda.get_device_name(0)}")
    print()

    # Cargar modelo base
    print("[INFO] Cargando YOLOv8n...")
    model = YOLO('yolov8n.pt')
    print("[OK] Modelo cargado")
    print()

    # Configurar parametros
    epochs = 100
    batch_size = 16
    img_size = 640
    patience = 20

    print(f"[INFO] Configuracion:")
    print(f"  - Epochs: {epochs}, Batch: {batch_size}, Size: {img_size}")
    print(f"  - Device: {device}, Patience: {patience}")
    print()
    print("[INFO] Iniciando entrenamiento...")
    print("=" * 60)

    # Entrenar
    results = model.train(
        data=str(data_yaml),
        epochs=epochs,
        batch=batch_size,
        imgsz=img_size,
        patience=patience,
        device=device,
        project=str(output_dir.parent),
        name='unified_training',
        exist_ok=True,
        pretrained=True,
        optimizer='AdamW',
        lr0=0.001,
        verbose=True,
        plots=True,
        save=True,
        save_period=10,
        workers=8,
        val=True,
        amp=True
    )

    print()
    print("=" * 60)
    print("[OK] ENTRENAMIENTO COMPLETADO")
    print("=" * 60)
    print()

    # Copiar mejor modelo
    best_model_path = output_dir.parent / 'unified_training' / 'weights' / 'best.pt'
    final_model_path = output_dir / 'unified_detector.pt'

    if best_model_path.exists():
        import shutil
        shutil.copy2(best_model_path, final_model_path)
        print(f"[OK] Modelo guardado: {final_model_path}")

    print()
    print("Metricas finales:")
    if hasattr(results, 'results_dict'):
        metrics = results.results_dict
        map50 = metrics.get('metrics/mAP50(B)', 0)
        map95 = metrics.get('metrics/mAP50-95(B)', 0)
        precision = metrics.get('metrics/precision(B)', 0)
        recall = metrics.get('metrics/recall(B)', 0)

        print(f"  - mAP50: {map50:.4f}")
        print(f"  - mAP50-95: {map95:.4f}")
        print(f"  - Precision: {precision:.4f}")
        print(f"  - Recall: {recall:.4f}")

        if precision > 0 and recall > 0:
            f1 = 2 * (precision * recall) / (precision + recall)
            print(f"  - F1-Score: {f1:.4f}")


if __name__ == '__main__':
    train_unified_model()
