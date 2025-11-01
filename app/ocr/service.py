# app/ocr/service.py
"""
Lógica principal de extracción OCR (impreso / manuscrito)
Optimizada para entornos limitados (como Render Free o Standard)
"""
from datetime import datetime
from typing import Dict
import io
import numpy as np
import cv2
from PIL import Image, UnidentifiedImageError
import pytesseract
from app.ocr.pipeline import preprocess_image_bytes
from app.ocr.reader import reader
from app.ocr.cleaner import clean_ocr_text

def _np_to_rgb(img_gray: np.ndarray) -> np.ndarray:
    """Convierte imagen a RGB si está en escala de grises."""
    if len(img_gray.shape) == 2:
        return cv2.cvtColor(img_gray, cv2.COLOR_GRAY2RGB)
    if img_gray.shape[2] == 3:
        return cv2.cvtColor(img_gray, cv2.COLOR_BGR2RGB)
    return img_gray

def _resize_if_needed(img: np.ndarray, max_dim: int = 1280) -> np.ndarray:
    """Evita que Render consuma demasiada memoria con imágenes grandes."""
    h, w = img.shape[:2]
    if max(h, w) > max_dim:
        ratio = max_dim / float(max(h, w))
        new_size = (int(w * ratio), int(h * ratio))
        return cv2.resize(img, new_size, interpolation=cv2.INTER_AREA)
    return img

async def extract_text_from_image(file) -> Dict[str, str]:
    """
    Pipeline completo:
      - Verifica tipo de archivo
      - Preprocesa (grises, contraste, binarización, deskew)
      - OCR con EasyOCR + Tesseract
      - Limpieza final
    """
    try:
        data = await file.read()
        if not file.content_type or not file.content_type.startswith("image/"):
            raise ValueError("❌ El archivo no es una imagen válida.")

        # Decodificar y validar
        try:
            Image.open(io.BytesIO(data))
        except UnidentifiedImageError:
            raise ValueError("⚠️ Imagen corrupta o formato no compatible.")

        # 1️⃣ Preprocesamiento
        img_gray = preprocess_image_bytes(data)
        rgb = _np_to_rgb(img_gray)
        rgb = _resize_if_needed(rgb)

        # 2️⃣ EasyOCR
        try:
            results_easy = reader.readtext(rgb, detail=1, paragraph=True)
            text_easy = "\n".join([r[1] for r in results_easy if len(r) > 1]).strip()
        except Exception as e:
            print(f"⚠️ EasyOCR falló: {e}")
            text_easy = ""

        # 3️⃣ PyTesseract
        try:
            text_tess = pytesseract.image_to_string(Image.fromarray(rgb), lang="spa+eng")
        except Exception as e:
            print(f"⚠️ PyTesseract falló: {e}")
            text_tess = ""

        # 4️⃣ Combinación y limpieza
        combined = (text_easy + "\n" + text_tess).strip()
        if not combined:
            raise ValueError("⚠️ No se detectó texto legible en la imagen.")

        cleaned = clean_ocr_text(combined)

        return {
            "text": cleaned,
            "mime": file.content_type,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

    except ValueError as e:
        # Error esperado (imagen vacía, formato inválido, etc.)
        raise ValueError(str(e))

    except Exception as e:
        # Error inesperado (OCR interno, memoria, etc.)
        raise ValueError(f"❌ Error interno del OCR: {e}")