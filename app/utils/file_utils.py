# ============================================================
# app/utils/file_utils.py — Utilidades para manejo de archivos OCR
# ============================================================
# Este módulo se encarga de guardar los textos extraídos por el OCR
# en archivos de texto (.txt) dentro del directorio /data/exports.
#
# Cada archivo se guarda con un nombre único basado en la fecha y hora
# (por ejemplo: ocr_20251106_034530.txt).
# ============================================================

import os
from datetime import datetime


# ============================================================
# Función: save_text_to_disk()
# ------------------------------------------------------------
# Guarda un texto recibido como parámetro en un archivo .txt dentro
# del directorio `/data/exports`, creando la carpeta si no existe.
#
# Flujo:
#   1️ Crea el directorio /data/exports si no existe.
#   2️ Genera un nombre único basado en la hora UTC actual.
#   3️ Escribe el texto en un archivo con codificación UTF-8.
#   4️ Devuelve solo el nombre del archivo generado.
#
# Parámetros:
#   - text (str): contenido textual que se desea guardar.
#
# Retorna:
#   - str: nombre del archivo creado (por ejemplo: "ocr_20251106_034530.txt").
#
# Lanza:
#   - Exception: si ocurre algún error durante el proceso de guardado.
# ============================================================
def save_text_to_disk(text: str) -> str:
    """
    Guarda el texto extraído en un archivo .txt dentro de /data/exports.
    Devuelve la ruta del archivo creada.
    """
    try:
        # 1️ Crea el directorio "data/exports" si aún no existe
        export_dir = os.path.join("data", "exports")
        os.makedirs(export_dir, exist_ok=True)

        # 2️ Genera un nombre único basado en la hora actual (UTC)
        now = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(export_dir, f"ocr_{now}.txt")

        # 3️ Escribe el texto en el archivo con codificación UTF-8
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text.strip())

        # 4️ Mensaje de confirmación en consola
        print(f" Archivo guardado en: {file_path}")

        # Devuelve el nombre base del archivo (sin la ruta completa)
        return os.path.basename(file_path)

    except Exception as e:
        # En caso de error, muestra en consola y propaga la excepción
        print(f" Error al guardar archivo: {e}")
        raise