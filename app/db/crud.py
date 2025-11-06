# ============================================================
# Módulo CRUD — Guardar registros de extracción OCR en la base de datos
# ============================================================
# Este módulo contiene funciones para interactuar con la base de datos,
# específicamente para registrar información relacionada con las extracciones
# realizadas por el sistema OCR (por ejemplo, el tipo de imagen procesada).
# ============================================================

from app.db.models import ExtractionRecord
from sqlalchemy.orm import Session


# ============================================================
# Función: save_extraction()
# ------------------------------------------------------------
# Guarda un nuevo registro en la tabla `extraction_records` (o equivalente).
# Cada registro contiene información sobre una extracción OCR realizada,
# incluyendo el tipo MIME de la imagen (por ejemplo: image/png, image/jpeg).
#
# Parámetros:
#   - db: objeto de sesión SQLAlchemy activo.
#   - image_mime (str): tipo MIME de la imagen procesada.
#
# Retorna:
#   - El objeto `ExtractionRecord` recién creado, con su ID generado.
# ============================================================
def save_extraction(db: Session, image_mime: str):
    """Guarda un nuevo registro de extracción en la base de datos."""
    try:
        # Crea un nuevo registro con el tipo MIME recibido
        rec = ExtractionRecord(image_mime=image_mime)

        # Agrega el registro a la sesión actual
        db.add(rec)

        # Confirma (guarda) los cambios en la base de datos
        db.commit()

        # Actualiza el objeto `rec` con los datos finales (por ejemplo, el ID asignado)
        db.refresh(rec)

        # Mensaje informativo en consola
        print(f" Guardado en DB: id={rec.id}, mime={rec.image_mime}")

        # Devuelve el registro recién guardado
        return rec

    except Exception as e:
        # En caso de error, revierte la transacción para evitar corrupción de datos
        db.rollback()
        print(f" Error guardando en DB: {e}")
        # Re-lanza el error para manejarlo desde el nivel superior
        raise