#!/bin/sh
# Script de inicialización para Ollama
# Descarga el modelo qwen3:8b si no está presente

set -e

echo "==================================="
echo "Iniciando Ollama y descargando modelo..."
echo "==================================="

# Iniciar Ollama en background
ollama serve &
OLLAMA_PID=$!

# Esperar a que Ollama esté listo
echo "Esperando a que Ollama esté listo..."
sleep 5

# Verificar si Ollama está corriendo
for i in $(seq 1 30); do
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "Ollama está listo!"
        break
    fi
    echo "Esperando... ($i/30)"
    sleep 2
done

# Descargar modelo qwen3:8b si no existe
echo "Verificando modelo qwen3:8b..."
if ! ollama list | grep -q "qwen3:8b"; then
    echo "Descargando modelo qwen3:8b (esto puede tardar varios minutos)..."
    ollama pull qwen3:8b
    echo "Modelo qwen3:8b descargado correctamente!"
else
    echo "Modelo qwen3:8b ya está disponible."
fi

echo "==================================="
echo "Ollama listo con modelo qwen3:8b"
echo "==================================="

# Mantener Ollama corriendo en foreground
wait $OLLAMA_PID
