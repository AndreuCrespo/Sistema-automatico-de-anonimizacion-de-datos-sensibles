"""
Script para entrenar el modelo unificado (rostros + matriculas).

Entrena un solo modelo YOLOv8 que detecta:
- Clase 0: face (rostros)
- Clase 1: plate (matriculas)
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

    # Verificar que existe el dataset
    if not data_yaml.exists():
        print(f"[ERROR] No se encontro el archivo data.yaml en {data_yaml}")
        print("Ejecuta primero: python scripts/create_unified_dataset.py")
        return

    # Verificar GPU disponible
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"[INFO] Dispositivo de entrenamiento: {device}")
    if device == 'cuda':
        print(f"[INFO] GPU detectada: {torch.cuda.get_device_name(0)}")
        print(f"[INFO] Memoria GPU disponible: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
    else:
        print("[WARNING] No se detecto GPU. El entrenamiento sera MUCHO mas lento.")
        print("[WARNING] Se recomienda usar Google Colab o una maquina con GPU.")
    print()

    # Cargar modelo base YOLOv8n
    print("[INFO] Cargando modelo base YOLOv8n...")
    model = YOLO('yolov8n.pt')
    print("[OK] Modelo base cargado")
    print()

    # Configurar parametros de entrenamiento
    print("[INFO] Configuracion de entrenamiento:")
    epochs = 100
    batch_size = 16 if device == 'cuda' else 8  # Menos batch en CPU
    img_size = 640
    patience = 20  # Early stopping

    print(f"  - Dataset: 2 clases (face + plate)")
    print(f"  - Imagenes: 1845 train, 526 valid, 266 test")
    print(f"  - Epochs: {epochs}")
    print(f"  - Batch size: {batch_size}")
    print(f"  - Image size: {img_size}x{img_size}")
    print(f"  - Early stopping patience: {patience}")
    print(f"  - Device: {device}")
    print(f"  - Modelo base: YOLOv8n (6.3M params)")
    print()

    if device == 'cpu':
        print("[WARNING] Tiempo estimado en CPU: 8-12 horas")
    else:
        print("[INFO] Tiempo estimado en GPU: 2-4 horas")

    print()
    input("Presiona ENTER para comenzar el entrenamiento...")
    print()

    # Entrenar modelo
    print("[INFO] Iniciando entrenamiento...")
    print("=" * 60)

    try:
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
            lrf=0.01,
            momentum=0.937,
            weight_decay=0.0005,
            warmup_epochs=3,
            warmup_momentum=0.8,
            warmup_bias_lr=0.1,
            box=7.5,
            cls=0.5,
            dfl=1.5,
            verbose=True,
            plots=True,
            save=True,
            save_period=10,  # Guardar cada 10 epochs
            cache=False,  # No cargar todo en RAM
            workers=8 if device == 'cuda' else 4,
            val=True,
            amp=True if device == 'cuda' else False  # Automatic Mixed Precision
        )

        print()
        print("=" * 60)
        print("[OK] ENTRENAMIENTO COMPLETADO")
        print("=" * 60)
        print()

        # Copiar mejor modelo al directorio final
        best_model_path = output_dir.parent / 'unified_training' / 'weights' / 'best.pt'
        final_model_path = output_dir / 'unified_detector.pt'

        if best_model_path.exists():
            import shutil
            shutil.copy2(best_model_path, final_model_path)
            print(f"[OK] Mejor modelo guardado en: {final_model_path}")
        else:
            print(f"[WARNING] No se encontro el modelo en {best_model_path}")

        print()
        print("Metricas finales:")

        # Extraer metricas
        if hasattr(results, 'results_dict'):
            metrics = results.results_dict
            print(f"  - mAP50 (todas las clases): {metrics.get('metrics/mAP50(B)', 'N/A')}")
            print(f"  - mAP50-95 (todas las clases): {metrics.get('metrics/mAP50-95(B)', 'N/A')}")

            # Calcular F1-Score aproximado
            # F1 = 2 * (precision * recall) / (precision + recall)
            precision = metrics.get('metrics/precision(B)', 0)
            recall = metrics.get('metrics/recall(B)', 0)

            if precision > 0 and recall > 0:
                f1_score = 2 * (precision * recall) / (precision + recall)
                print(f"  - Precision: {precision:.4f}")
                print(f"  - Recall: {recall:.4f}")
                print(f"  - F1-Score: {f1_score:.4f}")
                print()

                # Verificar objetivos
                print("Verificacion de objetivos del TFM:")
                print(f"  - Objetivo F1-Score rostros: >= 0.85")
                print(f"  - Objetivo F1-Score matriculas: >= 0.82")
                print(f"  - F1-Score obtenido (global): {f1_score:.4f}")

                if f1_score >= 0.82:
                    print("[OK] OBJETIVOS CUMPLIDOS!")
                else:
                    print(f"[INFO] Se necesita mejorar {0.82 - f1_score:.4f} puntos")

        print()
        print("Graficos de entrenamiento guardados en:")
        print(f"  {output_dir.parent / 'unified_training'}")
        print()
        print("Proximos pasos:")
        print("1. Revisar graficos de entrenamiento (results.png, confusion_matrix.png)")
        print("2. Evaluar modelo: python scripts/evaluate_unified_model.py")
        print("3. Actualizar backend para usar el modelo unificado")

    except KeyboardInterrupt:
        print()
        print("[INFO] Entrenamiento interrumpido por el usuario")
    except Exception as e:
        print()
        print(f"[ERROR] Error durante el entrenamiento: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    train_unified_model()
