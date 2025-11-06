# ============================================================
# app/db/models.py — Definición de modelos de base de datos (ORM)
# ============================================================
# Este archivo contiene las clases que representan las tablas de la base de datos
# usando SQLAlchemy ORM. Cada clase es un modelo con atributos que mapean columnas.
#
# En este caso, se define el modelo `ExtractionRecord`, que almacena información
# sobre las imágenes procesadas por el OCR (tipo MIME y fecha de creación).
# ============================================================

from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.connection import Base


# ============================================================
# Clase: ExtractionRecord
# ------------------------------------------------------------
# Representa la tabla `extraction_records` en la base de datos MySQL.
# Cada registro almacena:
#   - Un ID único (clave primaria)
#   - El tipo MIME de la imagen procesada (por ejemplo: image/png)
#   - La fecha y hora en que se registró la extracción
# ============================================================
class ExtractionRecord(Base):
    # Nombre exacto de la tabla en la base de datos (debe existir o se creará)
    __tablename__ = "extraction_records"  # Asegúrate de que coincida con la tabla MySQL

    # ------------------------------------------------------------
    # id — Identificador único del registro
    # ------------------------------------------------------------
    # Clave primaria autoincremental que identifica cada extracción OCR.
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # ------------------------------------------------------------
    # image_mime — Tipo de imagen procesada
    # ------------------------------------------------------------
    # Almacena el tipo MIME del archivo procesado (por ejemplo: 'image/png', 'image/jpeg').
    image_mime: Mapped[str] = mapped_column(String(50))

    # ------------------------------------------------------------
    # created_at — Fecha y hora de creación
    # ------------------------------------------------------------
    # Fecha y hora automática del momento en que se insertó el registro.
    # `func.now()` es una función SQL que devuelve la hora actual del servidor.
    created_at: Mapped[str] = mapped_column(DateTime, server_default=func.now())