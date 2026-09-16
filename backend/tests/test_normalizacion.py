import pytest
from app.core.normalizacion import municipios, especies, coordenadas, tipo_aprovechamiento
from app.core.reglas import requisitos

def test_normalizar_municipio_exacto():
    """Test exact match for municipality"""
    result = municipios.normalizar_municipio("Bogotá D.C.")
    assert result["nombre_oficial"] == "Bogotá D.C."
    assert result["codigo_dane"] == "11001"
    assert result["confianza"] == 100.0
    assert result["requiere_confirmacion"] == False

def test_normalizar_municipio_fuzzy():
    """Test fuzzy match for municipality"""
    result = municipios.normalizar_municipio("bogota dc")
    assert result["nombre_oficial"] == "Bogotá D.C."
    assert result["codigo_dane"] == "11001"
    assert result["confianza"] >= 85.0
    assert result["requiere_confirmacion"] == False

def test_normalizar_coordenada_gms():
    """Test GMS to decimal conversion"""
    result = coordenadas.normalizar_coordenada("4°39'50\"N")
    assert result["eje"] == "latitud"
    assert abs(result["valor_decimal"] - 4.6639) < 0.001
    assert result["en_colombia"] == True

def test_normalizar_coordenada_decimal():
    """Test decimal coordinate validation"""
    result = coordenadas.normalizar_coordenada("-74.0721")
    assert result["eje"] == "longitud"
    assert result["valor_decimal"] == -74.0721
    assert result["en_colombia"] == True

def test_clasificar_tipo_keywords():
    """Test classification by keywords"""
    result = tipo_aprovechamiento.clasificar_tipo("leña para consumo propio")
    assert result["categoria"] == "Aprovechamiento Doméstico"
    assert result["metodo"] == "keywords_expanded"
    assert result["confianza"] == 0.92

def test_normalizar_especie_fuzzy():
    """Test fuzzy match for species"""
    result = especies.normalizar_especie("pino")
    assert result["nombre_comun"] == "pino"
    assert result["nombre_cientifico"] == "Pinus patula"
    assert result["metodo"] == "fuzzy_match"
    assert result["confianza"] >= 80.0


def test_requisitos_por_autoridad():
    result = requisitos.obtener_requisitos("SDA")
    assert result["requiere_revision"] is False
    assert "Plano o mapa de localización" in result["anexos"]

if __name__ == "__main__":
    test_normalizar_municipio_exacto()
    test_normalizar_municipio_fuzzy()
    test_normalizar_coordenada_gms()
    test_normalizar_coordenada_decimal()
    test_clasificar_tipo_keywords()
    test_normalizar_especie_fuzzy()
    print("All tests passed!")