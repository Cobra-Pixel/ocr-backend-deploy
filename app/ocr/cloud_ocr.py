# app/ocr/cloud_ocr.py
import os
import io
import requests
from PIL import Image
from dotenv import load_dotenv

# Cargar variables (solo en local, Render usa variables de entorno)
load_dotenv()

API_KEY = os.getenv("OCR_SPACE_API_KEY")
OCR_URL = "https://api.ocr.space/parse/image"

def _resize_image_if_needed(image_bytes: bytes, max_dim: int = 1280) -> bytes:
    """
    Reduce resolución si la imagen es muy grande (OCR.Space tiene límite de ~1.5MB).
    """
    try:
        img = Image.open(io.BytesIO(image_bytes))
        if max(img.size) > max_dim:
            ratio = max_dim / float(max(img.size))
            new_size = tuple(int(x * ratio) for x in img.size)
            img = img.resize(new_size, Image.LANCZOS)
        buf = io.BytesIO()
        img.convert("RGB").save(buf, format="JPEG", quality=85)
        return buf.getvalue()
    except Exception:
        return image_bytes

def extract_text_cloud(image_bytes: bytes, filename: str, lang: str = "spa") -> dict:
    """
    Envía imagen a OCR.Space y devuelve el texto extraído o mensaje de error.
    """
    if not API_KEY:
        raise ValueError("❌ Falta configurar OCR_SPACE_API_KEY en Render.")

    # Reescalar y comprimir
    safe_bytes = _resize_image_if_needed(image_bytes)
    if len(safe_bytes) > 1_500_000:
        raise ValueError("⚠️ Imagen demasiado grande incluso tras compresión (límite 1.5 MB).")

    files = {"file": (filename or "image.jpg", safe_bytes, "image/jpeg")}
    data = {
        "apikey": API_KEY,
        "language": lang,
        "isOverlayRequired": False,
        "OCREngine": 2,
        "scale": True,
        "detectOrientation": True,
    }

    try:
        resp = requests.post(OCR_URL, files=files, data=data, timeout=60)
        resp.raise_for_status()
        result = resp.json()
    except Exception as e:
        raise ValueError(f"❌ Error al conectar con OCR.Space: {e}")

    if result.get("IsErroredOnProcessing"):
        err_msg = result.get("ErrorMessage") or result.get("ErrorDetails") or ["Error desconocido"]
        if isinstance(err_msg, list):
            err_msg = err_msg[0]
        raise ValueError(f"⚠️ OCR.Space rechazó la imagen: {err_msg}")

    parsed = result.get("ParsedResults") or []
    text = (parsed[0].get("ParsedText", "") if parsed else "").strip()

    if not text:
        raise ValueError("⚠️ No se detectó texto en la imagen (OCR.Space devolvió vacío).")

    return {"text": text}