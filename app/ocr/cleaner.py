# Todas las funciones de limpieza de texto
import re
import unicodedata

def normalize_text(text: str) -> str:
    """Normaliza caracteres y reemplaza símbolos raros."""
    text = unicodedata.normalize("NFKC", text)
    return text.replace("ﬁ", "fi").replace("ﬂ", "fl").replace("—", "-").replace("–", "-")

def strip_garbage_prefix(text: str) -> str:
    """Elimina líneas con símbolos no alfanuméricos o ruido."""
    lines = [ln.strip() for ln in text.splitlines()]
    clean_lines = []
    for ln in lines:
        if not ln:
            continue
        good = sum(ch.isalnum() or ch.isspace() or ch in ".,;:!?¡¿'\"()-/%" for ch in ln)
        if len(ln) == 0 or good / max(1, len(ln)) < 0.4:
            continue
        ln = re.sub(r"^[^A-Za-zÁÉÍÓÚÑáéíóú0-9¿¡(]+", "", ln)
        if not re.search(r"[A-Za-zÁÉÍÓÚÑáéíóú]", ln):
            continue
        clean_lines.append(ln)
    return "\n".join(clean_lines).strip()

def collapse_spaces(text: str) -> str:
    """Reduce espacios y saltos de línea innecesarios."""
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\s*\n\s*", "\n", text)
    return text.strip()

def clean_ocr_text(text: str) -> str:
    """Limpieza completa de texto OCR."""
    text = normalize_text(text)
    text = re.sub(r"[^\w\s.,;:!?¡¿'\"()/%ÁÉÍÓÚÑáéíóú-]", " ", text)
    text = strip_garbage_prefix(text)
    return collapse_spaces(text)