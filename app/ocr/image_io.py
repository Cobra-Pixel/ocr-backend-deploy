import numpy as np
from io import BytesIO
from PIL import Image

def bytes_to_grayscale(image_bytes: bytes) -> np.ndarray:
    """Convierte bytes de imagen en array numpy en escala de grises."""
    image = Image.open(BytesIO(image_bytes)).convert("L")
    return np.array(image)