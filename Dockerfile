# ============================================================
# Dockerfile — Imagen de despliegue para OCR Extractor Backend
# ============================================================
# Este archivo crea una imagen ligera basada en Python 3.12 Slim,
# instala dependencias del sistema necesarias para OCR (Tesseract y librerías),
# configura el entorno de trabajo, instala dependencias de Python,
# y arranca el servidor FastAPI en modo producción.
# ============================================================


# ============================================================
#  1️ Imagen base
# ------------------------------------------------------------
# Usa una versión ligera de Python 3.12 (basada en Debian Slim)
# para reducir el tamaño final de la imagen.
# ============================================================
FROM python:3.12-slim


# ============================================================
#  2️ Variables de entorno
# ------------------------------------------------------------
# Evita que Python guarde buffers en stdout/stderr (útil para logs en Docker).
# ============================================================
ENV PYTHONUNBUFFERED=1


# ============================================================
#  3️ Directorio de trabajo
# ------------------------------------------------------------
# Establece /app como el directorio donde se copiará y ejecutará el código.
# ============================================================
WORKDIR /app


# ============================================================
# 4️ Instalación de dependencias del sistema y Python
# ------------------------------------------------------------
# - Actualiza los paquetes base.
# - Instala Tesseract OCR y librerías de soporte (OpenCV, GLib, etc.).
# - Instala todas las dependencias de Python desde requirements.txt.
#
# `--no-cache-dir` evita almacenar archivos temporales de pip.
# ============================================================
COPY requirements.txt .
RUN apt-get update && apt-get install -y \
    tesseract-ocr \               # Motor OCR local
    libgl1 \                      # Librería requerida por OpenCV
    libglib2.0-0 \                # Soporte gráfico básico
    && pip install --no-cache-dir -r requirements.txt


# ============================================================
#  5️ Copiar código del proyecto
# ------------------------------------------------------------
# Copia todos los archivos del backend al contenedor (FastAPI, OCR, utils, etc.).
# ============================================================
COPY . .


# ============================================================
#  6️ Exponer puerto de ejecución
# ------------------------------------------------------------
# FastAPI usa el puerto 8000 por defecto (Render también lo detecta automáticamente).
# ============================================================
EXPOSE 8000


# ============================================================
#  7️ Precarga de modelos EasyOCR
# ------------------------------------------------------------
# Descarga y prepara los modelos de EasyOCR para español e inglés.
# Esto evita que se descarguen en tiempo de ejecución.
# ============================================================
RUN python -c "import easyocr; easyocr.Reader(['es', 'en'], gpu=False)"


# ============================================================
#  8️ Comando de inicio del servidor
# ------------------------------------------------------------
# Ejecuta la aplicación principal FastAPI (app/main.py) en modo producción.
# El uso de `python -m` permite resolver correctamente el paquete `app`.
# ============================================================
CMD ["python", "-m", "app.main"]