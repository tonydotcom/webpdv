"""Testes do comando `flask init-db` (usado na hospedagem)."""
from app.models import Produto


def test_init_db_com_exemplos(app):
    resultado = app.test_cli_runner().invoke(args=["init-db", "--exemplos"])
    assert "Banco de dados criado" in resultado.output
    with app.app_context():
        assert len(Produto.listar()) == 10


def test_se_vazio_nao_apaga_dados_existentes(app):
    runner = app.test_cli_runner()
    runner.invoke(args=["init-db", "--exemplos"])
    with app.app_context():
        Produto.excluir(Produto.buscar_por_codigo("78912939").id)

    resultado = runner.invoke(args=["init-db", "--exemplos", "--se-vazio"])
    assert "nada foi alterado" in resultado.output
    with app.app_context():
        assert len(Produto.listar()) == 9  # a exclusão foi mantida


def test_se_vazio_cria_quando_nao_ha_tabelas(tmp_path):
    from app import create_app

    app = create_app({"TESTING": True, "DATABASE_URL": f"sqlite:///{tmp_path / 'novo.db'}"})
    resultado = app.test_cli_runner().invoke(args=["init-db", "--exemplos", "--se-vazio"])
    assert "Banco de dados criado" in resultado.output
    with app.app_context():
        assert len(Produto.listar()) == 10
