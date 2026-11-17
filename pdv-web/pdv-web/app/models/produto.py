"""Model Produto: regras de negócio e persistência dos produtos."""
import re
from dataclasses import dataclass, field
from datetime import datetime

from app.db import get_db
from app.models.erros import ErroValidacao, NaoEncontrado
from app.utils.dinheiro import reais_para_centavos

ESTOQUE_BAIXO = 5  # RN11: a tela inicial avisa quando o estoque chega a este valor


@dataclass
class Produto:
    codigo_barras: str
    nome: str
    preco_centavos: int
    estoque: int
    id: int | None = None
    criado_em: datetime | None = field(default=None, compare=False)

    # ------------------------------------------------------------------ #
    # Validação
    # ------------------------------------------------------------------ #
    @staticmethod
    def a_partir_do_formulario(dados, produto_id=None):
        """Valida os dados digitados no formulário e devolve um Produto.

        Lança ErroValidacao com uma mensagem por campo inválido.
        """
        erros = {}

        codigo = (dados.get("codigo_barras") or "").strip()
        if not codigo:
            erros["codigo_barras"] = "Informe o código de barras."
        elif not re.fullmatch(r"\d{8,14}", codigo):
            erros["codigo_barras"] = "O código de barras deve ter de 8 a 14 números."

        nome = " ".join((dados.get("nome") or "").split())
        if len(nome) < 3:
            erros["nome"] = "O nome deve ter pelo menos 3 letras."
        elif len(nome) > 100:
            erros["nome"] = "O nome deve ter no máximo 100 caracteres."

        preco = 0
        try:
            preco = reais_para_centavos(dados.get("preco"))
            if preco <= 0:
                erros["preco"] = "O preço deve ser maior que zero."
        except ValueError:
            erros["preco"] = "Preço inválido. Use o formato 12,50."

        estoque = 0
        texto_estoque = str(dados.get("estoque", "")).strip()
        if not texto_estoque.isdigit():
            erros["estoque"] = "O estoque deve ser um número inteiro igual ou maior que zero."
        else:
            estoque = int(texto_estoque)

        if "codigo_barras" not in erros:
            existente = Produto.buscar_por_codigo(codigo)
            if existente and existente.id != produto_id:
                erros["codigo_barras"] = f"Já existe um produto com este código: {existente.nome}."

        if erros:
            raise ErroValidacao(erros)
        return Produto(codigo, nome, preco, estoque, id=produto_id)

    # ------------------------------------------------------------------ #
    # Consultas
    # ------------------------------------------------------------------ #
    @staticmethod
    def listar(busca=None):
        sql = "SELECT * FROM produto"
        params = []
        if busca:
            sql += " WHERE LOWER(nome) LIKE %s OR codigo_barras = %s"
            params = [f"%{busca.strip().lower()}%", busca.strip()]
        sql += " ORDER BY nome"
        return [Produto(**linha) for linha in get_db().buscar_todos(sql, params)]

    @staticmethod
    def listar_estoque_baixo():
        linhas = get_db().buscar_todos(
            "SELECT * FROM produto WHERE estoque <= %s ORDER BY estoque, nome", [ESTOQUE_BAIXO]
        )
        return [Produto(**linha) for linha in linhas]

    @staticmethod
    def buscar_por_id(produto_id):
        linha = get_db().buscar_um("SELECT * FROM produto WHERE id = %s", [produto_id])
        if not linha:
            raise NaoEncontrado(f"Produto {produto_id} não encontrado.")
        return Produto(**linha)

    @staticmethod
    def buscar_por_codigo(codigo_barras):
        linha = get_db().buscar_um(
            "SELECT * FROM produto WHERE codigo_barras = %s", [str(codigo_barras).strip()]
        )
        return Produto(**linha) if linha else None

    # ------------------------------------------------------------------ #
    # Gravação
    # ------------------------------------------------------------------ #
    def salvar(self):
        db = get_db()
        with db.transacao():
            if self.id is None:
                self.id = db.inserir(
                    "INSERT INTO produto (codigo_barras, nome, preco_centavos, estoque) "
                    "VALUES (%s, %s, %s, %s) RETURNING id",
                    [self.codigo_barras, self.nome, self.preco_centavos, self.estoque],
                )
            else:
                alteradas = db.executar(
                    "UPDATE produto SET codigo_barras = %s, nome = %s, preco_centavos = %s, "
                    "estoque = %s WHERE id = %s",
                    [self.codigo_barras, self.nome, self.preco_centavos, self.estoque, self.id],
                )
                if alteradas == 0:
                    raise NaoEncontrado(f"Produto {self.id} não encontrado.")
        return self

    @staticmethod
    def excluir(produto_id):
        """RN10: produto que já foi vendido não pode ser excluído (mantém o histórico)."""
        produto = Produto.buscar_por_id(produto_id)
        db = get_db()
        vendido = db.buscar_um(
            "SELECT COUNT(*) AS total FROM item_venda WHERE produto_id = %s", [produto_id]
        )["total"]
        if vendido:
            raise ErroValidacao(
                f"O produto \"{produto.nome}\" já aparece em vendas e não pode ser excluído. "
                "Se não for mais vendido, deixe o estoque em zero."
            )
        with db.transacao():
            db.executar("DELETE FROM produto WHERE id = %s", [produto_id])
        return produto

    @property
    def estoque_baixo(self):
        return self.estoque <= ESTOQUE_BAIXO

    def para_json(self):
        return {
            "id": self.id,
            "codigo_barras": self.codigo_barras,
            "nome": self.nome,
            "preco_centavos": self.preco_centavos,
            "estoque": self.estoque,
        }
