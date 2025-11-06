# ============================================================
# app/ocr/preprocess_pipeline.py — Flujo completo de preprocesamiento OCR
# ============================================================
# Este módulo define el pipeline completo de preprocesamiento de imágenes.
# Combina múltiples pasos (limpieza, contraste, binarización, corrección de
# inclinación y mejora de nitidez) para optimizar los resultados de OCR.
#
# Se apoya en los módulos:
#   - image_io.py        → conversión de bytes a matriz NumPy
#   - image_filters.py   → filtros de mejora visual
#
# Resultado: imagen procesada lista para reconocimiento OCR.
# ============================================================

import cv2
from .image_io import bytes_to_grayscale
from .image_filters import (
    denoise_and_contrast,
    binarize_and_clean,
    deskew_image,
    enhance_sharpness
)


# ============================================================
# Función: preprocess_image_bytes()
# ------------------------------------------------------------
# Ejecuta el flujo completo de preprocesamiento OCR sobre una imagen.
#
# Flujo general:
#   1️ Conversión de bytes → escala de grises.
#   2️ Reducción de ruido y aumento de contraste.
#   3️ Binarización y limpieza morfológica.
#   4️ Corrección de inclinación (deskew).
#   5️ Mejora de nitidez y detalle.
#   6️ Escalado final para mejorar legibilidad del OCR.
#   7️ Binarización suave final con Otsu.
#
# Parámetros:
#   - image_bytes (bytes): imagen original en formato binario.
#
# Retorna:
#   - img (np.ndarray): imagen procesada lista para reconocimiento OCR.
# ============================================================
def preprocess_image_bytes(image_bytes: bytes):
    """
    Flujo completo del preprocesamiento OCR.
    Combina limpieza, contraste, binarización, deskew y escalado final.
    """

    # 1️ Bytes → escala de grises
    # Convierte la imagen binaria (bytes) a matriz NumPy en escala de grises.
    img = bytes_to_grayscale(image_bytes)

    # 2️ Limpieza y contraste
    # Reduce ruido digital y aumenta contraste usando CLAHE.
    img = denoise_and_contrast(img)

    # 3️ Umbral + limpieza morfológica
    # Aplica binarización adaptativa y elimina líneas finas (por ejemplo, de cuadernos).
    img = binarize_and_clean(img)

    # 4️ Deskew
    # Corrige inclinaciones leves del texto para mejorar la detección OCR.
    img = deskew_image(img)

    # 5️ Nitidez final
    # Realza los bordes del texto y suaviza detalles excesivos.
    img = enhance_sharpness(img)

    # 6️ Escalado final 2x
    # Amplía la imagen al doble de tamaño (interpolación cúbica)
    # para facilitar el reconocimiento de caracteres pequeños.
    img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

    # 7️ Binarización suave final
    # Convierte nuevamente a blanco y negro usando el método de Otsu.
    _, img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Devuelve la imagen preprocesada final
    return img