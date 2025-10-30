# Inicializa EasyOCR y Tesseract
import easyocr

# Inicialización global del lector OCR
reader = easyocr.Reader(['es', 'en'], gpu=False, recog_network='latin_g2')