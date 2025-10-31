# app/main.py
from fastapi import FastAPI
from app.config import create_app
from app.db.connection import init_db
from app.routes.ocr_routes import router as ocr_router
from app.routes.save_routes import router as save_router

app: FastAPI = create_app()

# 🔹 DB al arrancar (que no tumbe la app si falla)
@app.on_event("startup")
def on_startup():
    try:
        init_db()
    except Exception as e:
        # Loguea pero no detiene el arranque
        print(f"[WARN] DB init skipped/failed: {e}")

# 🔹 Rutas
app.include_router(ocr_router, prefix="/api/ocr", tags=["OCR"])
app.include_router(save_router, prefix="/api", tags=["Save"])

@app.get("/")
def root():
    return {"message": "OCR Extractor API running ✅"}