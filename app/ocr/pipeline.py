import cv2
from .image_io import bytes_to_grayscale
from .image_filters import (
    denoise_and_contrast,
    binarize_and_clean,
    deskew_image,
    enhance_sharpness
)

def preprocess_image_bytes(image_bytes: bytes):
    """
    Flujo completo del preprocesamiento OCR.
    Combina limpieza, contraste, binarización, deskew y escalado final.
    """
    # 1️⃣ Bytes → escala de grises
    img = bytes_to_grayscale(image_bytes)

    # 2️⃣ Limpieza y contraste
    img = denoise_and_contrast(img)

    # 3️⃣ Umbral + limpieza morfológica
    img = binarize_and_clean(img)

    # 4️⃣ Deskew
    img = deskew_image(img)

    # 5️⃣ Nitidez final
    img = enhance_sharpness(img)

    # 6️⃣ Escalado final 2x
    img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

    # 7️⃣ Binarización suave final
    _, img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    return img