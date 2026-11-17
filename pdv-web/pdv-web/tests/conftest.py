import pytest

from app import create_app
from app.db import criar_tabelas


@pytest.fixture
def app(tmp_path):
    """Cada teste roda num banco novo e vazio (SQLite temporário)."""
    app = create_app({"TESTING": True, "DATABASE_URL": f"sqlite:///{tmp_path / 'teste.db'}"})
    with app.app_context():
        criar_tabelas()
    return app


@pytest.fixture
def app_com_exemplos(app):
    with app.app_context():
        criar_tabelas(com_exemplos=True)
    return app


@pytest.fixture
def contexto(app):
    """Contexto da aplicação, para testar os models diretamente."""
    with app.app_context():
        yield app


@pytest.fixture
def cliente(app):
    """Navegador simulado, para testar os controllers."""
    return app.test_client()


@pytest.fixture
def novo_produto(contexto):
    from app.models import Produto

    def _criar(codigo="7891000100103", nome="Leite Integral 1L", preco="5,49", estoque="10"):
        return Produto.a_partir_do_formulario(
            {"codigo_barras": codigo, "nome": nome, "preco": preco, "estoque": estoque}
        ).salvar()

    return _criar
