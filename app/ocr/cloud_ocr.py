import os
import io
import requests
from PIL import Image
from dotenv import load_dotenv

# Carga variables del archivo .env
load_dotenv()

API_KEY = os.getenv("OCR_SPACE_API_KEY")
OCR_URL = "https://api.ocr.space/parse/image"

def extract_text_cloud(image_bytes: bytes, filename: str, lang: str = "spa"):
    """
    Envía la imagen a la API OCR.Space y devuelve el texto reconocido.
    Funciona bien con manuscritos o fotos de cuaderno.
    """
    if not API_KEY:
        raise ValueError("⚠️ Falta OCR_SPACE_API_KEY en el entorno o archivo .env")

    # 🔹 Idiomas válidos según OCR.Space
    allowed_langs = {
        "eng", "spa", "por", "fra", "deu", "ita", "ara",
        "chi_sim", "jpn", "rus", "tur", "vie"
    }
    if lang not in allowed_langs:
        print(f"⚠️ Idioma '{lang}' no permitido. Se usará 'spa' por defecto.")
        lang = "spa"

    # 🔹 Comprimir si es muy grande (>1MB)
    if len(image_bytes) > 1024 * 1024:
        print("⚠️ Imagen demasiado grande, se comprimirá antes de enviar.")
        image = Image.open(io.BytesIO(image_bytes))
        image = image.convert("RGB")
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=70, optimize=True)
        image_bytes = buffer.getvalue()

    # 🔹 Archivos y parámetros
    files = {
        "file": (filename or "image.jpg", image_bytes, "image/jpeg")
    }
    data = {
        "apikey": API_KEY,
        "language": lang,
        "isOverlayRequired": False,
        "scale": True,
        "isTable": False,
        "OCREngine": 1  # <-- usa motor estable 1, no el 2 (causa errores)
    }

    try:
        response = requests.post(OCR_URL, files=files, data=data, timeout=90)
        response.raise_for_status()
    except Exception as e:
        raise ValueError(f"❌ Error en la petición a OCR.Space: {e}")

    try:
        result = response.json()
    except Exception:
        raise ValueError(f"❌ Respuesta inválida de OCR.Space: {response.text[:200]}")

    if result.get("IsErroredOnProcessing"):
        err = result.get("ErrorMessage") or result.get("ErrorDetails") or ["Error desconocido en OCR.Space"]
        raise ValueError(f"⚠️ {err[0]}")

    parsed = result.get("ParsedResults", [])
    if not parsed:
        return {"text": "", "error": "No se detectó texto"}

    text = parsed[0].get("ParsedText", "")
    return {"text": text.strip()}