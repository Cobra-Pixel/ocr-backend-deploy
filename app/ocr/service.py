# app/ocr/service.py
# Lógica principal de extracción OCR
from datetime import datetime
from typing import Dict

import numpy as np
from PIL import Image
import cv2
import pytesseract

from app.ocr.pipeline import preprocess_image_bytes
from app.ocr.reader import reader
from app.ocr.cleaner import clean_ocr_text

def _np_to_rgb(img_gray: np.ndarray) -> np.ndarray:
    # Asegura formato RGB para EasyOCR/Tesseract
    if len(img_gray.shape) == 2:
        return cv2.cvtColor(img_gray, cv2.COLOR_GRAY2RGB)
    if img_gray.shape[2] == 3:
        return cv2.cvtColor(img_gray, cv2.COLOR_BGR2RGB)
    return img_gray

async def extract_text_from_image(file) -> Dict[str, str]:
    """
    Pipeline completo:
      - preprocesa
      - extrae con EasyOCR (impreso/manuscrito)
      - intenta Tesseract (si existe en el sistema)
      - limpia y mezcla
    """
    data = await file.read()

    if not file.content_type or not file.content_type.startswith("image/"):
        raise ValueError("Archivo no es una imagen válida")

    # 1) Preprocesamiento (grises, contraste, binarización, deskew, escalado)
    img_gray = preprocess_image_bytes(data)
    rgb = _np_to_rgb(img_gray)

    # 2) EasyOCR
    results_easy = reader.readtext(rgb, detail=1, paragraph=True)
    text_easy = "\n".join([r[1] for r in results_easy if len(r) > 1]).strip()

    # 3) Tesseract (opcional)
    text_tess = ""
    try:
        text_tess = pytesseract.image_to_string(Image.fromarray(rgb), lang="spa+eng")
    except Exception:
        # En Render puede no estar instalado tesseract-ocr. No rompemos el flujo.
        text_tess = ""

    # 4) Limpieza y mezcla
    combined = (text_easy + "\n" + text_tess).strip()
    cleaned = clean_ocr_text(combined)

    return {
        "text": cleaned,
        "mime": file.content_type,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }