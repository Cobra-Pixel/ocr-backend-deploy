from app.db.models import ExtractionRecord
from sqlalchemy.orm import Session

def save_extraction(db: Session, image_mime: str):
    """Guarda un nuevo registro de extracción en la base de datos."""
    try:
        rec = ExtractionRecord(image_mime=image_mime)
        db.add(rec)
        db.commit()
        db.refresh(rec)
        print(f"✅ Guardado en DB: id={rec.id}, mime={rec.image_mime}")
        return rec
    except Exception as e:
        db.rollback()
        print(f"❌ Error guardando en DB: {e}")
        raise