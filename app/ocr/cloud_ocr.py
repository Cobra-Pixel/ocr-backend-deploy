# ============================================================
# app/ocr/cloud_ocr.py — Integración con la API OCR.Space
# ============================================================
# Este módulo se encarga de enviar imágenes al servicio OCR.Space,
# recibir el texto reconocido y manejar errores comunes.
#
# Incluye una función auxiliar que reduce el tamaño de la imagen si
# excede el límite permitido (~1.5 MB), para optimizar el envío.
# ============================================================

import os
import io
import requests
from PIL import Image
from dotenv import load_dotenv


# ============================================================
# Carga de variables de entorno
# ------------------------------------------------------------
# Solo se usa en desarrollo local; en Render, las variables se
# definen directamente en el panel de entorno.
# ============================================================
load_dotenv()


# ============================================================
# Configuración base
# ------------------------------------------------------------
# - API_KEY: clave personal para usar el servicio OCR.Space.
# - OCR_URL: endpoint oficial del servicio.
# ============================================================
API_KEY = os.getenv("OCR_SPACE_API_KEY")
OCR_URL = "https://api.ocr.space/parse/image"


# ============================================================
# Función: _resize_image_if_needed()
# ------------------------------------------------------------
# Reescala imágenes grandes para que cumplan con los límites de tamaño
# de la API OCR.Space (~1.5 MB). También convierte la imagen a JPEG
# con calidad controlada para reducir peso sin perder demasiada nitidez.
#
# Parámetros:
#   - image_bytes (bytes): imagen en formato binario.
#   - max_dim (int): tamaño máximo permitido para ancho o alto.
#
# Retorna:
#   - bytes: imagen comprimida y reescalada si fue necesario.
# ============================================================
def _resize_image_if_needed(image_bytes: bytes, max_dim: int = 1280) -> bytes:
    """
    Reduce resolución si la imagen es muy grande (OCR.Space tiene límite de ~1.5MB).
    """
    try:
        # Carga la imagen desde bytes
        img = Image.open(io.BytesIO(image_bytes))

        # Si alguna dimensión excede el límite, se reduce proporcionalmente
        if max(img.size) > max_dim:
            ratio = max_dim / float(max(img.size))
            new_size = tuple(int(x * ratio) for x in img.size)
            img = img.resize(new_size, Image.LANCZOS)

        # Convierte la imagen a formato JPEG optimizado
        buf = io.BytesIO()
        img.convert("RGB").save(buf, format="JPEG", quality=85)

        # Devuelve los bytes comprimidos
        return buf.getvalue()

    except Exception:
        # Si ocurre un error, devuelve la imagen original sin modificar
        return image_bytes


# ============================================================
# Función: extract_text_cloud()
# ------------------------------------------------------------
# Envía una imagen a la API OCR.Space para extraer el texto contenido.
#
# Flujo:
#   1. Comprueba que la API_KEY esté configurada.
#   2. Reescala la imagen si es demasiado grande.
#   3. Envía la solicitud HTTP POST con la imagen y los parámetros.
#   4. Procesa la respuesta JSON y extrae el texto.
#   5. Maneja posibles errores o respuestas vacías.
#
# Parámetros:
#   - image_bytes (bytes): contenido de la imagen en binario.
#   - filename (str): nombre del archivo (usado solo para el envío).
#   - lang (str): idioma del texto en la imagen (por defecto "spa").
#
# Retorna:
#   - dict: contiene el texto reconocido bajo la clave "text".
# ============================================================
def extract_text_cloud(image_bytes: bytes, filename: str, lang: str = "spa") -> dict:
    """
    Envía imagen a OCR.Space y devuelve el texto extraído o mensaje de error.
    """
    # ------------------------------------------------------------
    # 1️ Validar existencia de clave API
    # ------------------------------------------------------------
    if not API_KEY:
        raise ValueError(" Falta configurar OCR_SPACE_API_KEY en Render.")

    # ------------------------------------------------------------
    # 2️ Reescalar y comprimir imagen si es necesario
    # ------------------------------------------------------------
    safe_bytes = _resize_image_if_needed(image_bytes)

    # Verifica tamaño final (OCR.Space rechaza > 1.5 MB)
    if len(safe_bytes) > 1_500_000:
        raise ValueError(" Imagen demasiado grande incluso tras compresión (límite 1.5 MB).")

    # ------------------------------------------------------------
    # 3️ Preparar datos para la petición HTTP
    # ------------------------------------------------------------
    files = {"file": (filename or "image.jpg", safe_bytes, "image/jpeg")}
    data = {
        "apikey": API_KEY,
        "language": lang,
        "isOverlayRequired": False,
        "OCREngine": 2,          # Motor avanzado OCR.Space (más preciso)
        "scale": True,
        "detectOrientation": True,
    }

    # ------------------------------------------------------------
    # 4️ Enviar petición POST al servicio OCR.Space
    # ------------------------------------------------------------
    try:
        resp = requests.post(OCR_URL, files=files, data=data, timeout=60)
        resp.raise_for_status()  # Lanza excepción si hubo error HTTP
        result = resp.json()     # Convierte respuesta JSON en dict
    except Exception as e:
        raise ValueError(f" Error al conectar con OCR.Space: {e}")

    # ------------------------------------------------------------
    # 5️ Manejar errores específicos reportados por OCR.Space
    # ------------------------------------------------------------
    if result.get("IsErroredOnProcessing"):
        err_msg = result.get("ErrorMessage") or result.get("ErrorDetails") or ["Error desconocido"]
        if isinstance(err_msg, list):
            err_msg = err_msg[0]
        raise ValueError(f" OCR.Space rechazó la imagen: {err_msg}")

    # ------------------------------------------------------------
    # 6️ Extraer texto del resultado JSON
    # ------------------------------------------------------------
    parsed = result.get("ParsedResults") or []
    text = (parsed[0].get("ParsedText", "") if parsed else "").strip()

    if not text:
        raise ValueError(" No se detectó texto en la imagen (OCR.Space devolvió vacío).")

    # ------------------------------------------------------------
    # 7 Devolver texto reconocido
    # ------------------------------------------------------------
    return {"text": text}