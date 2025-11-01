# app/config.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

def create_app() -> FastAPI:
    app = FastAPI(title="OCR Extractor API")

    # 🚀 Dominios permitidos
    origins = [
        "http://localhost:5173",  # desarrollo local
        "https://ocr-frontend-ruddy.vercel.app",  # build anterior
        "https://ocr-frontend-253ad4nqb-cobra-pixel.vercel.app",  # nuevo dominio actual de Vercel
    ]

    # Permitir también los agregados por variable ALLOWED_ORIGINS
    env_origins = os.getenv("ALLOWED_ORIGINS")
    if env_origins:
        for origin in env_origins.split(","):
            o = origin.strip()
            if o not in origins:
                origins.append(o)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    print(f"🔐 CORS habilitado para: {origins}")
    return app