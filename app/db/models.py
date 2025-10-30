from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.connection import Base

class ExtractionRecord(Base):
    __tablename__ = "extraction_records"  # ⚠️ debe existir en MySQL

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    image_mime: Mapped[str] = mapped_column(String(50))
    created_at: Mapped[str] = mapped_column(DateTime, server_default=func.now())