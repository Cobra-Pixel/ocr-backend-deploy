# app/routes/ocr_routes.py
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.ocr.service import extract_text_from_image
from app.ocr.cloud_ocr import extract_text_cloud

router = APIRouter()

@router.get("/ping")
def ping():
    return {"status": "ok"}

@router.post("/")  # queda /api/ocr/ por el prefix del main
async def ocr_extract(file: UploadFile = File(...)):
    """OCR local: EasyOCR (+ Tesseract si está disponible)."""
    try:
        result = await extract_text_from_image(file)
        return {
            "text": (result.get("text") or "").strip(),
            "source": "EasyOCR + (opcional Tesseract)",
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cloud/")  # queda /api/ocr/cloud/
async def ocr_extract_cloud(file: UploadFile = File(...)):
    """OCR Cloud: OCR.Space (ideal manuscrito)."""
    try:
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Archivo no es imagen.")
        data = await file.read()
        result = extract_text_cloud(data, file.filename, lang="spa")
        return {
            "text": (result.get("text") or "").strip(),
            "source": "OCR.Space Cloud",
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    except ValueError as e:
        # Errores propios de la API (clave inválida, límites, etc.)
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))