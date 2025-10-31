# app/routes/ocr_routes.py
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.ocr.service import extract_text_from_image
from app.ocr.cloud_ocr import extract_text_cloud

router = APIRouter()

@router.get("/ping")
def ping():
    return {"status": "ok"}

@router.post("/")  # ✅ coincide con prefix /api/ocr
async def ocr_extract(file: UploadFile = File(...)):
    """Extrae texto con EasyOCR + PyTesseract."""
    try:
        result = await extract_text_from_image(file)
        return {
            "text": result.get("text", "").strip(),
            "source": "EasyOCR + PyTesseract",
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cloud/")  # ✅ agrega barra final
async def ocr_extract_cloud(file: UploadFile = File(...)):
    """Extrae texto manuscrito usando OCR.Space Cloud."""
    try:
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Archivo no es imagen.")
        data = await file.read()
        text = extract_text_cloud(data, file.filename, lang="spa")

        return {
            "text": text.strip(),
            "source": "OCR.Space Cloud",
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))