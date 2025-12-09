# Frontend Dockerfile - React + Vite (Multi-stage build)

# ====================================
# Etapa 1: Build de la aplicación
# ====================================
FROM node:20-alpine AS builder

WORKDIR /app

# Copiar archivos de dependencias
COPY package*.json ./

# Instalar dependencias
RUN npm ci --prefer-offline --no-audit

# Copiar código fuente
COPY . .

# Build de producción
RUN npm run build

# ====================================
# Etapa 2: Servidor nginx
# ====================================
FROM nginx:1.27-alpine

# Copiar build al directorio de nginx
COPY --from=builder /app/dist /usr/share/nginx/html

# Crear configuración de nginx
RUN echo 'server { \n\
    listen 80; \n\
    server_name _; \n\
    root /usr/share/nginx/html; \n\
    index index.html; \n\
    \n\
    # Configuración para SPA (Single Page Application) \n\
    location / { \n\
        try_files $uri $uri/ /index.html; \n\
    } \n\
    \n\
    # Proxy para el backend \n\
    location /api { \n\
        proxy_pass http://backend:8000; \n\
        proxy_http_version 1.1; \n\
        proxy_set_header Upgrade $http_upgrade; \n\
        proxy_set_header Connection "upgrade"; \n\
        proxy_set_header Host $host; \n\
        proxy_set_header X-Real-IP $remote_addr; \n\
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for; \n\
        proxy_set_header X-Forwarded-Proto $scheme; \n\
        proxy_cache_bypass $http_upgrade; \n\
        \n\
        # Timeouts largos para procesamiento de imágenes \n\
        proxy_connect_timeout 300s; \n\
        proxy_send_timeout 300s; \n\
        proxy_read_timeout 300s; \n\
        \n\
        # Tamaño máximo de body para uploads \n\
        client_max_body_size 20M; \n\
    } \n\
    \n\
    # Cache para assets estáticos \n\
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ { \n\
        expires 1y; \n\
        add_header Cache-Control "public, immutable"; \n\
    } \n\
    \n\
    # Compresión gzip \n\
    gzip on; \n\
    gzip_vary on; \n\
    gzip_min_length 1024; \n\
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/json application/javascript; \n\
}' > /etc/nginx/conf.d/default.conf

# Exponer puerto
EXPOSE 80

# Healthcheck
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost/ || exit 1

# Comando por defecto
CMD ["nginx", "-g", "daemon off;"]
