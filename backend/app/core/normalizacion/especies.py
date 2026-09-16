import json
from pathlib import Path
from rapidfuzz import process, fuzz
import re

DATA_PATH = Path(__file__).parent.parent.parent.parent / "data"
UMBRAL_FUZZY = 80

# Load IDEAM species data
try:
    with open(DATA_PATH / "especies_ideam.json", encoding="utf-8") as f:
        ESPECIES = json.load(f)
except FileNotFoundError:
    # Create placeholder data if file doesn't exist
    ESPECIES = [
        {"nombre_comun": "eucalipto", "nombre_cientifico": "Eucalyptus globulus", "familia": "Myrtaceae"},
        {"nombre_comun": "pino", "nombre_cientifico": "Pinus patula", "familia": "Pinaceae"},
        {"nombre_comun": "roble", "nombre_cientifico": "Quercus humboldtii", "familia": "Fagaceae"},
        {"nombre_comun": "cedro", "nombre_cientifico": "Cedrela odorata", "familia": "Meliaceae"},
        {"nombre_comun": "caoba", "nombre_cientifico": "Swietenia macrophylla", "familia": "Meliaceae"},
        {"nombre_comun": "guayacán", "nombre_cientifico": "Guaiacum officinale", "familia": "Zygophyllaceae"},
        {"nombre_comun": "morado", "nombre_cientifico": "Machorium luzonium", "familia": "Fabaceae"},
        {"nombre_comun": "saman", "nombre_cientifico": "Samanea saman", "familia": "Fabaceae"},
        {"nombre_comun": "ceiba", "nombre_cientifico": "Ceiba pentandra", "familia": "Malvaceae"},
        {"nombre_comun": "arrayán", "nombre_cientifico": "Luma apiculata", "familia": "Myrtaceae"},
        {"nombre_comun": "yarumo", "nombre_cientifico": "Cecropia peltata", "familia": "Urticaceae"},
        {"nombre_comun": "guadua", "nombre_cientifico": "Guadua angustifolia", "familia": "Poaceae"},
        {"nombre_comun": "palma de cera", "nombre_cientifico": "Ceroxylon quindiuense", "familia": "Arecaceae"},
        {"nombre_comun": "nogal", "nombre_cientifico": "Juglans neotropica", "familia": "Juglandaceae"},
        {"nombre_comun": "aliso", "nombre_cientifico": "Alnus acuminata", "familia": "Betulaceae"},
        {"nombre_comun": "arrayán blanco", "nombre_cientifico": "Myrcianthes rhopaloides", "familia": "Myrtaceae"},
        {"nombre_comun": "bolina blanca", "nombre_cientifico": "Tabebuia rosea", "familia": "Bignoniaceae"},
        {"nombre_comun": "mangle", "nombre_cientifico": "Rhizophora mangle", "familia": "Rhizophoraceae"},
        {"nombre_comun": "helecho", "nombre_cientifico": "Pteridium aquilinum", "familia": "Dennstaedtiaceae"},
        {"nombre_comun": "orquídea", "nombre_cientifico": "Cattleya trianae", "familia": "Orchidaceae"}
    ]
    # Save placeholder data
    DATA_PATH.mkdir(exist_ok=True)
    with open(DATA_PATH / "especies_ideam.json", "w", encoding="utf-8") as f:
        json.dump(ESPECIES, f, indent=2, ensure_ascii=False)

NOMBRES_COMUNES = [e["nombre_comun"] for e in ESPECIES]
ESP_MAP = {e["nombre_comun"]: e for e in ESPECIES}

# Common synonyms and variations for species names to improve matching
ESPECIE_SINONIMOS = {
    "eucalipto": ["eucalipto", "eucaliptus", "eucalyptus"],
    "pino": ["pino", "pinos", "pinus"],
    "roble": ["roble", "robles", "quercus"],
    "cedro": ["cedro", "cedros", "cedrela"],
    "caoba": ["caoba", "caobas", "swietenia", "mahogany"],
    "guayacán": ["guayacán", "guayacan", "guaiacum", "lignum vitae"],
    "morado": ["morado", "tabebuia", "pau d'arco", "ipe"],
    "saman": ["saman", "algarrobo", "samanea", "rain tree"],
    "ceiba": ["ceiba", "ceibas", "kapok", "silk cotton"],
    "arrayán": ["arrayán", "arrayan", "myrtus", "myrtle"],
    "yarumo": ["yarumo", "cecropia", "utz", "cecropia"],
    "guadua": ["guadua", "guaduas", "bamboo", "bambú"],
    "palma de cera": ["palma de cera", "wax palm", "ceroxylon"],
    "nogal": ["nogal", "nogales", "walnut", "juglans"],
    "aliso": ["aliso", "alisos", "alder", "alnus"],
    "arrayán blanco": ["arrayán blanco", "arrayan blanco", "myrcianthes"],
    "bolina blanca": ["bolina blanca", "bolina", "tabebuia rosea", "pink tabebuia"],
    "mangle": ["mangle", "mangles", "mangrove", "rhizophora"],
    "helecho": ["helecho", "helechos", "fern", "wholecho", "pteridium"],
    "orquídea": ["orquídea", "orquideas", "orchid", "cattleya", "orquídeas"]
}

def normalizar_especie(entrada: str, municipio: str = None) -> dict:
    """
    Normaliza el nombre de una especie forestal usando fuzzy matching contra el IDEAM.
    No requiere llamadas a API externas.
    """
    nombre = entrada.strip().lower()

    # First, try direct fuzzy match against common names
    mejor, score, _ = process.extractOne(nombre, NOMBRES_COMUNES, scorer=fuzz.WRatio)

    if score >= UMBRAL_FUZZY:
        esp = ESP_MAP[mejor]
        return {
            "nombre_comun": esp["nombre_comun"],
            "nombre_cientifico": esp["nombre_cientifico"],
            "familia": esp.get("familia", ""),
            "metodo": "fuzzy_match",
            "confianza": round(score, 2)
        }

    # If fuzzy match fails, try checking against known synonyms
    for nombre_estandar, sinonimos in ESPECIE_SINONIMOS.items():
        for sinonimo in sinonimos:
            # Check for exact match in synonyms
            if nombre == sinonimo:
                esp = ESP_MAP[nombre_estandar]
                return {
                    "nombre_comun": esp["nombre_comun"],
                    "nombre_cientifico": esp["nombre_cientifico"],
                    "familia": esp.get("familia", ""),
                    "metodo": "sinonimo_exacto",
                    "confianza": 95.0
                }
            # Check for fuzzy match against synonyms
            mejor_sinonimo, score_sinonimo, _ = process.extractOne(nombre, sinonimos, scorer=fuzz.WRatio)
            if score_sinonimo >= UMBRAL_FUZZY:
                esp = ESP_MAP[nombre_estandar]
                return {
                    "nombre_comun": esp["nombre_comun"],
                    "nombre_cientifico": esp["nombre_cientifico"],
                    "familia": esp.get("familia", ""),
                    "metodo": "sinonimo_fuzzy",
                    "confianza": round(score_sinonimo, 2)
                }

    # If still no match, try to extract potential scientific name patterns
    # Look for patterns like "Genus species" or "Genus sp."
    scientific_pattern = r'\b([A-Z][a-z]+)\s+([a-z]+)\b'
    match = re.search(scientific_pattern, entrada)
    if match:
        genus, species = match.groups()
        potential_name = f"{genus} {species}".lower()
        # Try fuzzy matching against scientific names
        nombres_cientificos = [e["nombre_cientifico"].lower() for e in ESPECIES]
        mejor_cientifico, score_cientifico, _ = process.extractOne(potential_name, nombres_cientificos, scorer=fuzz.WRatio)
        if score_cientifico >= UMBRAL_FUZZY:
            # Find the matching species
            for esp in ESPECIES:
                if esp["nombre_cientifico"].lower() == mejor_cientifico:
                    return {
                        "nombre_comun": esp["nombre_comun"],
                        "nombre_cientifico": esp["nombre_cientifico"],
                        "familia": esp.get("familia", ""),
                        "metodo": "nombre_cientifico",
                        "confianza": round(score_cientifico, 2)
                    }

    # Final fallback: return the best fuzzy match even if below threshold, but flag for review
    mejor, score, _ = process.extractOne(nombre, NOMBRES_COMUNES, scorer=fuzz.WRatio)
    esp = ESP_MAP[mejor]
    return {
        "nombre_comun": esp["nombre_comun"],
        "nombre_cientifico": esp["nombre_cientifico"],
        "familia": esp.get("familia", ""),
        "metodo": "fuzzy_match_bajo_umbral",
        "confianza": round(score, 2),
        "requiere_revision": score < UMBRAL_FUZZY,
        "advertencia": f"Coincidencia por debajo del umbral ({score}%). Verificar manualmente."
    }