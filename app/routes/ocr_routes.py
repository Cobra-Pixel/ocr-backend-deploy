# ============================================================
# app/routes/ocr_routes.py — Rutas principales del módulo OCR
# ============================================================
# Este archivo define los endpoints relacionados con la extracción OCR:
#   - OCR local (EasyOCR + PyTesseract)
#   - OCR en la nube (OCR.Space)
#
# Estas rutas se registran en el `main.py` con el prefijo `/api/ocr`.
# ============================================================

from datetime import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.ocr.service import extract_text_from_image
from app.ocr.cloud_ocr import extract_text_cloud


# ============================================================
# Inicialización del enrutador OCR
# ------------------------------------------------------------
# `APIRouter` permite agrupar las rutas relacionadas con OCR.
# Luego se asocia en el main.py con:
#   app.include_router(ocr_router, prefix="/api/ocr", tags=["OCR"])
# ============================================================
router = APIRouter()


# ============================================================
# Ruta: /api/ocr/ping
# ------------------------------------------------------------
# Endpoint simple de prueba para verificar si el servicio OCR está activo.
# ============================================================
@router.get("/ping")
def ping():
    """Verifica el estado del servicio OCR."""
    return {"status": "ok"}


# ============================================================
# Ruta: POST /api/ocr/
# ------------------------------------------------------------
# Realiza extracción OCR local usando EasyOCR y opcionalmente PyTesseract.
#
# Flujo:
#   1️ Recibe archivo de imagen desde el cliente.
#   2️ Llama a `extract_text_from_image()` para ejecutar el pipeline OCR local.
#   3️ Devuelve texto procesado, fuente y marca de tiempo.
#
# Ideal para: texto impreso, digitalizado o manuscrito legible.
# ============================================================
@router.post("/")  # Ruta efectiva: /api/ocr/
async def ocr_extract(file: UploadFile = File(...)):
    """OCR local: EasyOCR (+ Tesseract si está disponible)."""
    try:
        # Ejecuta el proceso OCR local completo
        result = await extract_text_from_image(file)

        # Devuelve el resultado con metadatos
        return {
            "text": (result.get("text") or "").strip(),
            "source": "EasyOCR + (opcional Tesseract)",
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

    # Errores controlados (por ejemplo: archivo inválido)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Errores inesperados del servidor
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# Ruta: POST /api/ocr/cloud/
# ------------------------------------------------------------
# Realiza extracción OCR en la nube utilizando el servicio OCR.Space.
#
# Flujo:
#   1️ Recibe imagen del cliente.
#   2️ Envía los bytes a `extract_text_cloud()` para ser procesada por OCR.Space.
#   3️ Devuelve el texto reconocido y metadatos.
#
# Ideal para: manuscritos, textos complejos o imágenes grandes,
# donde OCR.Space puede ser más robusto que el OCR local.
# ============================================================
@router.post("/cloud/")  # Ruta efectiva: /api/ocr/cloud/
async def ocr_extract_cloud(file: UploadFile = File(...)):
    """OCR Cloud: OCR.Space (ideal manuscrito)."""
    try:
        # Valida tipo MIME del archivo
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Archivo no es imagen.")

        # Lee contenido binario de la imagen
        data = await file.read()

        # Procesa mediante OCR.Space
        result = extract_text_cloud(data, file.filename, lang="spa")

        # Devuelve texto extraído y fuente
        return {
            "text": (result.get("text") or "").strip(),
            "source": "OCR.Space Cloud",
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

    # Errores específicos de la API OCR.Space
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Propaga errores HTTP ya manejados
    except HTTPException:
        raise

    # Errores inesperados del servidor
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))