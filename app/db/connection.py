# ============================================================
#  app/db/connection.py — Configuración de conexión a la base de datos
# ============================================================
# Este módulo define la conexión entre la aplicación FastAPI y MySQL,
# usando SQLAlchemy como ORM y variables de entorno para seguridad.
# También inicializa la base de datos y genera las tablas automáticamente.
# ============================================================

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv
import pymysql


# ============================================================
#  Configuración del conector MySQL
# ------------------------------------------------------------
# PyMySQL se utiliza como driver compatible con MySQLdb
# (necesario para que SQLAlchemy pueda comunicarse con MySQL).
# ============================================================
pymysql.install_as_MySQLdb()


# ============================================================
#  Carga de variables de entorno (.env)
# ------------------------------------------------------------
# Se usa python-dotenv para leer las credenciales desde el archivo .env,
# garantizando que las claves y contraseñas no se guarden directamente en el código.
# ============================================================
load_dotenv()


# ============================================================
#  URL de conexión a la base de datos
# ------------------------------------------------------------
# Ejemplo de variable en .env:
# DATABASE_URL=mysql+pymysql://usuario:contraseña@host:puerto/nombre_bd
# ============================================================
DATABASE_URL = os.getenv("DATABASE_URL")

# Si no existe la variable, se lanza un error crítico para evitar fallos silenciosos
if not DATABASE_URL:
    raise ValueError(" No se encontró DATABASE_URL en el archivo .env")


# ============================================================
#  Creación del motor de conexión (Engine)
# ------------------------------------------------------------
# `create_engine()` crea la conexión hacia MySQL.
#   - echo=False: oculta logs SQL (puede activarse para depuración).
#   - pool_pre_ping=True: evita desconexiones por inactividad.
# ============================================================
engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)


# ============================================================
#  Sesión local (SessionLocal)
# ------------------------------------------------------------
# Crea una clase de sesión que se usará en cada transacción con la DB.
#   - autocommit=False → los cambios deben confirmarse manualmente.
#   - autoflush=False  → evita que SQLAlchemy envíe cambios automáticamente.
# ============================================================
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ============================================================
#  Clase base para los modelos
# ------------------------------------------------------------
# `DeclarativeBase` permite definir clases modelo (tablas) usando SQLAlchemy ORM.
# Todas las clases de modelo heredarán de esta base.
# ============================================================
class Base(DeclarativeBase):
    pass


# ============================================================
#  Función init_db()
# ------------------------------------------------------------
# Inicializa la base de datos creando las tablas definidas en los modelos.
# Se importa `ExtractionRecord` para asegurar que esté registrado en metadata.
# ============================================================
def init_db():
    from app.db.models import ExtractionRecord  # Import diferido para evitar dependencias circulares
    Base.metadata.create_all(bind=engine)