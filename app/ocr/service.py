# ============================================================
# app/ocr/service.py — Lógica principal del procesamiento OCR
# ============================================================
# Este módulo implementa el pipeline completo de extracción de texto OCR
# tanto para texto impreso como manuscrito. Combina EasyOCR y PyTesseract
# para maximizar la precisión y aplica limpieza avanzada del resultado.
#
# Optimizado para entornos con recursos limitados (Render Free/Standard).
# ============================================================

from datetime import datetime
from typing import Dict
import io
import re
import numpy as np
import cv2
from PIL import Image, UnidentifiedImageError
import pytesseract
from app.ocr.pipeline import preprocess_image_bytes
from app.ocr.reader import reader
from app.ocr.cleaner import clean_ocr_text


# ============================================================
# Función auxiliar: _np_to_rgb()
# ------------------------------------------------------------
# Convierte una imagen en escala de grises o en BGR a formato RGB.
# Esto es necesario porque algunos motores OCR (como EasyOCR)
# esperan imágenes en color RGB, incluso si son grises.
# ============================================================
def _np_to_rgb(img_gray: np.ndarray) -> np.ndarray:
    """Convierte imagen a RGB si está en escala de grises."""
    if len(img_gray.shape) == 2:
        return cv2.cvtColor(img_gray, cv2.COLOR_GRAY2RGB)
    if img_gray.shape[2] == 3:
        return cv2.cvtColor(img_gray, cv2.COLOR_BGR2RGB)
    return img_gray


# ============================================================
# Función auxiliar: _resize_if_needed()
# ------------------------------------------------------------
# Redimensiona la imagen si supera un tamaño máximo definido.
# Esto previene que Render consuma demasiada memoria con
# imágenes de alta resolución.
# ============================================================
def _resize_if_needed(img: np.ndarray, max_dim: int = 1280) -> np.ndarray:
    """Evita que Render consuma demasiada memoria con imágenes grandes."""
    h, w = img.shape[:2]
    if max(h, w) > max_dim:
        ratio = max_dim / float(max(h, w))
        new_size = (int(w * ratio), int(h * ratio))
        return cv2.resize(img, new_size, interpolation=cv2.INTER_AREA)
    return img


# ============================================================
# Función auxiliar: _post_clean_text()
# ------------------------------------------------------------
# Aplica una limpieza profunda del texto OCR:
#   - Elimina líneas con exceso de números o símbolos.
#   - Descarta duplicados exactos.
#   - Normaliza saltos de línea y espacios.
#
# Esto mejora la legibilidad del texto final y reduce errores
# comunes en OCR sobre documentos ruidosos o escaneos.
# ============================================================
def _post_clean_text(text: str) -> str:
    """
    Limpia ruido: números sueltos, símbolos, duplicados y normaliza espacios.
    """
    # Divide en líneas no vacías
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    filtered = []

    for ln in lines:
        # Evita líneas con muchos números o símbolos irrelevantes
        letters = len(re.findall(r"[A-Za-zÁÉÍÓÚáéíóúÑñ]", ln))
        numbers = len(re.findall(r"\d", ln))
        if numbers > letters * 2:
            continue
        if len(ln) <= 2:
            continue
        if re.fullmatch(r"[\d\s;:%'\"!¡?¿,.]+", ln):
            continue
        filtered.append(ln)

    # Elimina líneas duplicadas consecutivas
    clean_unique = []
    for ln in filtered:
        if not clean_unique or clean_unique[-1].lower() != ln.lower():
            clean_unique.append(ln)

    # Normaliza espacios y saltos de línea
    clean_text = "\n".join(clean_unique)
    clean_text = re.sub(r"[ \t]+", " ", clean_text)
    clean_text = re.sub(r"\n{3,}", "\n\n", clean_text)

    return clean_text.strip()


# ============================================================
# Función principal: extract_text_from_image()
# ------------------------------------------------------------
# Ejecuta el flujo completo de procesamiento OCR:
#   1️ Verifica tipo de archivo y formato de imagen.
#   2️ Aplica pipeline de preprocesamiento (contraste, binarización, deskew).
#   3️ Ejecuta EasyOCR y PyTesseract para extraer texto.
#   4️ Combina, limpia y normaliza el resultado final.
#
# Parámetros:
#   - file: objeto de archivo subido (Starlette UploadFile).
#
# Retorna:
#   - dict con texto limpio, MIME type y timestamp ISO.
# ============================================================
async def extract_text_from_image(file) -> Dict[str, str]:
    """
    Pipeline completo:
      - Verifica tipo de archivo
      - Preprocesa (grises, contraste, binarización, deskew)
      - OCR con EasyOCR + Tesseract
      - Limpieza avanzada
    """
    try:
        # Leer contenido del archivo subido
        data = await file.read()

        # Validar tipo MIME
        if not file.content_type or not file.content_type.startswith("image/"):
            raise ValueError(" El archivo no es una imagen válida.")

        # Decodificar y verificar formato de imagen
        try:
            Image.open(io.BytesIO(data))
        except UnidentifiedImageError:
            raise ValueError(" Imagen corrupta o formato no compatible.")

        # =====================================================
        # 1️ Preprocesamiento de la imagen
        # =====================================================
        img_gray = preprocess_image_bytes(data)
        rgb = _np_to_rgb(img_gray)
        rgb = _resize_if_needed(rgb)

        # =====================================================
        # 2️ OCR con EasyOCR
        # =====================================================
        try:
            results_easy = reader.readtext(rgb, detail=1, paragraph=True)
            text_easy = "\n".join([r[1] for r in results_easy if len(r) > 1]).strip()
        except Exception as e:
            print(f" EasyOCR falló: {e}")
            text_easy = ""

        # =====================================================
        # 3️ OCR con PyTesseract
        # =====================================================
        try:
            text_tess = pytesseract.image_to_string(Image.fromarray(rgb), lang="spa+eng")
        except Exception as e:
            print(f" PyTesseract falló: {e}")
            text_tess = ""

        # =====================================================
        # 4️ Combinación y limpieza de texto
        # =====================================================
        combined = (text_easy + "\n" + text_tess).strip()
        if not combined:
            raise ValueError(" No se detectó texto legible en la imagen.")

        # Limpieza profunda: caracteres, duplicados y formato
        cleaned = clean_ocr_text(combined)
        cleaned = _post_clean_text(cleaned)

        # =====================================================
        # 5️ Respuesta final
        # =====================================================
        return {
            "text": cleaned,                                 # Texto extraído y limpio
            "mime": file.content_type,                        # Tipo MIME original
            "timestamp": datetime.utcnow().isoformat() + "Z", # Marca de tiempo UTC
        }

    # ============================================================
    # Manejo de errores
    # ============================================================
    except ValueError as e:
        raise ValueError(str(e))

    except Exception as e:
        raise ValueError(f" Error interno del OCR: {e}")