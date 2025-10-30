import os
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from dotenv import load_dotenv

# Cargar variables del archivo .env (solo en local)
load_dotenv()

def create_app() -> FastAPI:
    """Crea e inicializa la app con configuración base y CORS."""
    app = FastAPI(title="OCR Extractor API")

    allowed = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[o.strip() for o in allowed],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app