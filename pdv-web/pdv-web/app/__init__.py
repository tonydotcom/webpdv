"""Fábrica da aplicação Flask (PDV Web).

Organização MVC:
  app/models       -> Model: regras de negócio e acesso ao banco
  app/templates    -> View: páginas HTML (Jinja2), com CSS e JavaScript em app/static
  app/controllers  -> Controller: rotas que ligam a View ao Model
"""
import logging
import os

from flask import Flask, jsonify, render_template, request

from app import db
from app.utils.dinheiro import formatar_reais


def create_app(config=None):
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.environ.get("SECRET_KEY", "troque-esta-chave-em-producao"),
        DATABASE_URL=os.environ.get("DATABASE_URL", "sqlite:///pdv.db"),
    )
    if config:
        app.config.update(config)

    db.init_app(app)

    from app.controllers import inicio_controller, produto_controller, venda_controller

    app.register_blueprint(inicio_controller.bp)
    app.register_blueprint(produto_controller.bp)
    app.register_blueprint(venda_controller.bp)

    app.add_template_filter(formatar_reais, "reais")
    app.add_template_filter(lambda d: d.strftime("%d/%m/%Y %H:%M") if d else "-", "data_hora")

    _registrar_tratamento_de_erros(app)
    return app


def _quer_json():
    """As rotas chamadas pelo JavaScript recebem o erro em JSON; as demais, uma página."""
    return request.path.startswith("/produtos/api/") or (
        request.path == "/vendas/" and request.method == "POST"
    )


def _registrar_tratamento_de_erros(app):
    @app.errorhandler(404)
    def nao_encontrado(_erro):
        if _quer_json():
            return jsonify(erro="Recurso não encontrado."), 404
        return render_template("erro.html", codigo=404,
                               mensagem="A página que você procurou não existe."), 404

    @app.errorhandler(405)
    def metodo_nao_permitido(_erro):
        return render_template("erro.html", codigo=405,
                               mensagem="Esta ação não é permitida nesta página."), 405

    @app.errorhandler(Exception)
    def erro_inesperado(erro):
        from werkzeug.exceptions import HTTPException

        if isinstance(erro, HTTPException):
            return erro
        logging.getLogger(__name__).exception("Erro inesperado")
        mensagem = "Ocorreu um erro inesperado. Tente novamente; se continuar, avise o suporte."
        if _quer_json():
            return jsonify(erro=mensagem), 500
        return render_template("erro.html", codigo=500, mensagem=mensagem), 500
