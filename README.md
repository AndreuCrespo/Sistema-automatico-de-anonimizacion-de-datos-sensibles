# Sistema automatico de anonimizacion de datos sensibles

## Descripcion

Sistema completo de anonimizacion automatica de datos sensibles que detecta y anonimiza:
- Rostros humanos en imagenes y videos
- Matriculas de vehiculos
- Datos sensibles en texto (DNI, telefonos, emails, IBAN, tarjetas, nombres, direcciones)

Procesamiento 100% local, sin dependencias cloud, cumpliendo GDPR.

## Stack tecnologico

### Backend
- Python 3.11+
- FastAPI (API REST)
- PyTorch + Ultralytics YOLOv8 (deteccion visual)
- OpenCV (procesamiento de imagen/video)
- Ollama + Qwen3-8B (analisis de texto con LLM local)

### Frontend
- React 18 + Vite
- Material-UI (MUI)
- Axios

### Infraestructura
- Docker + Docker Compose
- GPU (NVIDIA CUDA 12.4)

## Estructura del proyecto

```
tfm-anonimizacion/
├── backend/                        # API FastAPI
│   ├── app/
│   │   ├── api/endpoints/          # Endpoints REST
│   │   │   ├── anonymize.py
│   │   │   ├── classes.py
│   │   │   ├── detect.py
│   │   │   ├── health.py
│   │   │   ├── text.py
│   │   │   └── video.py
│   │   ├── core/                   # Configuracion
│   │   │   ├── config.py
│   │   │   └── logging_config.py
│   │   ├── models/                 # Detectores YOLOv8
│   │   │   ├── face_detector.py
│   │   │   ├── multi_detector.py
│   │   │   ├── plate_detector.py
│   │   │   └── unified_detector.py
│   │   ├── schemas/                # Modelos Pydantic
│   │   │   ├── anonymization.py
│   │   │   ├── detection.py
│   │   │   └── health.py
│   │   ├── services/               # Logica de negocio
│   │   │   ├── anonymizer.py
│   │   │   ├── image_processor.py
│   │   │   ├── text_analyzer.py
│   │   │   └── video_processor.py
│   │   ├── utils/
│   │   │   └── file_handler.py
│   │   └── main.py
│   ├── tests/
│   │   ├── test_api.py
│   │   └── test_services.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/                       # React + MUI
│   ├── src/
│   │   ├── components/
│   │   │   ├── layout/MainLayout.jsx
│   │   │   ├── ClassSelector.jsx
│   │   │   ├── Controls.jsx
│   │   │   ├── ImagePreview.jsx
│   │   │   ├── ImageUpload.jsx
│   │   │   ├── VideoPreview.jsx
│   │   │   └── VideoUpload.jsx
│   │   ├── pages/
│   │   │   ├── Home.jsx
│   │   │   ├── ImageProcessing.jsx
│   │   │   ├── Settings.jsx
│   │   │   ├── TextAnalysis.jsx
│   │   │   └── VideoProcessing.jsx
│   │   ├── services/api.js
│   │   ├── App.jsx
│   │   ├── index.css
│   │   └── main.jsx
│   ├── Dockerfile
│   ├── index.html
│   └── vite.config.js
│
├── models/unified_training/        # Configuracion entrenamiento
│   └── args.yaml
│
├── scripts/                        # Scripts de utilidad
│   ├── benchmark_performance.py
│   ├── create_test_video.py
│   ├── create_unified_dataset.py
│   ├── evaluate_model.py
│   ├── evaluate_unified_model.py
│   ├── ollama-entrypoint.sh
│   ├── prepare_datasets.py
│   ├── train_face_detector.py
│   ├── train_plate_detector.py
│   ├── train_unified_model.py
│   └── train_unified_model_auto.py
│
├── docker-compose.yml
├── pyproject.toml
├── uv.lock
├── DOCKER_GUIDE.md
└── README.md
```

## API endpoints

### Imagenes
| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| POST | /api/anonymize | Anonimiza imagen (devuelve imagen) |
| POST | /api/detect | Solo deteccion (devuelve JSON) |
| GET | /api/classes | Clases disponibles |

### Videos
| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| POST | /api/process-video | Procesa video completo |
| WS | /api/ws/process-video | Streaming con preview |
| POST | /api/video-info | Metadata del video |

### Texto
| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| POST | /api/analyze-text | Detecta y anonimiza texto |
| POST | /api/detect-text | Solo deteccion |
| GET | /api/text/categories | Categorias disponibles |

### Sistema
| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| GET | /api/health | Estado del sistema |

## Metodos de anonimizacion

### Visual (imagenes/videos)
- **Gaussian blur**: desenfoque gaussiano (configurable)
- **Pixelate**: pixelacion por bloques
- **Mask**: cuadro negro solido

### Texto
- **Replace**: sustituye por tokens [TIPO-N]
- **Mask**: reemplaza por asteriscos
- **Remove**: elimina el dato

## Modos de deteccion de texto

- **Regex**: patrones estructurados (DNI, telefono, email, IBAN, tarjetas, fechas, codigos postales)
- **LLM**: deteccion contextual con Qwen3-8B (nombres, direcciones, organizaciones)
- **Both**: combinacion de ambos (segunda pasada de refuerzo)

## Instalacion

### Con uv (recomendado)

[uv](https://docs.astral.sh/uv/) es un gestor de paquetes Python ultrarapido, alternativa a pip.

```powershell
# Instalar uv (Windows)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Clonar repositorio
git clone https://github.com/usuario/tfm-anonimizacion.git
cd tfm-anonimizacion

# Instalar dependencias (crea .venv automaticamente)
uv sync

# Instalar Ollama y modelo LLM
winget install Ollama
ollama pull qwen3:8b

# Instalar frontend
cd frontend
npm install
cd ..

# Iniciar servicios
ollama serve                                           # Terminal 1
uv run uvicorn backend.app.main:app --reload           # Terminal 2
cd frontend && npm run dev                             # Terminal 3
```

### Con pip (alternativa)

```powershell
# Clonar repositorio
git clone https://github.com/usuario/tfm-anonimizacion.git
cd tfm-anonimizacion

# Crear entorno virtual
python -m venv .venv
.\.venv\Scripts\activate

# Instalar PyTorch con CUDA
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu128

# Instalar dependencias
pip install -r backend/requirements.txt

# Instalar Ollama y modelo
winget install Ollama
ollama pull qwen3:8b

# Instalar frontend
cd frontend
npm install
cd ..

# Iniciar servicios
ollama serve                                           # Terminal 1
cd backend && uvicorn app.main:app --reload            # Terminal 2
cd frontend && npm run dev                             # Terminal 3
```

### Docker

```bash
# Iniciar todos los servicios
docker-compose up -d
```

> **⏱️ Primera ejecución**: El primer arranque puede tardar **5-10 minutos** porque:
> 1. Se construyen las imágenes de backend y frontend
> 2. Se descarga el modelo LLM Qwen3-8B (~5.2GB)
>
> El sistema usa un healthcheck inteligente que espera a que el modelo esté completamente descargado antes de iniciar los demás servicios. **Las ejecuciones posteriores tardan menos de 2 minutos** ya que el modelo queda almacenado en el volumen `ollama-data`.

#### Verificar estado de los servicios

```bash
# Ver estado de los contenedores
docker ps

# Ver logs de Ollama (útil durante la primera descarga)
docker logs -f tfm-ollama

# Ver logs del backend
docker logs -f tfm-backend
```

#### Servicios y puertos

| Servicio | Puerto | Descripción |
|----------|--------|-------------|
| Frontend | http://localhost:80 | Interfaz web (Nginx + React) |
| Backend | http://localhost:8000 | API REST (FastAPI + YOLOv8) |
| Ollama | http://localhost:11434 | Servidor LLM local |

## Configuración

Variables de entorno principales (`.env` o docker-compose):

```env
# Servidor
HOST=0.0.0.0
PORT=8000
DEBUG=False

# Ollama (LLM)
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=qwen3:8b

# Deteccion
DETECTION_CONFIDENCE=0.25
```

## Metricas del Modelo

| Clase | Precision | Recall | F1-Score | mAP50 |
|-------|-----------|--------|----------|-------|
| Rostros | 0.92 | 0.89 | 0.90 | 0.91 |
| Matriculas | 0.88 | 0.85 | 0.86 | 0.87 |
| General | 0.90 | 0.87 | 0.88 | 0.89 |

Tiempo de procesamiento: <500ms por imagen (GPU)

## Uso

### Imagen
1. Acceder a http://localhost:3000
2. Ir a "Image Processing"
3. Subir imagen
4. Seleccionar clases a detectar y metodo de anonimizacion
5. Procesar y descargar resultado

### Video
1. Ir a "Video Processing"
2. Subir video (MP4, AVI, MOV)
3. Configurar opciones
4. Procesar con preview en tiempo real

### Texto
1. Ir a "Text Analysis"
2. Seleccionar modo (Regex/LLM/Both)
3. Pegar texto
4. Ver detecciones y texto anonimizado

## Testing

```powershell
# Tests unitarios
cd backend
pytest tests/ -v

# Tests de API
pytest tests/test_api.py -v
```

