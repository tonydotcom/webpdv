import pytest

from app.utils.dinheiro import centavos_para_campo, formatar_reais, reais_para_centavos


@pytest.mark.parametrize("texto, esperado", [
    ("12,50", 1250),
    ("12.5", 1250),
    ("12", 1200),
    ("0,05", 5),
    ("1.234,56", 123456),
    ("R$ 9,99", 999),
    (" 3,1 ", 310),
])
def test_converte_reais_para_centavos(texto, esperado):
    assert reais_para_centavos(texto) == esperado


@pytest.mark.parametrize("texto", ["", "abc", "12,345", "-5", "1,2,3", None])
def test_rejeita_valores_invalidos(texto):
    with pytest.raises(ValueError):
        reais_para_centavos(texto)


@pytest.mark.parametrize("centavos, esperado", [
    (0, "R$ 0,00"),
    (5, "R$ 0,05"),
    (1250, "R$ 12,50"),
    (123456, "R$ 1.234,56"),
    (100000000, "R$ 1.000.000,00"),
    (-150, "-R$ 1,50"),
])
def test_formata_reais(centavos, esperado):
    assert formatar_reais(centavos) == esperado


def test_centavos_para_campo():
    assert centavos_para_campo(1250) == "12,50"
    assert centavos_para_campo(5) == "0,05"
    assert centavos_para_campo(None) == ""
