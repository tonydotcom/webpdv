"""Controller de vendas: tela de caixa, finalização e histórico."""
from datetime import date

from flask import Blueprint, abort, jsonify, render_template, request, url_for

from app.models import FORMAS_PAGAMENTO, ErroValidacao, NaoEncontrado, Venda
from app.utils.dinheiro import reais_para_centavos

bp = Blueprint("vendas", __name__, url_prefix="/vendas")


@bp.get("/nova")
def nova():
    return render_template("vendas/nova.html", formas_pagamento=FORMAS_PAGAMENTO)


@bp.post("/")
def finalizar():
    """Recebe a venda em JSON (enviada pelo JavaScript da tela de caixa)."""
    dados = request.get_json(silent=True)
    if not isinstance(dados, dict):
        return jsonify(erro="Requisição inválida."), 400

    valor_recebido = None
    if dados.get("forma_pagamento") == "DINHEIRO":
        try:
            valor_recebido = reais_para_centavos(dados.get("valor_recebido"))
        except ValueError:
            return jsonify(erro="Valor recebido inválido. Use o formato 50,00."), 400

    try:
        venda = Venda.registrar(dados.get("itens"), dados.get("forma_pagamento"), valor_recebido)
    except ErroValidacao as erro:
        return jsonify(erro=str(erro), campos=erro.erros), 400

    return jsonify(
        id=venda.id,
        total_centavos=venda.total_centavos,
        troco_centavos=venda.troco_centavos,
        url=url_for("vendas.detalhe", venda_id=venda.id),
    ), 201


@bp.get("/")
def listar():
    texto_data = request.args.get("data", "")
    data_filtro = None
    erro_data = None
    if texto_data:
        try:
            data_filtro = date.fromisoformat(texto_data)
        except ValueError:
            erro_data = "Data inválida."
    vendas = Venda.listar(data_filtro)
    total = sum(v.total_centavos for v in vendas)
    return render_template(
        "vendas/lista.html", vendas=vendas, total=total, data=texto_data, erro_data=erro_data
    )


@bp.get("/<int:venda_id>")
def detalhe(venda_id):
    try:
        venda = Venda.buscar_por_id(venda_id)
    except NaoEncontrado:
        abort(404)
    return render_template("vendas/detalhe.html", venda=venda)
