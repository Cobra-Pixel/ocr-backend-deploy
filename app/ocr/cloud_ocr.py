# app/ocr/cloud_ocr.py
import os
import io
from typing import Dict

import requests
from PIL import Image
from dotenv import load_dotenv

# Solo para entorno local; en Render las variables vienen del panel
load_dotenv()

API_KEY = os.getenv("OCR_SPACE_API_KEY")
OCR_URL = "https://api.ocr.space/parse/image"

def _compress_if_needed(image_bytes: bytes, max_bytes: int = 1_500_000) -> bytes:
    """
    Re-encode a JPEG si el archivo es grande para evitar límites de OCR.Space.
    """
    if len(image_bytes) <= max_bytes:
        return image_bytes
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        # iterar calidades hasta quedar por debajo del límite
        for quality in (85, 80, 75, 70, 60):
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=quality, optimize=True)
            data = buf.getvalue()
            if len(data) <= max_bytes:
                return data
        return data
    except Exception:
        # si falla la compresión, regresamos el original
        return image_bytes

def extract_text_cloud(image_bytes: bytes, filename: str, lang: str = "spa") -> Dict[str, str]:
    """
    Envía la imagen a la API OCR.Space y devuelve el texto reconocido.
    """
    if not API_KEY:
        raise ValueError("OCR_SPACE_API_KEY no configurada en el servidor")

    payload = {
        "apikey": API_KEY,
        "language": lang,
        "isOverlayRequired": False,
        "OCREngine": 2,            # engine moderno
        "scale": True,
        "detectOrientation": True,
    }

    # filetype orienta mejor al motor (opcional)
    ext = (filename.split(".")[-1] or "png").lower()
    payload["filetype"] = ext

    safe_bytes = _compress_if_needed(image_bytes)

    files = {
        "file": (filename or f"image.{ext}", safe_bytes),
    }

    if response.status_code >= 400:
        raise ValueError(f"OCR.Space devolvió {response.status_code}: {response.text[:200]}")

    # Algunas respuestas de error vienen con 4xx/5xx: preferimos propagar el mensaje
    try:
        result = response.json()
    except Exception:
        raise ValueError(f"Respuesta inválida de OCR.Space: status={response.status_code} body={response.text[:200]}")

    if result.get("IsErroredOnProcessing"):
        # Devuelve primer mensaje entendible
        err = result.get("ErrorMessage") or result.get("ErrorDetails") or ["Error desconocido en OCR.Space"]
        if isinstance(err, list):
            err = err[0]
        raise ValueError(str(err))

    parsed = result.get("ParsedResults") or []
    text = (parsed[0].get("ParsedText", "") if parsed else "").strip()
    return {"text": text}