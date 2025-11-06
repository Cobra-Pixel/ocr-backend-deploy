# ============================================================
# app/main.py — Punto de entrada principal del backend OCR
# ============================================================
# Este archivo inicializa la aplicación FastAPI, configura la base de datos,
# registra las rutas del sistema y arranca el servidor (local o en Render).
# ============================================================

import os
from fastapi import FastAPI
from sqlalchemy import text
from app.config import create_app
from app.db.connection import init_db, SessionLocal
from app.routes.ocr_routes import router as ocr_router
from app.routes.save_routes import router as save_router


# ============================================================
#  Crear instancia principal de la aplicación FastAPI
# ------------------------------------------------------------
# La función create_app() define la configuración base de la app
# (por ejemplo: CORS, middlewares, metadatos, etc.)
# ============================================================
app: FastAPI = create_app()


# ============================================================
#  Evento al iniciar el servidor (startup)
# ------------------------------------------------------------
# Esta función se ejecuta automáticamente cuando la app arranca.
# Inicializa la conexión con la base de datos MySQL mediante SQLAlchemy.
# ============================================================
@app.on_event("startup")
def on_startup():
    try:
        # Llama al inicializador de la base de datos
        init_db()
        print(" Conexión a DB inicializada correctamente.")
    except Exception as e:
        # En caso de error, muestra advertencia en consola
        print(f"[WARN] Error iniciando DB: {e}")


# ============================================================
#  Registro de rutas principales (Routers)
# ------------------------------------------------------------
# Se importan y asocian los routers desde los módulos de rutas:
#   - /api/ocr → Lógica del OCR (procesamiento de imágenes)
#   - /api     → Guardado de datos, texto, resultados, etc.
# ============================================================
app.include_router(ocr_router, prefix="/api/ocr", tags=["OCR"])
app.include_router(save_router, prefix="/api", tags=["Save"])


# ============================================================
#  Ruta raíz (endpoint base)
# ------------------------------------------------------------
# Devuelve un mensaje simple para confirmar que la API está corriendo.
# Se puede usar para pruebas rápidas o monitoreo.
# ============================================================
@app.get("/")
def root():
    return {"message": "OCR Extractor API running "}


# ============================================================
#  Ruta de prueba de conexión a la base de datos
# ------------------------------------------------------------
# Permite verificar si la conexión a MySQL está activa.
# Ejecuta una consulta SQL mínima ("SELECT 1").
# ============================================================
@app.get("/api/test-db")
def test_db():
    try:
        # Crea una sesión temporal a la base de datos
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return {"status": " Conexión a MySQL exitosa"}
    except Exception as e:
        # Captura errores y los devuelve como respuesta JSON
        return {"status": " Error al conectar a MySQL", "detail": str(e)}


# ============================================================
#  Punto de entrada para Render o ejecución local directa
# ------------------------------------------------------------
# Render utiliza esta sección para iniciar el servidor con uvicorn.
# Si ejecutas "python app/main.py" manualmente, este bloque arranca el backend.
# ============================================================
if __name__ == "__main__":
    import uvicorn

    # Obtiene el puerto desde variables de entorno (Render lo define automáticamente)
    port = int(os.getenv("PORT", 8000))

    # Inicia el servidor en modo producción o desarrollo
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)