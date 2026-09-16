import json
import unicodedata
import re
from pathlib import Path
from rapidfuzz import process, fuzz

DATA_PATH = Path(__file__).parent.parent.parent.parent / "data"

def _normalize_text(text: str) -> str:
    """
    Normalize text for better matching:
    - Convert to lowercase
    - Remove accents/diacritics
    - Remove extra punctuation and special characters
    - Normalize whitespace
    """
    if not text:
        return ""

    # Convert to lowercase
    text = text.lower()

    # Normalize unicode characters (decompose accented characters)
    text = unicodedata.normalize('NFD', text)
    # Remove combining characters (accents)
    text = ''.join(c for c in text if not unicodedata.combining(c))

    # Remove punctuation and special characters, keep only letters, numbers, and spaces
    text = re.sub(r'[^a-z0-9\s]', ' ', text)

    # Normalize whitespace (multiple spaces to single space)
    text = re.sub(r'\s+', ' ', text).strip()

    return text

# Load DANE municipalities data — falla explícito si falta, sin placeholders silenciosos
try:
    with open(DATA_PATH / "municipios_dane.json", encoding="utf-8") as f:
        MUNICIPIOS_DANE = json.load(f)
except FileNotFoundError as exc:
    raise RuntimeError(
        f"No se encontró {DATA_PATH / 'municipios_dane.json'}: "
        "restaura el dataset DANE oficial, no se usa fallback."
    ) from exc
if not MUNICIPIOS_DANE:
    raise RuntimeError("municipios_dane.json está vacío: restaura el dataset DANE oficial.")

# Create normalized versions for matching
NOMBRES_NORMALIZADOS = [_normalize_text(m["nombre"]) for m in MUNICIPIOS_DANE]
MUNI_MAP = {m["nombre"]: m for m in MUNICIPIOS_DANE}
UMBRAL = 85

def normalizar_municipio(entrada: str) -> dict:
    if not entrada or not entrada.strip():
        return {
            "nombre_oficial": None,
            "codigo_dane": "",
            "departamento": None,
            "confianza": 0.0,
            "requiere_confirmacion": True,
            "entrada_original": entrada or "",
            "error": "Municipio vacío.",
        }
    entrada_limpia = entrada.strip()
    entrada_normalizada = _normalize_text(entrada_limpia)

    match = process.extractOne(
        entrada_normalizada,
        NOMBRES_NORMALIZADOS,
        scorer=fuzz.WRatio
    )
    if match is None:
        return {
            "nombre_oficial": None,
            "codigo_dane": "",
            "departamento": None,
            "confianza": 0.0,
            "requiere_confirmacion": True,
            "entrada_original": entrada_limpia,
            "error": "Sin coincidencias en dataset DANE.",
        }
    _, score, indice = match

    muni = MUNICIPIOS_DANE[indice]
    nombre_original_entrada = entrada_limpia

    return {
        "nombre_oficial":        muni["nombre"],
        "codigo_dane":           muni["codigo"],
        "departamento":          muni["departamento"],
        "confianza":             round(score, 2),
        "requiere_confirmacion": score < UMBRAL,
        "entrada_original":      nombre_original_entrada,
    }