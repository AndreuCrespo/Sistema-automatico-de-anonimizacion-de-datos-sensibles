"""
Script para evaluar modelos entrenados.

Calcula metricas de rendimiento (Precision, Recall, F1, mAP) en el conjunto de test.
"""

import argparse
from pathlib import Path
from ultralytics import YOLO
import json


def evaluate_model(model_type: str):
    """
    Evalua un modelo entrenado.

    Args:
        model_type: Tipo de modelo ('face' o 'plate')
    """
    print("=" * 60)
    print(f"EVALUACION DEL MODELO: {model_type.upper()}")
    print("=" * 60)
    print()

    # Configurar rutas
    project_root = Path(__file__).parent.parent
    models_dir = project_root / 'models' / 'trained'

    if model_type == 'face':
        model_path = models_dir / 'face_detector.pt'
        data_yaml = project_root / 'datasets' / 'faces_yolo' / 'data.yaml'
    elif model_type == 'plate':
        model_path = models_dir / 'plate_detector.pt'
        data_yaml = project_root / 'datasets' / 'plates_yolo' / 'data.yaml'
    else:
        print(f"[ERROR] Tipo de modelo invalido: {model_type}")
        print("Usa: 'face' o 'plate'")
        return

    # Verificar que existe el modelo
    if not model_path.exists():
        print(f"[ERROR] Modelo no encontrado en {model_path}")
        print(f"Entrena primero: python scripts/train_{model_type}_detector.py")
        return

    # Verificar que existe el dataset
    if not data_yaml.exists():
        print(f"[ERROR] Dataset no encontrado en {data_yaml}")
        print("Ejecuta primero: python scripts/prepare_datasets.py")
        return

    # Cargar modelo entrenado
    print(f"[INFO] Cargando modelo desde {model_path}")
    model = YOLO(str(model_path))
    print("[OK] Modelo cargado")
    print()

    # Evaluar en conjunto de test
    print("[INFO] Evaluando en conjunto de test...")
    print("=" * 60)

    metrics = model.val(
        data=str(data_yaml),
        split='test',
        plots=True,
        save_json=True,
        verbose=True
    )

    print()
    print("=" * 60)
    print("[OK] EVALUACION COMPLETADA")
    print("=" * 60)
    print()

    # Mostrar metricas
    print("METRICAS DE RENDIMIENTO:")
    print("-" * 60)

    # Precision, Recall, mAP
    precision = metrics.box.p[0] if hasattr(metrics.box, 'p') else metrics.box.mp
    recall = metrics.box.r[0] if hasattr(metrics.box, 'r') else metrics.box.mr
    map50 = metrics.box.map50
    map75 = metrics.box.map75
    map = metrics.box.map

    print(f"Precision:     {precision:.4f}")
    print(f"Recall:        {recall:.4f}")
    print(f"F1-Score:      {2 * (precision * recall) / (precision + recall):.4f}")
    print(f"mAP@0.5:       {map50:.4f}")
    print(f"mAP@0.75:      {map75:.4f}")
    print(f"mAP@0.5:0.95:  {map:.4f}")
    print("-" * 60)

    # Guardar metricas en archivo JSON
    output_file = project_root / 'outputs' / f'{model_type}_metrics.json'
    output_file.parent.mkdir(parents=True, exist_ok=True)

    metrics_dict = {
        'model_type': model_type,
        'model_path': str(model_path),
        'precision': float(precision),
        'recall': float(recall),
        'f1_score': float(2 * (precision * recall) / (precision + recall)),
        'map50': float(map50),
        'map75': float(map75),
        'map': float(map)
    }

    with open(output_file, 'w') as f:
        json.dump(metrics_dict, f, indent=4)

    print()
    print(f"[OK] Metricas guardadas en: {output_file}")
    print()

    # Verificar si cumple con los objetivos del TFM
    print("VERIFICACION DE OBJETIVOS:")
    print("-" * 60)

    if model_type == 'face':
        target_f1 = 0.85
        current_f1 = 2 * (precision * recall) / (precision + recall)
        print(f"Objetivo F1-Score: >= {target_f1}")
        print(f"F1-Score obtenido: {current_f1:.4f}")

        if current_f1 >= target_f1:
            print("[OK] OBJETIVO CUMPLIDO!")
        else:
            print(f"[WARNING] No se alcanzo el objetivo (falta {target_f1 - current_f1:.4f})")

    elif model_type == 'plate':
        target_f1 = 0.82
        current_f1 = 2 * (precision * recall) / (precision + recall)
        print(f"Objetivo F1-Score: >= {target_f1}")
        print(f"F1-Score obtenido: {current_f1:.4f}")

        if current_f1 >= target_f1:
            print("[OK] OBJETIVO CUMPLIDO!")
        else:
            print(f"[WARNING] No se alcanzo el objetivo (falta {target_f1 - current_f1:.4f})")

    print("-" * 60)


def main():
    """Funcion principal."""
    parser = argparse.ArgumentParser(
        description='Evalua modelos entrenados de deteccion'
    )
    parser.add_argument(
        '--model',
        type=str,
        choices=['face', 'plate'],
        required=True,
        help='Tipo de modelo a evaluar (face o plate)'
    )

    args = parser.parse_args()
    evaluate_model(args.model)


if __name__ == '__main__':
    main()
