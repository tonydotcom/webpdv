"""Controller de produtos: recebe as requisições, chama o model e escolhe a view."""
from flask import Blueprint, abort, flash, jsonify, redirect, render_template, request, url_for

from app.models import ErroValidacao, NaoEncontrado, Produto
from app.utils.dinheiro import centavos_para_campo

bp = Blueprint("produtos", __name__, url_prefix="/produtos")


@bp.get("/")
def listar():
    busca = request.args.get("busca", "").strip()
    return render_template("produtos/lista.html", produtos=Produto.listar(busca), busca=busca)


@bp.route("/novo", methods=["GET", "POST"])
def novo():
    dados, erros = {}, {}
    if request.method == "POST":
        dados = request.form
        try:
            produto = Produto.a_partir_do_formulario(dados).salvar()
            flash(f"Produto \"{produto.nome}\" cadastrado com sucesso.", "sucesso")
            return redirect(url_for("produtos.listar"))
        except ErroValidacao as erro:
            erros = erro.erros
            flash("Corrija os campos destacados.", "erro")
    return render_template("produtos/form.html", titulo="Novo produto", dados=dados, erros=erros), (
        400 if erros else 200
    )


@bp.route("/<int:produto_id>/editar", methods=["GET", "POST"])
def editar(produto_id):
    try:
        produto = Produto.buscar_por_id(produto_id)
    except NaoEncontrado:
        abort(404)

    dados = {
        "codigo_barras": produto.codigo_barras,
        "nome": produto.nome,
        "preco": centavos_para_campo(produto.preco_centavos),
        "estoque": produto.estoque,
    }
    erros = {}
    if request.method == "POST":
        dados = request.form
        try:
            produto = Produto.a_partir_do_formulario(dados, produto_id=produto_id).salvar()
            flash(f"Produto \"{produto.nome}\" atualizado.", "sucesso")
            return redirect(url_for("produtos.listar"))
        except ErroValidacao as erro:
            erros = erro.erros
            flash("Corrija os campos destacados.", "erro")
    return render_template(
        "produtos/form.html", titulo="Editar produto", dados=dados, erros=erros, produto_id=produto_id
    ), (400 if erros else 200)


@bp.post("/<int:produto_id>/excluir")
def excluir(produto_id):
    try:
        produto = Produto.excluir(produto_id)
        flash(f"Produto \"{produto.nome}\" excluído.", "sucesso")
    except NaoEncontrado:
        abort(404)
    except ErroValidacao as erro:
        flash(str(erro), "erro")
    return redirect(url_for("produtos.listar"))


@bp.get("/api/codigo/<codigo>")
def buscar_por_codigo(codigo):
    """Usado pela tela de venda para buscar o produto pelo código de barras."""
    produto = Produto.buscar_por_codigo(codigo)
    if not produto:
        return jsonify(erro=f"Nenhum produto com o código {codigo}."), 404
    return jsonify(produto.para_json())


@bp.get("/api/busca")
def buscar_por_nome():
    """Busca por nome, para quando o produto não tem código de barras legível."""
    termo = request.args.get("q", "").strip()
    if len(termo) < 2:
        return jsonify([])
    return jsonify([p.para_json() for p in Produto.listar(termo)[:10]])
