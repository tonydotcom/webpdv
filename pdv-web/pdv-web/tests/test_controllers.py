"""Testes dos Controllers: simulam o navegador fazendo requisições HTTP."""
import pytest

from app.models import Produto, Venda


@pytest.fixture
def cliente_com_exemplos(app_com_exemplos):
    return app_com_exemplos.test_client()


def id_do_produto(app, codigo):
    with app.app_context():
        return Produto.buscar_por_codigo(codigo).id


# --------------------------- Páginas ---------------------------------- #
@pytest.mark.parametrize("url", ["/", "/produtos/", "/produtos/novo", "/vendas/", "/vendas/nova"])
def test_paginas_abrem(cliente, url):
    resposta = cliente.get(url)
    assert resposta.status_code == 200
    assert "PDV" in resposta.get_data(as_text=True)


def test_painel_mostra_estoque_baixo(cliente_com_exemplos):
    html = cliente_com_exemplos.get("/").get_data(as_text=True)
    assert "Achocolatado em Pó 400g" in html  # estoque 3
    assert "Leite Integral 1L" not in html     # estoque 40


def test_pagina_inexistente_mostra_erro_404(cliente):
    resposta = cliente.get("/nao-existe")
    assert resposta.status_code == 404
    assert "não existe" in resposta.get_data(as_text=True)


def test_erro_inesperado_mostra_pagina_500(app, cliente, monkeypatch):
    def quebrar(*_args, **_kwargs):
        raise RuntimeError("banco fora do ar")
    monkeypatch.setattr(Produto, "listar", quebrar)
    resposta = cliente.get("/produtos/")
    assert resposta.status_code == 500
    assert "erro inesperado" in resposta.get_data(as_text=True)


# --------------------------- Produtos --------------------------------- #
def test_cadastrar_produto(app, cliente):
    resposta = cliente.post("/produtos/novo", data={
        "codigo_barras": "7891000100103", "nome": "Leite", "preco": "5,49", "estoque": "10",
    }, follow_redirects=True)
    assert resposta.status_code == 200
    assert "cadastrado com sucesso" in resposta.get_data(as_text=True)
    with app.app_context():
        assert Produto.buscar_por_codigo("7891000100103").preco_centavos == 549


def test_cadastrar_produto_invalido_mostra_erros(cliente):
    resposta = cliente.post("/produtos/novo", data={"codigo_barras": "12", "nome": "", "preco": "x", "estoque": "-1"})
    html = resposta.get_data(as_text=True)
    assert resposta.status_code == 400
    assert "de 8 a 14 números" in html
    assert "pelo menos 3 letras" in html
    assert "Preço inválido" in html
    assert 'value="12"' in html  # mantém o que o usuário digitou


def test_editar_produto(app, cliente_com_exemplos):
    produto_id = id_do_produto(app, "7891000100103")
    assert "5,49" in cliente_com_exemplos.get(f"/produtos/{produto_id}/editar").get_data(as_text=True)
    cliente_com_exemplos.post(f"/produtos/{produto_id}/editar", data={
        "codigo_barras": "7891000100103", "nome": "Leite Integral 1L", "preco": "5,99", "estoque": "40",
    })
    with app.app_context():
        assert Produto.buscar_por_id(produto_id).preco_centavos == 599


def test_editar_produto_inexistente(cliente):
    assert cliente.get("/produtos/999/editar").status_code == 404


def test_excluir_produto(app, cliente_com_exemplos):
    produto_id = id_do_produto(app, "78912939")
    resposta = cliente_com_exemplos.post(f"/produtos/{produto_id}/excluir", follow_redirects=True)
    assert "excluído" in resposta.get_data(as_text=True)


def test_excluir_produto_vendido_mostra_aviso(app, cliente_com_exemplos):
    produto_id = id_do_produto(app, "78912939")
    with app.app_context():
        Venda.registrar([{"produto_id": produto_id, "quantidade": 1}], "PIX")
    resposta = cliente_com_exemplos.post(f"/produtos/{produto_id}/excluir", follow_redirects=True)
    assert "não pode ser excluído" in resposta.get_data(as_text=True)


def test_excluir_exige_post(cliente_com_exemplos):
    assert cliente_com_exemplos.get("/produtos/1/excluir").status_code == 405


def test_api_busca_por_codigo(cliente_com_exemplos):
    resposta = cliente_com_exemplos.get("/produtos/api/codigo/7891000100103")
    assert resposta.status_code == 200
    assert resposta.get_json()["nome"] == "Leite Integral 1L"


def test_api_codigo_inexistente_responde_json(cliente):
    resposta = cliente.get("/produtos/api/codigo/0000000000000")
    assert resposta.status_code == 404
    assert "Nenhum produto" in resposta.get_json()["erro"]


def test_api_busca_por_nome(cliente_com_exemplos):
    nomes = [p["nome"] for p in cliente_com_exemplos.get("/produtos/api/busca?q=caf").get_json()]
    assert nomes == ["Café Torrado e Moído 500g"]
    assert cliente_com_exemplos.get("/produtos/api/busca?q=c").get_json() == []


# ---------------------------- Vendas ---------------------------------- #
def test_finalizar_venda_em_dinheiro(app, cliente_com_exemplos):
    leite = id_do_produto(app, "7891000100103")
    resposta = cliente_com_exemplos.post("/vendas/", json={
        "itens": [{"produto_id": leite, "quantidade": 2}],
        "forma_pagamento": "DINHEIRO",
        "valor_recebido": "20,00",
    })
    assert resposta.status_code == 201
    dados = resposta.get_json()
    assert dados["total_centavos"] == 1098
    assert dados["troco_centavos"] == 902

    detalhe = cliente_com_exemplos.get(dados["url"]).get_data(as_text=True)
    assert "Leite Integral 1L" in detalhe
    assert "R$ 9,02" in detalhe


def test_finalizar_venda_estoque_insuficiente(app, cliente_com_exemplos):
    achocolatado = id_do_produto(app, "7891000053508")  # estoque 3
    resposta = cliente_com_exemplos.post("/vendas/", json={
        "itens": [{"produto_id": achocolatado, "quantidade": 5}], "forma_pagamento": "PIX",
    })
    assert resposta.status_code == 400
    assert "Estoque insuficiente" in resposta.get_json()["erro"]


@pytest.mark.parametrize("corpo, mensagem", [
    ({"itens": [], "forma_pagamento": "PIX"}, "pelo menos um produto"),
    ({"itens": [{"produto_id": 1, "quantidade": 1}], "forma_pagamento": "DINHEIRO", "valor_recebido": "abc"},
     "Valor recebido inválido"),
    ({"itens": [{"produto_id": 1, "quantidade": 1}], "forma_pagamento": "BOLETO"}, "forma de pagamento"),
])
def test_finalizar_venda_invalida(cliente_com_exemplos, corpo, mensagem):
    resposta = cliente_com_exemplos.post("/vendas/", json=corpo)
    assert resposta.status_code == 400
    assert mensagem in resposta.get_json()["erro"]


def test_finalizar_venda_sem_json(cliente):
    resposta = cliente.post("/vendas/", data="isto não é json", content_type="text/plain")
    assert resposta.status_code == 400
    assert resposta.get_json()["erro"] == "Requisição inválida."


def test_lista_vendas_com_filtro_de_data(app, cliente_com_exemplos):
    leite = id_do_produto(app, "7891000100103")
    cliente_com_exemplos.post("/vendas/", json={"itens": [{"produto_id": leite, "quantidade": 1}], "forma_pagamento": "PIX"})
    assert "#1" in cliente_com_exemplos.get("/vendas/").get_data(as_text=True)
    assert "Nenhuma venda" in cliente_com_exemplos.get("/vendas/?data=2000-01-01").get_data(as_text=True)
    assert "Data inválida" in cliente_com_exemplos.get("/vendas/?data=ontem").get_data(as_text=True)


def test_detalhe_venda_inexistente(cliente):
    assert cliente.get("/vendas/999").status_code == 404
