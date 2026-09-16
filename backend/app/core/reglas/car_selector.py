import json
from pathlib import Path

DATA_PATH = Path(__file__).parent.parent.parent.parent / "data"

# Load CAR por municipio mapping
try:
    with open(DATA_PATH / "car_por_municipio.json", encoding="utf-8") as f:
        CAR_POR_MUNICIPIO: dict = json.load(f)
except FileNotFoundError:
    # Create placeholder mapping if file doesn't exist
    CAR_POR_MUNICIPIO = {
        "11001": "SDA",           # Bogotá D.C.
        "05001": "CAR",           # Medellín
        "76001": "CAR",           # Cali
        "08001": "CAR",           # Barranquilla
        "13001": "CAR",           # Cartagena
        "54001": "CAR",           # Cúcuta
        "08074": "CAR",           # Soledad
        "73001": "CAR",           # Ibagué
        "50001": "CAR",           # Villavicencio
        "47001": "CAR",           # Santa Marta
        "20001": "CAR",           # Valledupar
        "23001": "CAR",           # Montería
        "17001": "CAR",           # Manizales
        "66001": "CAR",           # Pereira
        "19001": "CAR",           # Popayán
        "41001": "CAR",           # Neiva
        "15244": "CORPOBOYACA",   # Duitama
        "25001": "CAR",           # Tunja
        "25239": "CAR",           # Girardot
        "25269": "CAR",           # Facatativá
    }
    # Save placeholder mapping
    DATA_PATH.mkdir(exist_ok=True)
    with open(DATA_PATH / "car_por_municipio.json", "w", encoding="utf-8") as f:
        json.dump(CAR_POR_MUNICIPIO, f, indent=2, ensure_ascii=False)

AUTORIDADES = {
    "CAR":        {"nombre": "Corporación Autónoma Regional de Cundinamarca", "sitio_web": "https://www.car.gov.co"},
    "SDA":        {"nombre": "Secretaría Distrital de Ambiente", "sitio_web": "https://www.ambientebogota.gov.co"},
    "CORPOBOYACA":{"nombre": "Corporación Autónoma Regional de Boyacá", "sitio_web": "https://www.corpoboyaca.gov.co"},
}

def seleccionar_autoridad(codigo_dane: str) -> dict:
    sigla = CAR_POR_MUNICIPIO.get(codigo_dane)
    if not sigla:
        return {"error": "municipio_no_mapeado", "codigo_dane": codigo_dane, "requiere_revision": True}
    return {"sigla": sigla, **AUTORIDADES.get(sigla, {}), "encontrado": True}