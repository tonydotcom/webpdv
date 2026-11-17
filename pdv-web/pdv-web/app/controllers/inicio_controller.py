"""Controller da tela inicial (painel do dia)."""
from datetime import date

from flask import Blueprint, render_template

from app.models import Produto, Venda

bp = Blueprint("inicio", __name__)


@bp.get("/")
def painel():
    hoje = date.today()
    return render_template(
        "inicio.html",
        resumo=Venda.resumo_do_dia(hoje),
        estoque_baixo=Produto.listar_estoque_baixo(),
        ultimas_vendas=Venda.listar(hoje)[:5],
    )
