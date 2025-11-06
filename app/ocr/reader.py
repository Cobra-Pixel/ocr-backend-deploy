# ============================================================
# app/ocr/ocr_reader.py — Inicialización del motor EasyOCR
# ============================================================
# Este módulo configura e inicializa el motor OCR basado en EasyOCR.
# Permite el reconocimiento de texto en imágenes en varios idiomas,
# usando una red preentrenada optimizada para alfabetos latinos.
#
# EasyOCR puede trabajar junto con PyTesseract o PaddleOCR, y es útil
# para reconocer texto manuscrito o impreso en documentos complejos.
# ============================================================

import easyocr


# ============================================================
# Inicialización global del lector OCR
# ------------------------------------------------------------
# Se crea una instancia del lector EasyOCR que soporta:
#   - Idiomas: español ('es') y inglés ('en').
#   - GPU desactivada (gpu=False) para compatibilidad en entornos
#     como Render o servidores sin aceleración CUDA.
#   - Red de reconocimiento: 'latin_g2', optimizada para texto impreso.
#
# El objeto `reader` se puede importar y reutilizar en todo el backend
# para realizar detecciones OCR sin re-inicializar el modelo.
# ============================================================
reader = easyocr.Reader(
    ['es', 'en'],          # Soporte multilenguaje (español e inglés)
    gpu=False,             # Sin GPU para compatibilidad en servidores
    recog_network='latin_g2'  # Red OCR preentrenada para alfabetos latinos
)