import os
from datetime import datetime

def save_text_to_disk(text: str) -> str:
    """
    Guarda el texto extraído en un archivo .txt dentro de /data/exports.
    Devuelve la ruta del archivo creada.
    """
    try:
        # Crea carpeta si no existe
        export_dir = os.path.join("data", "exports")
        os.makedirs(export_dir, exist_ok=True)

        # Nombre único por fecha
        now = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(export_dir, f"ocr_{now}.txt")

        # Guardar archivo
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text.strip())

        print(f"💾 Archivo guardado en: {file_path}")
        return os.path.basename(file_path)

    except Exception as e:
        print(f"❌ Error al guardar archivo: {e}")
        raise