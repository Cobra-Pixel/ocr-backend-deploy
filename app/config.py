# app/config.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

def create_app() -> FastAPI:
    app = FastAPI(title="OCR Extractor API")

    # 🚀 Agrega tus dominios frontend aquí
    origins = [
        "http://localhost:5173",                      # para desarrollo local
        "https://ocr-frontend-ruddy.vercel.app",      # dominio de producción Vercel
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app