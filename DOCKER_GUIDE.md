# Guía de despliegue con Docker

Esta guía explica cómo levantar el sistema completo usando Docker y Docker Compose.

## Requisitos previos

1. **Docker Desktop** instalado y configurado
   - Descargar: https://www.docker.com/products/docker-desktop/
   - Verificar: `docker --version` y `docker-compose --version`

2. **NVIDIA Container Toolkit** (para soporte GPU)
   ```bash
   # Windows: ya incluido en Docker Desktop con WSL2
   # Verificar que Docker Desktop tenga habilitado WSL2 integration
   ```

3. **Modelo entrenado** debe existir en:
   ```
   models/trained/unified_detector.pt
   ```

## Estructura de servicios

```
┌─────────────────────────────────────────────────┐
│                   Frontend                       │
│           React + Vite + Nginx                  │
│              Puerto: 80                         │
└────────────────┬────────────────────────────────┘
                 │ HTTP Proxy
                 ▼
┌─────────────────────────────────────────────────┐
│                   Backend                        │
│        FastAPI + YOLOv8 + PyTorch GPU           │
│              Puerto: 8000                       │
└─────────────────────────────────────────────────┘
```

## Comandos básicos

### 1. Construir las imágenes

```bash
# Construir ambos servicios
docker-compose build

# Construir solo backend
docker-compose build backend

# Construir solo frontend
docker-compose build frontend

# Construir sin usar caché (útil para actualizaciones)
docker-compose build --no-cache
```

### 2. Levantar los servicios

```bash
# Levantar en background (modo daemon)
docker-compose up -d

# Levantar en foreground (ver logs en tiempo real)
docker-compose up

# Levantar solo un servicio
docker-compose up -d backend
```

### 3. Ver logs

```bash
# Ver logs de todos los servicios
docker-compose logs -f

# Ver logs del backend
docker-compose logs -f backend

# Ver logs del frontend
docker-compose logs -f frontend

# Ver últimas 100 líneas
docker-compose logs --tail=100 -f
```

### 4. Verificar estado

```bash
# Ver servicios en ejecución
docker-compose ps

# Ver uso de recursos
docker stats

# Verificar salud de servicios
docker-compose ps
```

### 5. Detener servicios

```bash
# Detener servicios (mantiene volúmenes)
docker-compose stop

# Detener y eliminar contenedores (mantiene volúmenes)
docker-compose down

# Detener, eliminar contenedores y volúmenes
docker-compose down -v

# Detener, eliminar todo incluyendo imágenes
docker-compose down --rmi all
```

## Acceso a la aplicación

Una vez levantados los servicios:

- **Frontend**: http://localhost
- **Backend API**: http://localhost:8000
- **Documentación API**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health

## Verificación de GPU

Para verificar que el backend tiene acceso a la GPU:

```bash
# Ejecutar comando dentro del contenedor backend
docker-compose exec backend python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"N/A\"}')"
```

Deberías ver:
```
CUDA available: True
GPU: NVIDIA GeForce RTX 5080
```

## Desarrollo

### Modo desarrollo con hot-reload

El `docker-compose.yml` ya está configurado para desarrollo:

```yaml
volumes:
  - ./backend:/app/backend  # Hot-reload del código backend
```

Para cambios en el frontend, necesitas reconstruir:
```bash
docker-compose build frontend
docker-compose up -d frontend
```

### Ejecutar comandos dentro de contenedores

```bash
# Abrir shell en el backend
docker-compose exec backend bash

# Ejecutar script de Python
docker-compose exec backend python scripts/evaluate_unified_model.py

# Abrir shell en el frontend
docker-compose exec frontend sh
```

## Solución de problemas

### Error: "no matching manifest for windows/amd64"

Asegúrate de que Docker Desktop está configurado para usar **Linux containers** (no Windows containers).

### Error: "could not select device driver with capabilities: [[gpu]]"

1. Verifica que Docker Desktop tiene habilitado WSL2
2. Verifica NVIDIA drivers actualizados
3. Reinicia Docker Desktop

### Backend no detecta GPU

```bash
# Verificar dentro del contenedor
docker-compose exec backend nvidia-smi
```

Si falla, revisa la configuración de GPU en `docker-compose.yml`:
```yaml
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: 1
          capabilities: [gpu]
```

### Puerto ya en uso

Si el puerto 80 o 8000 ya están ocupados:

```bash
# Modificar puertos en docker-compose.yml
ports:
  - "8080:80"    # Frontend en puerto 8080
  - "8001:8000"  # Backend en puerto 8001
```

### Contenedor se reinicia constantemente

```bash
# Ver logs para identificar el problema
docker-compose logs -f backend

# Verificar que el modelo existe
ls -lh models/trained/unified_detector.pt
```

## Limpieza

```bash
# Eliminar contenedores detenidos
docker-compose down

# Eliminar imágenes no usadas
docker image prune -a

# Eliminar todo (contenedores, redes, imágenes, volúmenes)
docker system prune -a --volumes

# Ver espacio usado
docker system df
```
