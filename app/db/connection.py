import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv
import pymysql  # ✅ usamos PyMySQL como reemplazo de MySQLdb

# 👇 esta línea es la clave
pymysql.install_as_MySQLdb()

# Cargar variables de entorno
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("❌ No se encontró DATABASE_URL en el archivo .env")

# Crear el engine de SQLAlchemy
engine = create_engine(DATABASE_URL, echo=True)  # echo=True mostrará queries SQL

# Sesión
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos
class Base(DeclarativeBase):
    pass

# Inicialización del modelo
def init_db():
    from app.db.models import ExtractionRecord
    Base.metadata.create_all(bind=engine)