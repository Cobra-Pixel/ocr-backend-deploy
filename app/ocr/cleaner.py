# ============================================================
# Módulo de limpieza de texto — Funciones de preprocesamiento OCR
# ============================================================
# Este módulo contiene funciones para limpiar y normalizar texto extraído
# mediante OCR (reconocimiento óptico de caracteres).
#
# Su propósito es eliminar caracteres no deseados, normalizar acentos,
# reducir ruido visual, y dejar el texto en un formato más legible y coherente.
# ============================================================

import re
import unicodedata


# ============================================================
# Función: normalize_text()
# ------------------------------------------------------------
# Normaliza el texto aplicando compatibilidad Unicode (NFKC) y reemplaza
# caracteres tipográficos inusuales que suelen aparecer en documentos escaneados,
# como ligaduras (ﬁ, ﬂ) o guiones largos (—, –).
#
# Parámetros:
#   - text (str): texto a normalizar.
#
# Retorna:
#   - Texto con caracteres estandarizados y símbolos corregidos.
# ============================================================
def normalize_text(text: str) -> str:
    """Normaliza caracteres y reemplaza símbolos raros."""
    # Convierte el texto a su forma canónica compatible (NFKC)
    text = unicodedata.normalize("NFKC", text)

    # Reemplaza ligaduras y guiones especiales por sus equivalentes ASCII
    return (
        text.replace("ﬁ", "fi")
            .replace("ﬂ", "fl")
            .replace("—", "-")
            .replace("–", "-")
    )


# ============================================================
# Función: strip_garbage_prefix()
# ------------------------------------------------------------
# Elimina líneas que contengan demasiados símbolos o poco texto legible,
# normalmente resultado de ruido visual o errores del OCR.
#
# El proceso:
#   1. Divide el texto en líneas y elimina espacios extra.
#   2. Calcula la proporción de caracteres válidos por línea.
#   3. Filtra líneas con <40% de caracteres alfanuméricos o útiles.
#   4. Limpia caracteres no deseados al inicio de las líneas.
#   5. Devuelve solo las líneas con contenido textual real.
#
# Parámetros:
#   - text (str): texto crudo del OCR.
#
# Retorna:
#   - Texto limpio sin líneas basura.
# ============================================================
def strip_garbage_prefix(text: str) -> str:
    """Elimina líneas con símbolos no alfanuméricos o ruido."""
    # Divide el texto en líneas y elimina espacios iniciales/finales
    lines = [ln.strip() for ln in text.splitlines()]
    clean_lines = []

    for ln in lines:
        if not ln:
            continue  # Salta líneas vacías

        # Calcula la proporción de caracteres válidos
        good = sum(
            ch.isalnum() or ch.isspace() or ch in ".,;:!?¡¿'\"()-/%"
            for ch in ln
        )

        # Filtra líneas con muy poco contenido útil
        if len(ln) == 0 or good / max(1, len(ln)) < 0.4:
            continue

        # Elimina caracteres no alfabéticos al inicio
        ln = re.sub(r"^[^A-Za-zÁÉÍÓÚÑáéíóú0-9¿¡(]+", "", ln)

        # Asegura que haya texto legible en la línea
        if not re.search(r"[A-Za-zÁÉÍÓÚÑáéíóú]", ln):
            continue

        clean_lines.append(ln)

    # Une las líneas limpias en un solo texto
    return "\n".join(clean_lines).strip()


# ============================================================
# Función: collapse_spaces()
# ------------------------------------------------------------
# Reduce múltiples espacios o tabulaciones consecutivos a uno solo,
# y limpia saltos de línea innecesarios.
#
# Parámetros:
#   - text (str): texto posiblemente con espacios o saltos repetidos.
#
# Retorna:
#   - Texto compacto y sin espacios redundantes.
# ============================================================
def collapse_spaces(text: str) -> str:
    """Reduce espacios y saltos de línea innecesarios."""
    # Sustituye espacios o tabulaciones múltiples por un solo espacio
    text = re.sub(r"[ \t]+", " ", text)

    # Limpia saltos de línea consecutivos
    text = re.sub(r"\s*\n\s*", "\n", text)

    # Elimina espacios sobrantes al inicio y final
    return text.strip()


# ============================================================
# Función: clean_ocr_text()
# ------------------------------------------------------------
# Combina todas las funciones anteriores para aplicar una limpieza completa
# del texto OCR: normalización, filtrado de ruido y reducción de espacios.
#
# Parámetros:
#   - text (str): texto crudo generado por el OCR.
#
# Retorna:
#   - Texto limpio, legible y listo para mostrarse o almacenarse.
# ============================================================
def clean_ocr_text(text: str) -> str:
    """Limpieza completa de texto OCR."""
    # Normaliza caracteres y símbolos especiales
    text = normalize_text(text)

    # Elimina caracteres no deseados (excepto signos útiles y letras acentuadas)
    text = re.sub(r"[^\w\s.,;:!?¡¿'\"()/%ÁÉÍÓÚÑáéíóú-]", " ", text)

    # Quita líneas con ruido o símbolos erróneos
    text = strip_garbage_prefix(text)

    # Reduce espacios redundantes y saltos de línea
    return collapse_spaces(text)