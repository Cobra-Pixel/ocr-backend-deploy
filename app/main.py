# app/main.py
from fastapi import FastAPI
from sqlalchemy import text
from app.config import create_app
from app.db.connection import init_db, SessionLocal
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

# 🔹 Rutas principales
app.include_router(ocr_router, prefix="/api/ocr", tags=["OCR"])
app.include_router(save_router, prefix="/api", tags=["Save"])

# 🔹 Ruta raíz
@app.get("/")
def root():
    return {"message": "OCR Extractor API running ✅"}

# 🚀 Ruta de prueba para verificar conexión a MySQL
@app.get("/api/test-db")
def test_db():
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return {"status": "✅ Conexión a MySQL exitosa"}
    except Exception as e:
        return {"status": "❌ Error al conectar a MySQL", "detail": str(e)}