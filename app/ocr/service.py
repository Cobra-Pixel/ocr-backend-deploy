# Logica principal de extraccion OCR
import cv2
import pytesseract
from PIL import Image
from datetime import datetime
from app.ocr.pipeline import preprocess_image_bytes
from app.ocr.reader import reader
from app.ocr.cleaner import clean_ocr_text

async def extract_text_from_image(file) -> dict:
    """Pipeline completo: preprocesa, extrae con EasyOCR+Tesseract y limpia."""
    data = await file.read()

    # Validaciones básicas
    if not file.content_type.startswith("image/"):
        raise ValueError("Archivo no es una imagen válida")
    if len(data) > 10 * 1024 * 1024:
        raise ValueError("Imagen demasiado grande (>10MB)")

    gray = preprocess_image_bytes(data)
    rgb = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)

    # OCR EasyOCR
    results_easy = reader.readtext(
        rgb, detail=1, paragraph=False,
        text_threshold=0.4, low_text=0.2, link_threshold=0.3
    )
    text_easy = "\n".join([
    r[1] for r in results_easy
    if len(r) > 2 and float(r[2]) >= 0.30  # menor threshold mejora capturas de manuscrito
])

    # OCR Tesseract
    text_tess = pytesseract.image_to_string(Image.fromarray(rgb), lang="spa+eng")

    # Limpieza y mezcla
    cleaned = clean_ocr_text(f"{text_easy}\n{text_tess}")

    return {
        "text": cleaned,
        "mime": file.content_type,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }