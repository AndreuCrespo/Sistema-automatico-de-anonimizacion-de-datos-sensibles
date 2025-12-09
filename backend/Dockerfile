# Backend Dockerfile - FastAPI + YOLOv8 + CUDA 12.8
# Usa imagen oficial de PyTorch con CUDA 12.8
FROM pytorch/pytorch:2.6.0-cuda12.4-cudnn9-runtime

# Configurar variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# Instalar dependencias del sistema necesarias para OpenCV
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgeos-dev \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Instalar PyTorch 2.9.0 con CUDA 12.8
RUN pip install --no-cache-dir \
    torch==2.9.0 \
    torchvision==0.24.0 \
    --index-url https://download.pytorch.org/whl/cu128

# Instalar dependencias de la aplicación
RUN pip install --no-cache-dir \
    fastapi==0.115.6 \
    uvicorn[standard]==0.34.0 \
    python-multipart==0.0.20 \
    pydantic==2.10.5 \
    pydantic-settings==2.7.1 \
    ultralytics==8.3.223 \
    opencv-python-headless==4.10.0.84 \
    Pillow==11.1.0 \
    numpy==2.2.1 \
    pandas==2.2.3 \
    scipy==1.15.1 \
    python-dotenv==1.0.1 \
    pyyaml==6.0.2 \
    tqdm==4.67.1 \
    lxml==5.3.0 \
    scikit-image==0.25.0 \
    imageio==2.37.0 \
    loguru==0.7.2 \
    httpx==0.26.0

# Copiar código del backend
COPY backend/ /app/backend/

# Crear directorios necesarios
RUN mkdir -p /app/models/trained /app/uploads /app/logs

# Copiar modelo entrenado
COPY models/trained/unified_detector.pt /app/models/trained/

# Exponer puerto
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/api/health')"

# Comando para iniciar el servidor
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
