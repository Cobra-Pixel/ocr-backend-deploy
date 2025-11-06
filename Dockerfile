# Usa una imagen ligera y moderna de Python
FROM python:3.12-slim

# Evita buffering de logs
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Instala dependencias del sistema necesarias para OCR
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    libtesseract-dev \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    ffmpeg \
    fonts-dejavu-core && \
    rm -rf /var/lib/apt/lists/*

# Establece directorio de trabajo
WORKDIR /app

# Copia requirements primero (aprovecha cache)
COPY requirements.txt .

# Instala dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código
COPY . .

# Expone el puerto para FastAPI
EXPOSE 8000

# 🔧 Precalienta EasyOCR (descarga modelos antes del arranque)
RUN python - <<EOF
import easyocr
print("📦 Precargando modelos EasyOCR (es/en)...")
reader = easyocr.Reader(['es', 'en'], gpu=False)
print("✅ Modelos EasyOCR listos.")
EOF

# Comando que inicia el servidor
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]