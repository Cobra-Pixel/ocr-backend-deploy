# ============================================================
#  app/config.py — Configuración general de la aplicación FastAPI
# ============================================================
# Este módulo define la función create_app(), encargada de:
#   - Crear la instancia principal de FastAPI.
#   - Configurar los permisos CORS para permitir la comunicación
#     entre el backend (FastAPI) y los frontends (por ejemplo, Vercel o localhost).
# ============================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os


# ============================================================
#  Función principal: create_app()
# ------------------------------------------------------------
# Crea una instancia de FastAPI y aplica configuraciones de seguridad
# y comunicación, como los orígenes permitidos (CORS).
# ============================================================
def create_app() -> FastAPI:
    # Crea la app principal con un título descriptivo
    app = FastAPI(title="OCR Extractor API")

    # ------------------------------------------------------------
    #  Lista inicial de dominios permitidos
    # ------------------------------------------------------------
    # Estos dominios son los que pueden comunicarse con el backend.
    # Incluye el entorno local de desarrollo y los despliegues en Vercel.
    origins = [
        "http://localhost:5173",  # Desarrollo local (vite dev server)
        "https://ocr-frontend-ruddy.vercel.app",  # Versión anterior desplegada en Vercel
        "https://ocr-frontend-253ad4nqb-cobra-pixel.vercel.app",  # Nuevo dominio actual de producción
    ]

    # ------------------------------------------------------------
    #  Agregar orígenes dinámicos desde variables de entorno
    # ------------------------------------------------------------
    # Render o cualquier otro entorno de producción puede definir
    # la variable ALLOWED_ORIGINS para añadir dominios extra.
    env_origins = os.getenv("ALLOWED_ORIGINS")
    if env_origins:
        for origin in env_origins.split(","):
            o = origin.strip()
            if o not in origins:
                origins.append(o)  # Evita duplicados

    # ------------------------------------------------------------
    #  Configurar Middleware CORS
    # ------------------------------------------------------------
    # El middleware CORS permite solicitudes cruzadas entre
    # el backend (FastAPI) y el frontend (React/Vercel).
    # Aquí se define qué dominios, métodos y cabeceras son válidos.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,          # Dominios permitidos
        allow_credentials=True,         # Permite cookies o tokens
        allow_methods=["*"],            # Permite todos los métodos (GET, POST, etc.)
        allow_headers=["*"],            # Permite cualquier cabecera HTTP
    )

    # ------------------------------------------------------------
    #  Mensaje informativo en consola
    # ------------------------------------------------------------
    # Imprime los dominios habilitados al iniciar el servidor.
    print(f" CORS habilitado para: {origins}")

    # Devuelve la aplicación ya configurada
    return app