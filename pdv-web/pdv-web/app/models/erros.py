"""Erros de regra de negócio. Os controllers os transformam em mensagens na tela."""


class ErroValidacao(Exception):
    """Dados inválidos. `erros` é um dicionário {campo: mensagem}."""

    def __init__(self, erros):
        if isinstance(erros, str):
            erros = {"geral": erros}
        self.erros = erros
        super().__init__("; ".join(erros.values()))


class EstoqueInsuficiente(ErroValidacao):
    pass


class NaoEncontrado(Exception):
    pass
