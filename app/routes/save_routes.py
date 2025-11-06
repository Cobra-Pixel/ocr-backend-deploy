# ============================================================
# app/routes/save_routes.py — Rutas de guardado y descarga
# ============================================================
# Este módulo define las rutas para:
#   - Guardar texto OCR y sus metadatos en base de datos y disco.
#   - Descargar archivos .txt previamente guardados.
#
# Se registra en `main.py` con el prefijo `/api`, por lo tanto:
#   - POST  → /api/save/
#   - GET   → /api/download/{filename}
# ============================================================

from pathlib import Path
from fastapi import APIRouter, Form, HTTPException
from fastapi.responses import FileResponse
from app.db.connection import SessionLocal
from app.db.crud import save_extraction
from app.utils.file_utils import save_text_to_disk


# ============================================================
# Inicialización del enrutador
# ------------------------------------------------------------
# `APIRouter` permite agrupar las rutas relacionadas con el
# almacenamiento y gestión de archivos extraídos por el OCR.
# ============================================================
router = APIRouter()


# ============================================================
# Ruta: POST /api/save/
# ------------------------------------------------------------
# Guarda el texto OCR y los metadatos asociados:
#   - Inserta un registro en la base de datos (usando save_extraction()).
#   - Guarda el contenido textual en un archivo local (.txt).
#
# Flujo:
#   1️ Recibe texto y tipo MIME del formulario.
#   2️ Llama a `save_text_to_disk()` → genera archivo .txt en /data/exports.
#   3️ Llama a `save_extraction()` → guarda registro en la base de datos.
#   4️ Devuelve estado de éxito o error.
# ============================================================
@router.post("/save/")  # sin /api/, porque el prefijo /api ya se aplica en main.py
async def save_text(text: str = Form(...), image_mime: str = Form(...)):
    """Guarda texto y metadatos en base de datos y disco."""
    db = SessionLocal()
    try:
        # 1️ Guarda el texto procesado en un archivo .txt dentro de /data/exports
        file_path = save_text_to_disk(text)

        # 2️ Registra la extracción en la base de datos (MySQL)
        save_extraction(db, image_mime)

        # 3️ Devuelve confirmación y ruta del archivo generado
        return {"saved": True, "txt_path": file_path}

    except Exception as e:
        # En caso de error, revierte transacción para evitar datos corruptos
        db.rollback()
        return {"saved": False, "error": str(e)}

    finally:
        # Cierra la sesión de base de datos en todos los casos
        db.close()


# ============================================================
# Ruta: GET /api/download/{filename}
# ------------------------------------------------------------
# Permite descargar un archivo .txt generado previamente por el OCR.
#
# Flujo:
#   1️ Busca el archivo en la ruta /data/exports/{filename}.
#   2️ Verifica existencia; si no existe, devuelve 404.
#   3️ Si existe, lo envía como respuesta (tipo text/plain).
# ============================================================
@router.get("/download/{filename}")  # sin /api/, el prefijo ya está definido en main.py
async def download_file(filename: str):
    """Devuelve el archivo .txt guardado en /data/exports."""
    # Ruta base del proyecto → sube tres niveles desde este archivo
    base_dir = Path(__file__).resolve().parent.parent.parent

    # Construye la ruta completa al archivo exportado
    file_path = base_dir / "data" / "exports" / filename

    # 1️ Verifica si el archivo existe
    if not file_path.exists():
        print(f" Archivo no encontrado: {file_path}")
        raise HTTPException(status_code=404, detail="Archivo no encontrado")

    # 2️ Si existe, devuelve el archivo como respuesta
    print(f" Archivo encontrado: {file_path}")
    return FileResponse(
        path=str(file_path),
        media_type="text/plain",
        filename=filename
    )