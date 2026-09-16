import json
import re
from typing import Dict, Any

CATEGORIAS = {
    "domestico":   "Aprovechamiento Doméstico",
    "comercial":   "Aprovechamiento Comercial",
    "persistente": "Aprovechamiento Persistente",
    "unico":       "Aprovechamiento Único",
}

# Expanded keyword lists for better coverage without API calls
KEYWORDS = {
    "domestico":   [
        "leña", "lenia", "consumo propio", "uso familiar", "autoconsumo",
        "doméstico", "domestico", "familia", "hogar", "cocina", "calefacción",
        "leños", "lenas", "para cocinar", "para calentar", "uso interno",
        "consumo familiar", "uso domestico", "leña de cocina"
    ],
    "comercial":   [
        "venta", "vender", "comercio", "comercial", "maderable", "industrial",
        "exportación", "exportar", "industrial", "aserradero", "carpintería",
        "muebles", "construcción comercial", "madera aserrada", "tablones",
        "vigones", "postes", "durmientes", "embalaje", "embale", "papel",
        "cartón", "fibras", "tablero", "contraplacado", "madera comercial"
    ],
    "persistente": [
        "manejo", "manojo", "silvicultura", "bosque natural", "sostenible",
        "manejo forestal", "manejo sostenible", "bosque", "natural", "reserva",
        "conservación", "protección", "extracción controlada", "cosecha",
        "rotación", "ciclo corto", "manejo de bosques", "silvicultura",
        "aprovechamiento sostenible", "manejo forestal sostenible"
    ],
    "unico":       [
        "tala", "talas", "única vez", "cambio de uso", "obra", "construcción",
        "tala única", "tala total", "desbosque", "desmonte", "limpieza de terreno",
        "obra civil", "construcción de vías", "minería", "represa", "línea de transmisión",
        "oleoducto", "gasoducto", "proyecto de infraestructura", "desarrollo urbano",
        "expansión agrícola", "ganadería", "cambio de uso de suelo"
    ]
}

# Confidence scores for keyword matches
KEYWORD_CONFIDENCE = {
    "domestico":   0.85,
    "comercial":   0.90,
    "persistente": 0.88,
    "unico":       0.92
}

def clasificar_tipo(texto_libre: str) -> Dict[str, Any]:
    """
    Clasifica el tipo de aprovechamiento usando solo coincidencias de palabras clave.
    No requiere llamadas a API externas.
    """
    texto = texto_libre.lower()

    # Check each category for keyword matches (return on first match)
    for categoria, palabras_clave in KEYWORDS.items():
        for palabra in palabras_clave:
            if palabra in texto:
                return {
                    "categoria": CATEGORIAS[categoria],
                    "codigo": categoria,
                    "metodo": "keywords_expanded",
                    "referencia_legal": "Decreto 1791/1996, Art. 9-13",
                    "confianza": 0.92
                }

    # If no keyword matches, apply some heuristic rules based on common phrases
    texto_lower = texto_libre.lower()

    # Heuristic rules for common cases
    if any(word in texto_lower for word in ["leña", "lenia", "cocina", "calentar", "calentamiento"]):
        return {
            "categoria": CATEGORIAS["domestico"],
            "codigo": "domestico",
            "metodo": "heuristic_domestico",
            "referencia_legal": "Decreto 1791/1996, Art. 9-13",
            "confianza": 0.75
        }

    if any(word in texto_lower for word in ["venta", "vender", "comercio", "exportar", "industrial"]):
        return {
            "categoria": CATEGORIAS["comercial"],
            "codigo": "comercial",
            "metodo": "heuristic_comercial",
            "referencia_legal": "Decreto 1791/1996, Art. 9-13",
            "confianza": 0.75
        }

    if any(word in texto_lower for word in ["manejo", "silvicultura", "sostenible", "conservacion"]):
        return {
            "categoria": CATEGORIAS["persistente"],
            "codigo": "persistente",
            "metodo": "heuristic_persistente",
            "referencia_legal": "Decreto 1791/1996, Art. 9-13",
            "confianza": 0.75
        }

    if any(word in texto_lower for word in ["tala", "obra", "construccion", "cambio de uso", "desbosque"]):
        return {
            "categoria": CATEGORIAS["unico"],
            "codigo": "unico",
            "metodo": "heuristic_unico",
            "referencia_legal": "Decreto 1791/1996, Art. 9-13",
            "confianza": 0.75
        }

    # Default to requer_revision_manual if no matches found
    return {
        "error": "clasificacion_fallida",
        "requiere_revision_manual": True,
        "sugerencia": "Revisar manualmente el tipo de aprovechamiento basado en la descripción proporcionada",
        "metodo": "fallback"
    }