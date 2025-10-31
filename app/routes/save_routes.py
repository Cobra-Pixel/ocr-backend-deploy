from pathlib import Path
from fastapi import APIRouter, Form, HTTPException
from fastapi.responses import FileResponse
from app.db.connection import SessionLocal
from app.db.crud import save_extraction
from app.utils.file_utils import save_text_to_disk

router = APIRouter()

@router.post("/api/save/")
async def save_text(text: str = Form(...), image_mime: str = Form(...)):
    """Guarda texto y metadatos en base de datos y disco."""
    db = SessionLocal()
    try:
        file_path = save_text_to_disk(text)
        save_extraction(db, image_mime)
        return {"saved": True, "txt_path": file_path}
    except Exception as e:
        db.rollback()
        return {"saved": False, "error": str(e)}
    finally:
        db.close()


@router.get("/api/download/{filename}")
async def download_file(filename: str):
    """Devuelve el archivo .txt guardado en /data/exports."""
    base_dir = Path(__file__).resolve().parent.parent.parent
    file_path = base_dir / "data" / "exports" / filename

    if not file_path.exists():
        print(f"⚠️ Archivo no encontrado: {file_path}")
        raise HTTPException(status_code=404, detail="Archivo no encontrado")

    print(f"✅ Archivo encontrado: {file_path}")
    return FileResponse(path=str(file_path), media_type="text/plain", filename=filename)