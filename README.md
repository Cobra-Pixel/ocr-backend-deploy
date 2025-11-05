# OCR Extracor Backend (Fast API + EasyOCR + PyTesseract)
Este es el **backend oficial del proyecto OCR Extractor**, una aplicacion web que permite extraer texto desde imagenes **impresas o manuscritas**, combinando modelos **EasyOCR**, **PyTeesseract** y la **API de OCR.Space Cloud**.

Desarrollado con **FastAPI**, **SQLAlchemy** y **MySQL (Railway)**, y desplegado en **Render**.

## Enlaces de despliegue
| Servicio | URL |
|----------|-----|
**Frontend (Vercel)** [https://ocr-frontend-ruddy.vercel.app] (https://ocr-frontend-ruddy.vercel.app)
**Backend (Render)** [https://ocr-backend-deploy.onrender.com] (https://ocr-backend-deploy.onrender.com)
**Base de datos (Railway)** Conexion privada MySQL

## Tecnologias principales
- **Python 3.12**
- **FastAPI**
- **EasyOCR**
- **PyTessercat**
- **OCR.Space Cloud API**
- **SQLAlchemy + MySQL (Railway)**
- **Render** (backend)
- **Vercel** (frontend)

## Variables de entorno (.env)
Ejemplo de archivo '.env' local o variables configuradas en Render:

'Bash'
DATABASE_URL=mysql+pymysql://usuario:contraseña@host:puerto/nombreDB
OCR_SPACE_API_KEY=MI_API_KEY_DE_OCR_SPACE
ALLOWED_ORIGINS=https://ocr-frontend-ruddy.vercel.app, http://localhost:5173
SECRET_KEY=SEPA
PORT=8000

## Instalacion local
# Clonar el repositorio
git clone https://github.com/Cobra-Pixel/ocr-backend-deploy.git
cd ocr-backend-deploy
# Crear entorno virtual
python -m venv .venv
source .venv/Scripts/activate  # En Windows
# O bien 
source .venv/bin/activate # En Linux o Mac
# Instalar dependencias
pip install -r requirements.txt
# Ejecutar el servidor local
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
# Luego abrir navegador
http://127.0.0.1:8000/docs

# Despliegue
Render (Backend)
Configurar variables de entorno (DATABASE_URL, OCR_SPACE_API_KEY, ALLOWED_ORIGINS, etc.)
Usar este comando al inicio
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Railway (Base de datos)
Crear una base de datos MySQL
Copiar URL y pegarla en DATABASE_URL

# OCR.Space API
Obtener API Key gratuita en
https://ocr.space/ocrapi

## Endpoints principales
  # Metodo      # Ruta                       # Descripcion
- **POST**    **/api/ocr/**                  **Extrae texto con EasyOCR + PyTesseract**
- **POST**    **/api/ocr/cloud/**            **Extrae texto con OCR.Space Cloud**
- **POST**    **/api/save/**                 **Guarda el texto en la base de datos**
- **GET**     **/api/download/{filename}**   **Descarga el archivo .txt generado**

## Licencia
Proyecto de uso educativo y lobre bajo licencia MIT.
Desarrollado por Cobra-Pixel
© 2025 - OCR Extractor 

## Creditos y soporte
Si te resulta util, deja una estrellita en el repositorio y comparte tus sugerencias.
Puedes abrir un issue o PR en https://github.com/Cobra-Pixel/ocr-backend-deploy
