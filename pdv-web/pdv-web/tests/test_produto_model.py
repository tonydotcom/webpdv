"""Testes do Model Produto (regras RN01 a RN04 e RN10)."""
import pytest

from app.models import ErroValidacao, NaoEncontrado, Produto, Venda

DADOS_VALIDOS = {"codigo_barras": "7891000100103", "nome": "Leite Integral 1L", "preco": "5,49", "estoque": "10"}


def dados(**alteracoes):
    return {**DADOS_VALIDOS, **alteracoes}


def test_cadastra_produto_valido(contexto):
    produto = Produto.a_partir_do_formulario(DADOS_VALIDOS).salvar()
    assert produto.id is not None
    salvo = Produto.buscar_por_id(produto.id)
    assert salvo.nome == "Leite Integral 1L"
    assert salvo.preco_centavos == 549
    assert salvo.estoque == 10


def test_remove_espacos_extras_do_nome(contexto):
    produto = Produto.a_partir_do_formulario(dados(nome="  Leite    Integral  "))
    assert produto.nome == "Leite Integral"


@pytest.mark.parametrize("codigo", ["", "123", "123456789012345", "78910001001AB"])
def test_rn01_codigo_de_barras_invalido(contexto, codigo):
    with pytest.raises(ErroValidacao) as erro:
        Produto.a_partir_do_formulario(dados(codigo_barras=codigo))
    assert "codigo_barras" in erro.value.erros


def test_rn01_codigo_de_barras_duplicado(contexto, novo_produto):
    novo_produto()
    with pytest.raises(ErroValidacao) as erro:
        Produto.a_partir_do_formulario(dados(nome="Outro produto"))
    assert "Já existe" in erro.value.erros["codigo_barras"]


def test_rn01_editar_mantendo_o_mesmo_codigo_e_permitido(contexto, novo_produto):
    produto = novo_produto()
    editado = Produto.a_partir_do_formulario(dados(nome="Leite Desnatado 1L"), produto_id=produto.id).salvar()
    assert Produto.buscar_por_id(produto.id).nome == "Leite Desnatado 1L"
    assert editado.id == produto.id


@pytest.mark.parametrize("nome", ["", "ab", "x" * 101])
def test_rn02_nome_invalido(contexto, nome):
    with pytest.raises(ErroValidacao) as erro:
        Produto.a_partir_do_formulario(dados(nome=nome))
    assert "nome" in erro.value.erros


@pytest.mark.parametrize("preco", ["0", "0,00", "abc", "", "-3"])
def test_rn03_preco_invalido(contexto, preco):
    with pytest.raises(ErroValidacao) as erro:
        Produto.a_partir_do_formulario(dados(preco=preco))
    assert "preco" in erro.value.erros


@pytest.mark.parametrize("estoque", ["-1", "2.5", "abc", ""])
def test_rn04_estoque_invalido(contexto, estoque):
    with pytest.raises(ErroValidacao) as erro:
        Produto.a_partir_do_formulario(dados(estoque=estoque))
    assert "estoque" in erro.value.erros


def test_mostra_todos_os_erros_de_uma_vez(contexto):
    with pytest.raises(ErroValidacao) as erro:
        Produto.a_partir_do_formulario({"codigo_barras": "", "nome": "", "preco": "", "estoque": ""})
    assert set(erro.value.erros) == {"codigo_barras", "nome", "preco", "estoque"}


def test_lista_e_busca_por_nome_ou_codigo(contexto, novo_produto):
    novo_produto()
    novo_produto(codigo="7891910000197", nome="Açúcar Refinado 1kg")
    assert [p.nome for p in Produto.listar()] == ["Açúcar Refinado 1kg", "Leite Integral 1L"]
    assert [p.nome for p in Produto.listar("leite")] == ["Leite Integral 1L"]
    assert [p.nome for p in Produto.listar("7891910000197")] == ["Açúcar Refinado 1kg"]
    assert Produto.listar("inexistente") == []


def test_lista_estoque_baixo(contexto, novo_produto):
    novo_produto(estoque="50")
    novo_produto(codigo="7891910000197", nome="Açúcar", estoque="5")
    novo_produto(codigo="7896004000015", nome="Arroz", estoque="0")
    assert [p.nome for p in Produto.listar_estoque_baixo()] == ["Arroz", "Açúcar"]


def test_buscar_inexistente_lanca_erro(contexto):
    with pytest.raises(NaoEncontrado):
        Produto.buscar_por_id(999)


def test_exclui_produto_sem_vendas(contexto, novo_produto):
    produto = novo_produto()
    Produto.excluir(produto.id)
    assert Produto.buscar_por_codigo(produto.codigo_barras) is None


def test_rn10_nao_exclui_produto_ja_vendido(contexto, novo_produto):
    produto = novo_produto()
    Venda.registrar([{"produto_id": produto.id, "quantidade": 1}], "PIX")
    with pytest.raises(ErroValidacao, match="não pode ser excluído"):
        Produto.excluir(produto.id)
    assert Produto.buscar_por_id(produto.id) is not None
