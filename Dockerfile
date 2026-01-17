# Usar Python 3.11
FROM python:3.11-slim

# Instalar ffmpeg (necesario para pydub)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Establecer directorio de trabajo
WORKDIR /app

# Copiar requirements primero (para cache de Docker)
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY . .

# Exponer el puerto (Render asignará PORT automáticamente)
EXPOSE 8000

# Comando de inicio
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
