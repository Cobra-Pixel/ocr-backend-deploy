import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv
import pymysql

# 🔧 IMPORTANTE: hace que pymysql actúe como MySQLdb
pymysql.install_as_MySQLdb()

# Cargar variables del .env
load_dotenv()

# Leer URL de la base de datos desde las variables de entorno
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("❌ No se encontró DATABASE_URL en el archivo .env")

# Crear motor de conexión
engine = create_engine(DATABASE_URL, echo=True)

# Crear sesión
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Clase base para modelos
class Base(DeclarativeBase):
    pass

# Inicializar DB
def init_db():
    from app.db.models import ExtractionRecord
    Base.metadata.create_all(bind=engine)