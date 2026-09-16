"""
Basic test to verify that the modules can be imported and instantiated correctly.
"""
def test_imports():
    """Test that all modules can be imported without errors."""
    from app.core.normalizacion import municipios, especies, coordenadas, tipo_aprovechamiento
    from app.core.reglas import car_selector
    from app.core.reglas import requisitos
    from app.core.generacion import documento_word
    from app.api.routes import formulario
    from app.models import tramite
    from app.schemas import formulario as formulario_schema
    from app.config import settings
    from app.database import Base, engine

    assert all((municipios, especies, coordenadas, tipo_aprovechamiento,
                car_selector, requisitos, documento_word, formulario, tramite,
                formulario_schema, settings, Base, engine))

def test_municipio_normalizacion():
    """Test municipio normalization function."""
    from app.core.normalizacion import municipios

    result = municipios.normalizar_municipio("bogota")
    assert result["nombre_oficial"] == "Bogotá D.C."
    assert result["codigo_dane"] == "11001"
    assert result["confianza"] >= 85.0

def test_coordenadas_normalizacion():
    """Test coordenadas normalization function."""
    from app.core.normalizacion import coordenadas

    result = coordenadas.normalizar_coordenada("4°39'50\"N")
    assert result["eje"] == "latitud"
    assert abs(result["valor_decimal"] - 4.6639) < 0.001

def test_car_selector():
    """Test CAR selector function."""
    from app.core.reglas import car_selector

    result = car_selector.seleccionar_autoridad("11001")  # Bogotá D.C.
    assert result["sigla"] == "SDA"
    assert result["nombre"] == "Secretaría Distrital de Ambiente"
