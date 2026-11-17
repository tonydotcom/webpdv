"""Conversão de valores em dinheiro.

Todo valor monetário é guardado em centavos (inteiro) para evitar erros de
arredondamento de números de ponto flutuante (ex.: 0.1 + 0.2 != 0.3).
"""
import re

_FORMATO_VALIDO = re.compile(r"^\d+([.,]\d{1,2})?$")


def reais_para_centavos(texto):
    """Converte '12,50', '12.5' ou '1.234,56' em centavos (1250, 1250, 123456).

    Lança ValueError se o texto não for um valor válido.
    """
    if texto is None:
        raise ValueError("Valor não informado.")
    texto = str(texto).strip().replace("R$", "").replace(" ", "")
    if "," in texto:
        texto = texto.replace(".", "")  # "1.234,56" -> "1234,56"
    if not _FORMATO_VALIDO.match(texto):
        raise ValueError(f"Valor inválido: {texto!r}")
    inteiro, _, decimais = texto.replace(",", ".").partition(".")
    return int(inteiro) * 100 + int(decimais.ljust(2, "0") or 0)


def formatar_reais(centavos):
    """Converte 123456 em 'R$ 1.234,56'."""
    if centavos is None:
        return "-"
    sinal = "-" if centavos < 0 else ""
    reais, cents = divmod(abs(int(centavos)), 100)
    reais_formatado = f"{reais:,}".replace(",", ".")
    return f"{sinal}R$ {reais_formatado},{cents:02d}"


def centavos_para_campo(centavos):
    """Converte 1250 em '12,50' (para preencher campos de formulário)."""
    if centavos is None:
        return ""
    reais, cents = divmod(int(centavos), 100)
    return f"{reais},{cents:02d}"
