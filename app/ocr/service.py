# app/ocr/service.py
from datetime import datetime
from typing import Dict
import re
import numpy as np
from PIL import Image
import cv2
import pytesseract

from app.ocr.pipeline import preprocess_image_bytes
from app.ocr.reader import reader
from app.ocr.cleaner import clean_ocr_text


def _np_to_rgb(img_gray: np.ndarray) -> np.ndarray:
    """Asegura formato RGB para EasyOCR/Tesseract."""
    if len(img_gray.shape) == 2:
        return cv2.cvtColor(img_gray, cv2.COLOR_GRAY2RGB)
    if img_gray.shape[2] == 3:
        return cv2.cvtColor(img_gray, cv2.COLOR_BGR2RGB)
    return img_gray


def _remove_noise_lines(text: str) -> str:
    """Elimina líneas basura: numéricas, símbolos o repeticiones."""
    clean_lines = []
    for line in text.splitlines():
        line_stripped = line.strip()

        # Ignorar líneas vacías o llenas de símbolos
        if not line_stripped:
            continue
        if len(re.findall(r"[A-Za-zÁÉÍÓÚáéíóúÑñ]", line_stripped)) < 3:
            continue  # poca cantidad de letras, parece ruido
        if re.fullmatch(r"[\d\s;:.,%\-_'\"!¡?¿]+", line_stripped):
            continue
        if re.search(r"[;:%0-9]{5,}", line_stripped):
            continue

        clean_lines.append(line_stripped)

    # Evita duplicados consecutivos
    final_lines = []
    for line in clean_lines:
        if not final_lines or final_lines[-1].lower() != line.lower():
            final_lines.append(line)
    return "\n".join(final_lines)


def _normalize_spaces(text: str) -> str:
    """Normaliza espacios, saltos y signos raros."""
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


async def extract_text_from_image(file) -> Dict[str, str]:
    """
    Pipeline completo:
      - Preprocesa imagen
      - Extrae texto con EasyOCR + Tesseract
      - Limpia duplicados y ruido
    """
    data = await file.read()

    if not file.content_type or not file.content_type.startswith("image/"):
        raise ValueError("Archivo no es una imagen válida")

    # 1️⃣ Preprocesamiento
    img_gray = preprocess_image_bytes(data)
    rgb = _np_to_rgb(img_gray)

    # 2️⃣ EasyOCR (impreso/manuscrito)
    results_easy = reader.readtext(rgb, detail=1, paragraph=True)
    text_easy = "\n".join([r[1] for r in results_easy if len(r) > 1]).strip()

    # 3️⃣ Tesseract (impreso)
    text_tess = ""
    try:
        text_tess = pytesseract.image_to_string(Image.fromarray(rgb), lang="spa+eng")
    except Exception:
        text_tess = ""

    # 4️⃣ Combina y limpia
    combined = (text_easy + "\n" + text_tess).strip()
    cleaned = clean_ocr_text(combined)
    cleaned = _remove_noise_lines(cleaned)
    cleaned = _normalize_spaces(cleaned)

    return {
        "text": cleaned,
        "mime": file.content_type,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }