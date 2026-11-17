"""Model Venda: registra vendas, baixa o estoque e consulta o histórico."""
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from app.db import get_db
from app.models.erros import ErroValidacao, EstoqueInsuficiente, NaoEncontrado

FORMAS_PAGAMENTO = {
    "DINHEIRO": "Dinheiro",
    "DEBITO": "Cartão de débito",
    "CREDITO": "Cartão de crédito",
    "PIX": "Pix",
}


@dataclass
class ItemVenda:
    produto_id: int
    quantidade: int
    preco_unitario_centavos: int
    nome: str = ""
    codigo_barras: str = ""

    @property
    def subtotal_centavos(self):
        return self.quantidade * self.preco_unitario_centavos


@dataclass
class Venda:
    total_centavos: int
    forma_pagamento: str
    valor_recebido_centavos: int | None = None
    troco_centavos: int = 0
    id: int | None = None
    data_hora: datetime | None = None
    itens: list = field(default_factory=list)

    @property
    def forma_pagamento_descricao(self):
        return FORMAS_PAGAMENTO.get(self.forma_pagamento, self.forma_pagamento)

    @property
    def quantidade_itens(self):
        return sum(item.quantidade for item in self.itens)

    # ------------------------------------------------------------------ #
    # Registrar venda
    # ------------------------------------------------------------------ #
    @staticmethod
    def registrar(itens, forma_pagamento, valor_recebido_centavos=None):
        """Registra uma venda.

        itens: lista de {"produto_id": int, "quantidade": int}
        O preço é sempre lido do banco, nunca do navegador.
        Tudo acontece numa única transação: ou a venda inteira é gravada
        (com a baixa de estoque), ou nada é gravado.
        """
        quantidades = Venda._validar_itens(itens)

        if forma_pagamento not in FORMAS_PAGAMENTO:
            raise ErroValidacao({"forma_pagamento": "Escolha uma forma de pagamento válida."})

        db = get_db()
        with db.transacao():
            itens_venda = []
            for produto_id, quantidade in quantidades.items():
                produto = db.buscar_um("SELECT * FROM produto WHERE id = %s", [produto_id])
                if not produto:
                    raise ErroValidacao(f"Produto {produto_id} não encontrado.")
                if quantidade > produto["estoque"]:
                    raise EstoqueInsuficiente(
                        f"Estoque insuficiente para \"{produto['nome']}\": "
                        f"pedido {quantidade}, disponível {produto['estoque']}."
                    )
                itens_venda.append(
                    ItemVenda(produto_id, quantidade, produto["preco_centavos"], produto["nome"],
                              produto["codigo_barras"])
                )

            total = sum(item.subtotal_centavos for item in itens_venda)
            troco = 0
            if forma_pagamento == "DINHEIRO":
                if valor_recebido_centavos is None:
                    raise ErroValidacao({"valor_recebido": "Informe o valor recebido em dinheiro."})
                if valor_recebido_centavos < total:
                    raise ErroValidacao({"valor_recebido": "O valor recebido é menor que o total da venda."})
                troco = valor_recebido_centavos - total
            else:
                valor_recebido_centavos = None

            venda = Venda(total, forma_pagamento, valor_recebido_centavos, troco,
                          data_hora=datetime.now().replace(microsecond=0), itens=itens_venda)
            venda.id = db.inserir(
                "INSERT INTO venda (data_hora, total_centavos, forma_pagamento, "
                "valor_recebido_centavos, troco_centavos) VALUES (%s, %s, %s, %s, %s) RETURNING id",
                [venda.data_hora, total, forma_pagamento, valor_recebido_centavos, troco],
            )

            for item in itens_venda:
                db.executar(
                    "INSERT INTO item_venda (venda_id, produto_id, quantidade, preco_unitario_centavos) "
                    "VALUES (%s, %s, %s, %s)",
                    [venda.id, item.produto_id, item.quantidade, item.preco_unitario_centavos],
                )
                # Baixa condicional: se outro caixa vendeu o mesmo produto ao mesmo
                # tempo e o estoque acabou, nenhuma linha é alterada e a venda é desfeita.
                alteradas = db.executar(
                    "UPDATE produto SET estoque = estoque - %s WHERE id = %s AND estoque >= %s",
                    [item.quantidade, item.produto_id, item.quantidade],
                )
                if alteradas == 0:
                    raise EstoqueInsuficiente(f"Estoque insuficiente para \"{item.nome}\".")
        return venda

    @staticmethod
    def _validar_itens(itens):
        """Junta itens repetidos e valida as quantidades. Devolve {produto_id: quantidade}."""
        if not itens:
            raise ErroValidacao("Adicione pelo menos um produto antes de finalizar a venda.")
        quantidades = {}
        for item in itens:
            try:
                produto_id = int(item["produto_id"])
                quantidade = int(item["quantidade"])
            except (KeyError, TypeError, ValueError):
                raise ErroValidacao("Item da venda inválido.")
            if quantidade < 1:
                raise ErroValidacao("A quantidade de cada item deve ser pelo menos 1.")
            quantidades[produto_id] = quantidades.get(produto_id, 0) + quantidade
        return quantidades

    # ------------------------------------------------------------------ #
    # Consultas
    # ------------------------------------------------------------------ #
    @staticmethod
    def _de_linha(linha):
        return Venda(
            id=linha["id"],
            data_hora=linha["data_hora"],
            total_centavos=linha["total_centavos"],
            forma_pagamento=linha["forma_pagamento"],
            valor_recebido_centavos=linha["valor_recebido_centavos"],
            troco_centavos=linha["troco_centavos"],
        )

    @staticmethod
    def listar(data=None):
        """Lista as vendas, opcionalmente de um único dia (date)."""
        sql = "SELECT * FROM venda"
        params = []
        if data:
            inicio = datetime.combine(data, datetime.min.time())
            sql += " WHERE data_hora >= %s AND data_hora < %s"
            params = [inicio, inicio + timedelta(days=1)]
        sql += " ORDER BY data_hora DESC, id DESC"
        return [Venda._de_linha(linha) for linha in get_db().buscar_todos(sql, params)]

    @staticmethod
    def buscar_por_id(venda_id):
        db = get_db()
        linha = db.buscar_um("SELECT * FROM venda WHERE id = %s", [venda_id])
        if not linha:
            raise NaoEncontrado(f"Venda {venda_id} não encontrada.")
        venda = Venda._de_linha(linha)
        venda.itens = [
            ItemVenda(i["produto_id"], i["quantidade"], i["preco_unitario_centavos"], i["nome"],
                      i["codigo_barras"])
            for i in db.buscar_todos(
                "SELECT iv.*, p.nome, p.codigo_barras FROM item_venda iv "
                "JOIN produto p ON p.id = iv.produto_id WHERE iv.venda_id = %s ORDER BY iv.id",
                [venda_id],
            )
        ]
        return venda

    @staticmethod
    def resumo_do_dia(data):
        inicio = datetime.combine(data, datetime.min.time())
        linha = get_db().buscar_um(
            "SELECT COUNT(*) AS quantidade, COALESCE(SUM(total_centavos), 0) AS total "
            "FROM venda WHERE data_hora >= %s AND data_hora < %s",
            [inicio, inicio + timedelta(days=1)],
        )
        return {"quantidade": int(linha["quantidade"]), "total_centavos": int(linha["total"])}
