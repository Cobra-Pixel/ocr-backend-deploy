import cv2
import numpy as np

def denoise_and_contrast(img: np.ndarray) -> np.ndarray:
    """Reduce ruido y aumenta contraste con CLAHE + normalización."""
    img = cv2.fastNlMeansDenoising(img, None, 10, 7, 21)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    img = clahe.apply(img)
    img = cv2.normalize(img, None, 0, 255, cv2.NORM_MINMAX)
    return img

def binarize_and_clean(img: np.ndarray) -> np.ndarray:
    """Binariza y limpia líneas finas (mejor para notas de libreta)."""
    thresh = cv2.adaptiveThreshold(
        img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV, 15, 11
    )
    # Remueve líneas de libreta horizontales con morfología
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
    remove_horizontal = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=1)
    cleaned = cv2.subtract(thresh, remove_horizontal)
    cleaned = cv2.medianBlur(cleaned, 3)
    return cleaned

def deskew_image(img: np.ndarray) -> np.ndarray:
    """Corrige inclinación leve del texto."""
    coords = np.column_stack(np.where(img > 0))
    angle = 0.0
    if coords.size > 0:
        rect = cv2.minAreaRect(coords)
        angle = rect[-1]
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
    (h, w) = img.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    return cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

def enhance_sharpness(img: np.ndarray) -> np.ndarray:
    """Aumenta nitidez y suaviza bordes de trazos."""
    kernel_sharp = np.array([
        [-1, -1, -1],
        [-1,  9, -1],
        [-1, -1, -1]
    ])
    sharpened = cv2.filter2D(img, -1, kernel_sharp)
    return cv2.GaussianBlur(sharpened, (1, 1), 0)