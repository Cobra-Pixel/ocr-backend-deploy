# Usa una imagen ligera de Python 3.12
FROM python:3.12-slim

# Evita buffering de logs
ENV PYTHONUNBUFFERED=1

# Crea y usa el directorio de trabajo
WORKDIR /app

# Copia solo requirements primero (para aprovechar cache de Docker)
COPY requirements.txt .

# Instala dependencias sin cache
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del proyecto
COPY . .

# Expone el puerto donde correrá FastAPI
EXPOSE 8000

# Fuerza la descarga de modelos EasyOCR para evitar errores en Render
RUN python -m easyocr -l es,en --download_only

# Comando que ejecutará la app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]