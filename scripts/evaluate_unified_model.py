"""
Script para evaluar el modelo unificado en el conjunto de test.

Genera métricas detalladas por clase y globales.
"""

import os
from pathlib import Path
from ultralytics import YOLO
import torch
import json


def evaluate_unified_model():
    """Evalúa el modelo unificado en el conjunto de test."""
    print("=" * 60)
    print("EVALUACIÓN DEL MODELO UNIFICADO")
    print("=" * 60)
    print()

    # Configurar rutas
    project_root = Path(__file__).parent.parent
    model_path = project_root / 'models' / 'trained' / 'unified_detector.pt'
    data_yaml = project_root / 'datasets' / 'unified_yolo' / 'data.yaml'
    output_dir = project_root / 'models' / 'evaluation'
    output_dir.mkdir(parents=True, exist_ok=True)

    # Verificar que existe el modelo
    if not model_path.exists():
        print(f"[ERROR] No se encontró el modelo en {model_path}")
        print("Ejecuta primero: python scripts/train_unified_model.py")
        return

    # Verificar GPU
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"[INFO] Dispositivo: {device}")
    if device == 'cuda':
        print(f"[INFO] GPU: {torch.cuda.get_device_name(0)}")
    print()

    # Cargar modelo
    print(f"[INFO] Cargando modelo desde {model_path}")
    model = YOLO(str(model_path))
    print("[OK] Modelo cargado")
    print()

    # Evaluar en conjunto de test
    print("[INFO] Evaluando en conjunto de test...")
    print("=" * 60)

    try:
        results = model.val(
            data=str(data_yaml),
            split='test',  # Evaluar en test set
            device=device,
            batch=16,
            imgsz=640,
            plots=True,
            save_json=True,
            project=str(output_dir.parent),
            name='evaluation'
        )

        print()
        print("=" * 60)
        print("[OK] EVALUACIÓN COMPLETADA")
        print("=" * 60)
        print()

        # Extraer métricas
        metrics = {
            'model': str(model_path),
            'dataset': 'unified_yolo',
            'test_split': 'test (266 images)',
            'device': device,
            'global_metrics': {},
            'per_class_metrics': {}
        }

        # Métricas globales
        if hasattr(results, 'box'):
            box = results.box
            metrics['global_metrics'] = {
                'mAP50': float(box.map50) if hasattr(box, 'map50') else 0.0,
                'mAP50-95': float(box.map) if hasattr(box, 'map') else 0.0,
                'precision': float(box.mp) if hasattr(box, 'mp') else 0.0,
                'recall': float(box.mr) if hasattr(box, 'mr') else 0.0,
            }

            # Calcular F1-Score
            precision = metrics['global_metrics']['precision']
            recall = metrics['global_metrics']['recall']
            if precision > 0 and recall > 0:
                f1 = 2 * (precision * recall) / (precision + recall)
                metrics['global_metrics']['f1_score'] = float(f1)
            else:
                metrics['global_metrics']['f1_score'] = 0.0

            # Métricas por clase
            if hasattr(box, 'ap_class_index') and hasattr(box, 'ap50'):
                class_names = {0: 'face', 1: 'plate'}

                for idx, class_id in enumerate(box.ap_class_index):
                    class_name = class_names.get(int(class_id), f'class_{class_id}')

                    class_metrics = {
                        'mAP50': float(box.ap50[idx]) if idx < len(box.ap50) else 0.0,
                        'mAP50-95': float(box.ap[idx]) if idx < len(box.ap) else 0.0,
                    }

                    # Precisión y Recall por clase si están disponibles
                    if hasattr(box, 'p') and idx < len(box.p):
                        class_metrics['precision'] = float(box.p[idx])
                    if hasattr(box, 'r') and idx < len(box.r):
                        class_metrics['recall'] = float(box.r[idx])

                    # F1-Score por clase
                    if 'precision' in class_metrics and 'recall' in class_metrics:
                        p = class_metrics['precision']
                        r = class_metrics['recall']
                        if p > 0 and r > 0:
                            class_metrics['f1_score'] = 2 * (p * r) / (p + r)
                        else:
                            class_metrics['f1_score'] = 0.0

                    metrics['per_class_metrics'][class_name] = class_metrics

        # Guardar métricas en JSON
        metrics_file = output_dir / 'test_metrics.json'
        with open(metrics_file, 'w', encoding='utf-8') as f:
            json.dump(metrics, f, indent=2, ensure_ascii=False)

        print(f"[OK] Métricas guardadas en: {metrics_file}")
        print()

        # Mostrar métricas
        print("MÉTRICAS GLOBALES (Test Set):")
        print("-" * 60)
        for key, value in metrics['global_metrics'].items():
            print(f"  {key:20s}: {value:.4f}")
        print()

        if metrics['per_class_metrics']:
            print("MÉTRICAS POR CLASE:")
            print("-" * 60)
            for class_name, class_metrics in metrics['per_class_metrics'].items():
                print(f"\n  {class_name.upper()}:")
                for key, value in class_metrics.items():
                    print(f"    {key:20s}: {value:.4f}")
        print()

        # Verificación de objetivos del TFM
        print("VERIFICACIÓN DE OBJETIVOS DEL TFM:")
        print("-" * 60)

        face_f1 = metrics['per_class_metrics'].get('face', {}).get('f1_score', 0)
        plate_f1 = metrics['per_class_metrics'].get('plate', {}).get('f1_score', 0)
        global_f1 = metrics['global_metrics'].get('f1_score', 0)

        print(f"  Objetivo F1-Score rostros:     >= 0.85")
        print(f"  F1-Score rostros obtenido:        {face_f1:.4f} {'✓' if face_f1 >= 0.85 else '✗'}")
        print()
        print(f"  Objetivo F1-Score matrículas:  >= 0.82")
        print(f"  F1-Score matrículas obtenido:     {plate_f1:.4f} {'✓' if plate_f1 >= 0.82 else '✗'}")
        print()
        print(f"  F1-Score global:                  {global_f1:.4f}")
        print()

        if face_f1 >= 0.85 and plate_f1 >= 0.82:
            print("  [OK] ¡TODOS LOS OBJETIVOS CUMPLIDOS! 🎉")
        else:
            print("  [INFO] Algunos objetivos no alcanzados")
            if face_f1 < 0.85:
                print(f"        - Rostros: faltan {0.85 - face_f1:.4f} puntos")
            if plate_f1 < 0.82:
                print(f"        - Matrículas: faltan {0.82 - plate_f1:.4f} puntos")

        print()
        print("Gráficos de evaluación guardados en:")
        print(f"  {output_dir.parent / 'evaluation'}")
        print()
        print("Archivos generados:")
        print("  - confusion_matrix.png")
        print("  - BoxF1_curve.png")
        print("  - BoxPR_curve.png")
        print("  - predictions.json (predicciones detalladas)")

    except Exception as e:
        print()
        print(f"[ERROR] Error durante la evaluación: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    evaluate_unified_model()
