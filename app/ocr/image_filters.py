# ============================================================
# app/ocr/image_filters.py — Filtros de preprocesamiento de imágenes para OCR
# ============================================================
# Este módulo contiene funciones para preparar imágenes antes del reconocimiento OCR.
# Mejora la calidad visual mediante reducción de ruido, aumento de contraste,
# binarización, eliminación de líneas y corrección de inclinación del texto.
#
# Se usa OpenCV (cv2) y NumPy para las transformaciones de imagen.
# ============================================================

import cv2
import numpy as np


# ============================================================
# Función: denoise_and_contrast()
# ------------------------------------------------------------
# Reduce el ruido digital (artefactos) y aumenta el contraste general de la imagen.
# Utiliza:
#   - fastNlMeansDenoising: para eliminar ruido sin perder detalles.
#   - CLAHE (Contrast Limited Adaptive Histogram Equalization): mejora el contraste
#     local en áreas oscuras o con iluminación desigual.
#   - Normalización: ajusta los valores de brillo entre 0 y 255.
#
# Ideal para: imágenes escaneadas o con poca iluminación.
# ============================================================
def denoise_and_contrast(img: np.ndarray) -> np.ndarray:
    """Reduce ruido y aumenta contraste con CLAHE + normalización."""
    # 1️ Elimina ruido preservando bordes y trazos finos
    img = cv2.fastNlMeansDenoising(img, None, 10, 7, 21)

    # 2️ Aplica ecualización adaptativa de histograma (CLAHE)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    img = clahe.apply(img)

    # 3️ Normaliza la intensidad entre 0 (negro) y 255 (blanco)
    img = cv2.normalize(img, None, 0, 255, cv2.NORM_MINMAX)

    return img


# ============================================================
# Función: binarize_and_clean()
# ------------------------------------------------------------
# Convierte la imagen a blanco y negro (binarización adaptativa)
# y elimina líneas horizontales finas como las de una libreta.
#
# Utiliza:
#   - adaptiveThreshold: separa texto del fondo dinámicamente.
#   - morphological operations (MORPH_OPEN): limpia líneas horizontales.
#   - medianBlur: suaviza bordes del texto.
#
# Ideal para: notas manuscritas o papel cuadriculado.
# ============================================================
def binarize_and_clean(img: np.ndarray) -> np.ndarray:
    """Binariza y limpia líneas finas (mejor para notas de libreta)."""
    # 1️ Binarización adaptativa (inversión de colores)
    thresh = cv2.adaptiveThreshold(
        img,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        15,
        11
    )

    # 2️ Crea un kernel horizontal para detectar líneas de libreta
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))

    # 3️ Detecta y remueve líneas horizontales
    remove_horizontal = cv2.morphologyEx(
        thresh,
        cv2.MORPH_OPEN,
        horizontal_kernel,
        iterations=1
    )

    # 4️ Sustrae las líneas detectadas del resultado
    cleaned = cv2.subtract(thresh, remove_horizontal)

    # 5️ Suaviza bordes del texto para mejorar OCR
    cleaned = cv2.medianBlur(cleaned, 3)

    return cleaned


# ============================================================
# Función: deskew_image()
# ------------------------------------------------------------
# Corrige la inclinación del texto (deskew), detectando el ángulo
# mediante la mínima área rotada de los píxeles activos.
#
# Utiliza:
#   - cv2.minAreaRect() para calcular el ángulo de rotación.
#   - cv2.warpAffine() para rotar la imagen al ángulo correcto.
#
# Ideal para: fotografías inclinadas o escaneos torcidos.
# ============================================================
def deskew_image(img: np.ndarray) -> np.ndarray:
    """Corrige inclinación leve del texto."""
    # Encuentra coordenadas de los píxeles con texto (blancos)
    coords = np.column_stack(np.where(img > 0))
    angle = 0.0

    # 1️ Si hay píxeles detectados, calcula el ángulo mínimo del texto
    if coords.size > 0:
        rect = cv2.minAreaRect(coords)
        angle = rect[-1]

        # Ajusta ángulo a rango correcto (-45 a 45 grados)
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle

    # 2️ Calcula centro y aplica rotación inversa
    (h, w) = img.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)

    # 3️ Rota imagen para alinear texto
    return cv2.warpAffine(
        img,
        M,
        (w, h),
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_REPLICATE
    )


# ============================================================
# Función: enhance_sharpness()
# ------------------------------------------------------------
# Aumenta la nitidez del texto usando un filtro de realce (sharpen kernel),
# y aplica un ligero desenfoque para suavizar bordes duros.
#
# Ideal para: texto borroso o difuminado.
# ============================================================
def enhance_sharpness(img: np.ndarray) -> np.ndarray:
    """Aumenta nitidez y suaviza bordes de trazos."""
    # 1️ Define un kernel de realce de bordes (sharpen filter)
    kernel_sharp = np.array([
        [-1, -1, -1],
        [-1,  9, -1],
        [-1, -1, -1]
    ])

    # 2️ Aplica el filtro a la imagen
    sharpened = cv2.filter2D(img, -1, kernel_sharp)

    # 3️ Suaviza mínimamente para reducir bordes duros
    return cv2.GaussianBlur(sharpened, (1, 1), 0)