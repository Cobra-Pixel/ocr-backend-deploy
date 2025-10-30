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
        raise ValueError("⚠️ Falta OCR_SPACE_API_KEY en el archivo .env")

    # Verifica idioma válido, OCR.Space no acepta combinaciones como "spa+eng"
    allowed_langs = {"eng", "spa", "por", "fra", "deu", "ita", "ara", "chi_sim", "jpn", "rus", "tur", "vie"}
    if lang not in allowed_langs:
        print(f"⚠️ Idioma '{lang}' no permitido. Se usará 'spa' por defecto.")
        lang = "spa"
     # Comprimir la imagen si pesa más de 1 MB
    if len(image_bytes) > 1024 * 1024:
        print("⚠️ Imagen demasiado grande, se comprimirá antes de enviar.")
        image = Image.open(io.BytesIO(image_bytes))
        image = image.convert("RGB")  # asegura formato
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=70, optimize=True)
        image_bytes = buffer.getvalue()
    
    files = {"file": (filename or "image.jpg", image_bytes)}
    data = {
        "language": lang,              # idioma simple válido
        "isOverlayRequired": False,
        "scale": True,
        "isTable": False,
        "OCREngine": 2,                # motor OCR moderno
    }
    headers = {"apikey": API_KEY}

    # Petición POST
    response = requests.post(OCR_URL, files=files, data=data, headers=headers, timeout=60)
    response.raise_for_status()
    result = response.json()

    if result.get("IsErroredOnProcessing"):
        err = result.get("ErrorMessage") or ["Error en OCR.Space"]
        raise ValueError(str(err[0]))

    parsed = result.get("ParsedResults", [])
    if not parsed:
        return ""

    text = parsed[0].get("ParsedText", "")
    return text.strip()