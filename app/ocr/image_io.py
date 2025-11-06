# ============================================================
# app/ocr/image_utils.py — Utilidades para manejo de imágenes OCR
# ============================================================
# Este módulo contiene funciones auxiliares para convertir imágenes
# en distintos formatos, necesarias para el procesamiento OCR.
#
# En particular, convierte bytes crudos de una imagen en un arreglo
# NumPy en escala de grises, que puede ser usado por OpenCV y otros
# filtros definidos en el módulo image_filters.py.
# ============================================================

import numpy as np
from io import BytesIO
from PIL import Image


# ============================================================
# Función: bytes_to_grayscale()
# ------------------------------------------------------------
# Convierte una imagen recibida como bytes (por ejemplo, desde
# una solicitud HTTP o archivo subido) en una matriz NumPy en
# escala de grises.
#
# Flujo:
#   1️ Lee los bytes en memoria como un objeto de imagen PIL.
#   2️ Convierte la imagen a modo “L” (grayscale / escala de grises).
#   3️ Transforma el resultado en un array NumPy (valores 0–255).
#
# Parámetros:
#   - image_bytes (bytes): contenido binario de la imagen.
#
# Retorna:
#   - np.ndarray: imagen en escala de grises lista para procesar con OpenCV.
# ============================================================
def bytes_to_grayscale(image_bytes: bytes) -> np.ndarray:
    """Convierte bytes de imagen en array numpy en escala de grises."""
    # 1️ Crea un flujo binario a partir de los bytes de la imagen
    image = Image.open(BytesIO(image_bytes)).convert("L")

    # 2️ Convierte la imagen PIL a un array NumPy (grises 0–255)
    return np.array(image)