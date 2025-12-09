"""
Script para crear un dataset unificado combinando rostros y matriculas.

Combina los datasets de faces_yolo y plates_yolo en un solo dataset
con 2 clases: face (clase 0) y plate (clase 1).
"""

import os
import shutil
from pathlib import Path
from typing import List
import random


def combine_datasets(faces_dir: Path, plates_dir: Path, output_dir: Path):
    """
    Combina datasets de rostros y matriculas en uno solo.

    Args:
        faces_dir: Directorio del dataset de rostros
        plates_dir: Directorio del dataset de matriculas
        output_dir: Directorio de salida para dataset combinado
    """
    print("=" * 60)
    print("CREACION DE DATASET UNIFICADO (FACES + PLATES)")
    print("=" * 60)
    print()

    # Crear estructura de directorios
    for split in ['train', 'valid', 'test']:
        (output_dir / 'images' / split).mkdir(parents=True, exist_ok=True)
        (output_dir / 'labels' / split).mkdir(parents=True, exist_ok=True)

    total_images = 0
    total_labels = 0

    for split in ['train', 'valid', 'test']:
        print(f"[INFO] Procesando split: {split}")

        # Copiar imagenes y labels de ROSTROS (clase 0 - sin cambios)
        faces_images_dir = faces_dir / 'images' / split
        faces_labels_dir = faces_dir / 'labels' / split

        if faces_images_dir.exists():
            face_images = list(faces_images_dir.glob('*.jpg'))
            print(f"  - Rostros: {len(face_images)} imagenes")

            for img_path in face_images:
                # Copiar imagen
                dst_img = output_dir / 'images' / split / img_path.name
                shutil.copy2(img_path, dst_img)
                total_images += 1

                # Copiar label (clase 0 ya esta correcta)
                label_name = img_path.stem + '.txt'
                label_path = faces_labels_dir / label_name

                if label_path.exists():
                    dst_label = output_dir / 'labels' / split / label_name
                    shutil.copy2(label_path, dst_label)
                    total_labels += 1

        # Copiar imagenes y labels de MATRICULAS (cambiar clase 0 -> 1)
        plates_images_dir = plates_dir / 'images' / split
        plates_labels_dir = plates_dir / 'labels' / split

        if plates_images_dir.exists():
            plate_images = list(plates_images_dir.glob('*.png'))
            print(f"  - Matriculas: {len(plate_images)} imagenes")

            for img_path in plate_images:
                # Copiar imagen
                dst_img = output_dir / 'images' / split / img_path.name
                shutil.copy2(img_path, dst_img)
                total_images += 1

                # Copiar y modificar label (cambiar clase 0 -> 1)
                label_name = img_path.stem + '.txt'
                label_path = plates_labels_dir / label_name

                if label_path.exists():
                    dst_label = output_dir / 'labels' / split / label_name

                    # Leer labels y cambiar clase 0 -> 1
                    with open(label_path, 'r') as f:
                        lines = f.readlines()

                    # Modificar clase en cada linea
                    new_lines = []
                    for line in lines:
                        parts = line.strip().split()
                        if len(parts) >= 5:
                            # Cambiar clase 0 -> 1
                            parts[0] = '1'
                            new_lines.append(' '.join(parts) + '\n')

                    # Guardar label modificado
                    with open(dst_label, 'w') as f:
                        f.writelines(new_lines)

                    total_labels += 1

        print()

    print("=" * 60)
    print("[OK] DATASET UNIFICADO CREADO")
    print("=" * 60)
    print()
    print(f"Total imagenes: {total_images}")
    print(f"Total labels: {total_labels}")
    print()
    print(f"Ubicacion: {output_dir}")
    print()
    print("Estructura del dataset:")
    for split in ['train', 'valid', 'test']:
        n_images = len(list((output_dir / 'images' / split).glob('*')))
        n_labels = len(list((output_dir / 'labels' / split).glob('*.txt')))
        print(f"  {split:6s}: {n_images} imagenes, {n_labels} labels")


def main():
    """Funcion principal."""
    # Configurar rutas
    project_root = Path(__file__).parent.parent
    datasets_root = project_root / 'datasets'

    faces_dir = datasets_root / 'faces_yolo'
    plates_dir = datasets_root / 'plates_yolo'
    output_dir = datasets_root / 'unified_yolo'

    # Verificar que existen los datasets
    if not faces_dir.exists():
        print(f"[ERROR] No se encontro dataset de rostros en {faces_dir}")
        print("Ejecuta primero: python scripts/prepare_datasets.py")
        return

    if not plates_dir.exists():
        print(f"[ERROR] No se encontro dataset de matriculas en {plates_dir}")
        print("Ejecuta primero: python scripts/prepare_datasets.py")
        return

    # Combinar datasets
    combine_datasets(faces_dir, plates_dir, output_dir)

    # Crear data.yaml
    data_yaml_path = output_dir / 'data.yaml'
    data_yaml_content = f"""# YOLOv8 Dataset Configuration - Unified (Faces + Plates)
# Total images: 2637 (train: 1845, valid: 526, test: 266)

# Rutas relativas al directorio del proyecto
path: ../datasets/unified_yolo  # Ruta raiz del dataset
train: images/train  # Ruta a imagenes de entrenamiento
val: images/valid    # Ruta a imagenes de validacion
test: images/test    # Ruta a imagenes de test

# Clases
nc: 2  # Numero de clases
names:
  0: face   # Clase 0: rostro humano
  1: plate  # Clase 1: matricula de vehiculo
"""

    with open(data_yaml_path, 'w') as f:
        f.write(data_yaml_content)

    print(f"[OK] Archivo data.yaml creado en: {data_yaml_path}")
    print()
    print("Proximo paso:")
    print("  python scripts/train_unified_model.py")


if __name__ == '__main__':
    main()
