"""
Script para preparar y convertir datasets a formato YOLO.

Convierte:
- CSV de faces (x0,y0,x1,y1) → YOLO (class x_center y_center width height)
- XML de plates (Pascal VOC) → YOLO

Organiza en estructura train/valid/test (70%/20%/10%)
"""

import os
import csv
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Tuple, List, Dict
import shutil
from collections import defaultdict
import random


def csv_to_yolo(row: Dict, img_width: int, img_height: int, class_id: int = 0) -> str:
    """
    Convierte coordenadas CSV (x0,y0,x1,y1) a formato YOLO.

    Args:
        row: Diccionario con keys width, height, x0, y0, x1, y1
        img_width: Ancho de la imagen
        img_height: Alto de la imagen
        class_id: ID de la clase (default 0 para face)

    Returns:
        String en formato YOLO: "class_id x_center y_center width height"
    """
    x0 = float(row['x0'])
    y0 = float(row['y0'])
    x1 = float(row['x1'])
    y1 = float(row['y1'])

    # Calcular centro y dimensiones normalizadas
    x_center = ((x0 + x1) / 2) / img_width
    y_center = ((y0 + y1) / 2) / img_height
    width = (x1 - x0) / img_width
    height = (y1 - y0) / img_height

    # Asegurar que los valores estén en rango [0, 1]
    x_center = max(0, min(1, x_center))
    y_center = max(0, min(1, y_center))
    width = max(0, min(1, width))
    height = max(0, min(1, height))

    return f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}"


def xml_to_yolo(xml_path: str, class_id: int = 0) -> Tuple[List[str], int, int]:
    """
    Convierte anotación XML (Pascal VOC) a formato YOLO.

    Args:
        xml_path: Ruta al archivo XML
        class_id: ID de la clase (default 0 para plate)

    Returns:
        Tupla (lista de anotaciones YOLO, width, height)
    """
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Obtener dimensiones de la imagen
    size = root.find('size')
    img_width = int(size.find('width').text)
    img_height = int(size.find('height').text)

    yolo_annotations = []

    # Procesar cada objeto
    for obj in root.findall('object'):
        bndbox = obj.find('bndbox')
        xmin = float(bndbox.find('xmin').text)
        ymin = float(bndbox.find('ymin').text)
        xmax = float(bndbox.find('xmax').text)
        ymax = float(bndbox.find('ymax').text)

        # Calcular centro y dimensiones normalizadas
        x_center = ((xmin + xmax) / 2) / img_width
        y_center = ((ymin + ymax) / 2) / img_height
        width = (xmax - xmin) / img_width
        height = (ymax - ymin) / img_height

        # Asegurar que los valores estén en rango [0, 1]
        x_center = max(0, min(1, x_center))
        y_center = max(0, min(1, y_center))
        width = max(0, min(1, width))
        height = max(0, min(1, height))

        yolo_annotations.append(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}")

    return yolo_annotations, img_width, img_height


def split_dataset(items: List[str], train_ratio: float = 0.7, valid_ratio: float = 0.2) -> Dict[str, List[str]]:
    """
    Divide el dataset en train/valid/test.

    Args:
        items: Lista de elementos a dividir
        train_ratio: Porcentaje para entrenamiento (default 0.7)
        valid_ratio: Porcentaje para validación (default 0.2)

    Returns:
        Diccionario con keys 'train', 'valid', 'test' y listas de elementos
    """
    random.shuffle(items)

    total = len(items)
    train_end = int(total * train_ratio)
    valid_end = train_end + int(total * valid_ratio)

    return {
        'train': items[:train_end],
        'valid': items[train_end:valid_end],
        'test': items[valid_end:]
    }


def prepare_faces_dataset(base_path: Path, output_path: Path):
    """
    Prepara el dataset de rostros (faces).

    Args:
        base_path: Ruta al dataset original
        output_path: Ruta donde guardar el dataset procesado
    """
    print("[INFO] Procesando dataset de ROSTROS...")

    csv_path = base_path / 'faces.csv'
    images_path = base_path / 'images'

    # Agrupar anotaciones por imagen (una imagen puede tener múltiples rostros)
    image_annotations = defaultdict(list)

    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            img_name = row['image_name']
            img_width = int(row['width'])
            img_height = int(row['height'])

            yolo_line = csv_to_yolo(row, img_width, img_height, class_id=0)
            image_annotations[img_name].append(yolo_line)

    # Obtener lista de imágenes únicas
    unique_images = list(image_annotations.keys())
    print(f"  Total de imágenes con anotaciones: {len(unique_images)}")

    # Dividir en train/valid/test
    splits = split_dataset(unique_images)

    print(f"  Train: {len(splits['train'])} imágenes")
    print(f"  Valid: {len(splits['valid'])} imágenes")
    print(f"  Test: {len(splits['test'])} imágenes")

    # Crear estructura de directorios
    for split in ['train', 'valid', 'test']:
        (output_path / 'images' / split).mkdir(parents=True, exist_ok=True)
        (output_path / 'labels' / split).mkdir(parents=True, exist_ok=True)

    # Copiar imágenes y crear archivos de labels
    for split, images in splits.items():
        for img_name in images:
            src_img = images_path / img_name
            dst_img = output_path / 'images' / split / img_name

            if src_img.exists():
                shutil.copy2(src_img, dst_img)

                # Crear archivo de label
                label_name = img_name.replace('.jpg', '.txt')
                label_path = output_path / 'labels' / split / label_name

                with open(label_path, 'w') as f:
                    f.write('\n'.join(image_annotations[img_name]))

    print("[OK] Dataset de rostros procesado correctamente\n")


def prepare_plates_dataset(base_path: Path, output_path: Path):
    """
    Prepara el dataset de matrículas (plates).

    Args:
        base_path: Ruta al dataset original
        output_path: Ruta donde guardar el dataset procesado
    """
    print("[INFO] Procesando dataset de MATRICULAS...")

    images_path = base_path / 'images'
    annotations_path = base_path / 'annotations'

    # Obtener lista de archivos XML
    xml_files = list(annotations_path.glob('*.xml'))
    print(f"  Total de anotaciones: {len(xml_files)}")

    # Dividir en train/valid/test
    splits = split_dataset(xml_files)

    print(f"  Train: {len(splits['train'])} imágenes")
    print(f"  Valid: {len(splits['valid'])} imágenes")
    print(f"  Test: {len(splits['test'])} imágenes")

    # Crear estructura de directorios
    for split in ['train', 'valid', 'test']:
        (output_path / 'images' / split).mkdir(parents=True, exist_ok=True)
        (output_path / 'labels' / split).mkdir(parents=True, exist_ok=True)

    # Procesar cada split
    for split, xml_files_list in splits.items():
        for xml_file in xml_files_list:
            # Nombre base sin extensión (ej: Cars0)
            base_name = xml_file.stem

            # Buscar imagen correspondiente
            img_file = images_path / f"{base_name}.png"

            if img_file.exists():
                # Copiar imagen
                dst_img = output_path / 'images' / split / f"{base_name}.png"
                shutil.copy2(img_file, dst_img)

                # Convertir XML a YOLO
                yolo_annotations, _, _ = xml_to_yolo(str(xml_file), class_id=0)

                # Guardar label
                label_path = output_path / 'labels' / split / f"{base_name}.txt"
                with open(label_path, 'w') as f:
                    f.write('\n'.join(yolo_annotations))

    print("[OK] Dataset de matriculas procesado correctamente\n")


def main():
    """Función principal para preparar ambos datasets."""
    print("=" * 60)
    print("PREPARACION DE DATASETS PARA YOLOV8")
    print("=" * 60)
    print()

    # Configurar rutas
    project_root = Path(__file__).parent.parent
    datasets_root = project_root / 'datasets'

    # Establecer seed para reproducibilidad
    random.seed(42)

    # Preparar dataset de rostros
    faces_input = datasets_root / 'faces'
    faces_output = datasets_root / 'faces_yolo'

    if faces_input.exists():
        prepare_faces_dataset(faces_input, faces_output)
    else:
        print(f"[WARNING] No se encontro {faces_input}")

    # Preparar dataset de matrículas
    plates_input = datasets_root / 'plates'
    plates_output = datasets_root / 'plates_yolo'

    if plates_input.exists():
        prepare_plates_dataset(plates_input, plates_output)
    else:
        print(f"[WARNING] No se encontro {plates_input}")

    print("=" * 60)
    print("[OK] PREPARACION COMPLETADA")
    print("=" * 60)
    print()
    print("Proximos pasos:")
    print("1. Crear archivos data.yaml para YOLOv8")
    print("2. Entrenar modelos con los datasets procesados")
    print("3. Evaluar rendimiento en conjunto de test")


if __name__ == '__main__':
    main()
