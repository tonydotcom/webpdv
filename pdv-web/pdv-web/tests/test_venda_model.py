"""Testes do Model Venda (regras RN05 a RN09)."""
from datetime import date, timedelta

import pytest

from app.models import ErroValidacao, EstoqueInsuficiente, NaoEncontrado, Produto, Venda


@pytest.fixture
def leite(novo_produto):
    return novo_produto(preco="5,49", estoque="10")


@pytest.fixture
def arroz(novo_produto):
    return novo_produto(codigo="7896004000015", nome="Arroz 5kg", preco="28,99", estoque="3")


def test_registra_venda_e_calcula_total(contexto, leite, arroz):
    venda = Venda.registrar(
        [{"produto_id": leite.id, "quantidade": 2}, {"produto_id": arroz.id, "quantidade": 1}], "PIX"
    )
    assert venda.id is not None
    assert venda.total_centavos == 2 * 549 + 2899
    salva = Venda.buscar_por_id(venda.id)
    assert salva.total_centavos == venda.total_centavos
    assert [(i.nome, i.quantidade) for i in salva.itens] == [("Leite Integral 1L", 2), ("Arroz 5kg", 1)]


def test_rn09_baixa_o_estoque(contexto, leite, arroz):
    Venda.registrar([{"produto_id": leite.id, "quantidade": 4}, {"produto_id": arroz.id, "quantidade": 3}], "DEBITO")
    assert Produto.buscar_por_id(leite.id).estoque == 6
    assert Produto.buscar_por_id(arroz.id).estoque == 0


def test_usa_o_preco_do_banco_e_nao_o_enviado(contexto, leite):
    venda = Venda.registrar([{"produto_id": leite.id, "quantidade": 1, "preco_centavos": 1}], "PIX")
    assert venda.total_centavos == 549


def test_junta_itens_repetidos(contexto, leite):
    venda = Venda.registrar(
        [{"produto_id": leite.id, "quantidade": 1}, {"produto_id": leite.id, "quantidade": 2}], "PIX"
    )
    assert len(venda.itens) == 1
    assert venda.itens[0].quantidade == 3


def test_rn05_venda_sem_itens(contexto):
    with pytest.raises(ErroValidacao, match="pelo menos um produto"):
        Venda.registrar([], "PIX")


@pytest.mark.parametrize("quantidade", [0, -1, "abc"])
def test_rn06_quantidade_invalida(contexto, leite, quantidade):
    with pytest.raises(ErroValidacao):
        Venda.registrar([{"produto_id": leite.id, "quantidade": quantidade}], "PIX")


def test_rn06_estoque_insuficiente_nao_grava_nada(contexto, leite, arroz):
    with pytest.raises(EstoqueInsuficiente, match="Arroz 5kg"):
        Venda.registrar([{"produto_id": leite.id, "quantidade": 1}, {"produto_id": arroz.id, "quantidade": 4}], "PIX")
    # Nada pode ter mudado: nem venda gravada, nem estoque do leite baixado.
    assert Venda.listar() == []
    assert Produto.buscar_por_id(leite.id).estoque == 10


def test_produto_inexistente(contexto):
    with pytest.raises(ErroValidacao, match="não encontrado"):
        Venda.registrar([{"produto_id": 999, "quantidade": 1}], "PIX")


def test_rn07_forma_de_pagamento_invalida(contexto, leite):
    with pytest.raises(ErroValidacao) as erro:
        Venda.registrar([{"produto_id": leite.id, "quantidade": 1}], "CHEQUE")
    assert "forma_pagamento" in erro.value.erros


def test_rn08_dinheiro_calcula_troco(contexto, leite):
    venda = Venda.registrar([{"produto_id": leite.id, "quantidade": 2}], "DINHEIRO", valor_recebido_centavos=2000)
    assert venda.total_centavos == 1098
    assert venda.troco_centavos == 902


def test_rn08_dinheiro_valor_exato_troco_zero(contexto, leite):
    venda = Venda.registrar([{"produto_id": leite.id, "quantidade": 1}], "DINHEIRO", valor_recebido_centavos=549)
    assert venda.troco_centavos == 0


def test_rn08_dinheiro_valor_menor_que_total(contexto, leite):
    with pytest.raises(ErroValidacao) as erro:
        Venda.registrar([{"produto_id": leite.id, "quantidade": 1}], "DINHEIRO", valor_recebido_centavos=500)
    assert "menor que o total" in erro.value.erros["valor_recebido"]
    assert Produto.buscar_por_id(leite.id).estoque == 10


def test_rn08_dinheiro_sem_valor_recebido(contexto, leite):
    with pytest.raises(ErroValidacao):
        Venda.registrar([{"produto_id": leite.id, "quantidade": 1}], "DINHEIRO")


def test_cartao_nao_guarda_valor_recebido(contexto, leite):
    venda = Venda.registrar([{"produto_id": leite.id, "quantidade": 1}], "CREDITO", valor_recebido_centavos=10000)
    assert venda.valor_recebido_centavos is None
    assert venda.troco_centavos == 0


def test_lista_vendas_e_resumo_do_dia(contexto, leite):
    Venda.registrar([{"produto_id": leite.id, "quantidade": 1}], "PIX")
    Venda.registrar([{"produto_id": leite.id, "quantidade": 2}], "PIX")
    hoje = date.today()
    assert len(Venda.listar(hoje)) == 2
    assert Venda.listar(hoje - timedelta(days=1)) == []
    assert Venda.resumo_do_dia(hoje) == {"quantidade": 2, "total_centavos": 3 * 549}
    assert Venda.resumo_do_dia(hoje - timedelta(days=1)) == {"quantidade": 0, "total_centavos": 0}


def test_buscar_venda_inexistente(contexto):
    with pytest.raises(NaoEncontrado):
        Venda.buscar_por_id(999)
