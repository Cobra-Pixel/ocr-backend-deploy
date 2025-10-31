from pathlib import Path
from fastapi import APIRouter, Form, HTTPException
from fastapi.responses import FileResponse
from app.db.connection import SessionLocal
from app.db.crud import save_extraction
from app.utils.file_utils import save_text_to_disk

router = APIRouter()

@router.post("/save")
async def save_text(text: str = Form(...), image_mime: str = Form(...)):
    """Guarda texto y metadatos en base de datos y disco."""
    db = SessionLocal()
    try:
        # 🔧 Crea carpeta si no existe
        exports_dir = Path("data/exports")
        exports_dir.mkdir(parents=True, exist_ok=True)

        file_path = save_text_to_disk(text)
        save_extraction(db, image_mime)
        return {"saved": True, "txt_path": file_path}
    except Exception as e:
        db.rollback()
        return {"saved": False, "error": str(e)}
    finally:
        db.close()