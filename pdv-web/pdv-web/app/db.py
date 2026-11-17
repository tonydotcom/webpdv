"""Acesso ao banco de dados.

O sistema usa PostgreSQL (DATABASE_URL=postgresql://...). Para facilitar os
testes automatizados e quem quiser rodar sem instalar nada, também aceita
SQLite (DATABASE_URL=sqlite:///caminho/arquivo.db).

Os models escrevem o SQL com o marcador %s; esta classe troca por ? quando o
banco é SQLite. Assim o mesmo SQL serve para os dois bancos.
"""
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

import click
from flask import current_app, g
from flask.cli import with_appcontext

PASTA_DATABASE = Path(__file__).resolve().parent.parent / "database"

# SQLite não converte datetime sozinho a partir do Python 3.12.
sqlite3.register_adapter(datetime, lambda d: d.isoformat(sep=" "))
sqlite3.register_converter("TIMESTAMP", lambda b: datetime.fromisoformat(b.decode()))


class Database:
    def __init__(self, conexao, dialeto):
        self.conexao = conexao
        self.dialeto = dialeto  # "postgres" ou "sqlite"

    def _sql(self, sql):
        return sql.replace("%s", "?") if self.dialeto == "sqlite" else sql

    def _cursor(self, sql, params):
        cursor = self.conexao.cursor()
        cursor.execute(self._sql(sql), tuple(params))
        return cursor

    def buscar_todos(self, sql, params=()):
        return [dict(linha) for linha in self._cursor(sql, params).fetchall()]

    def buscar_um(self, sql, params=()):
        linha = self._cursor(sql, params).fetchone()
        return dict(linha) if linha else None

    def executar(self, sql, params=()):
        """Executa INSERT/UPDATE/DELETE e devolve quantas linhas foram afetadas."""
        return self._cursor(sql, params).rowcount

    def inserir(self, sql, params=()):
        """Executa um INSERT ... RETURNING id e devolve o id gerado."""
        return self.buscar_um(sql, params)["id"]

    @contextmanager
    def transacao(self):
        try:
            yield self
            self.conexao.commit()
        except Exception:
            self.conexao.rollback()
            raise

    def executar_script(self, script):
        if self.dialeto == "sqlite":
            self.conexao.executescript(script)
        else:
            self.conexao.cursor().execute(script)
        self.conexao.commit()

    def fechar(self):
        self.conexao.close()


def conectar(url):
    if url.startswith(("postgresql://", "postgres://")):
        import psycopg2
        import psycopg2.extras

        conexao = psycopg2.connect(url, cursor_factory=psycopg2.extras.RealDictCursor)
        return Database(conexao, "postgres")

    if url.startswith("sqlite:///"):
        conexao = sqlite3.connect(url[len("sqlite:///"):], detect_types=sqlite3.PARSE_DECLTYPES)
        conexao.row_factory = sqlite3.Row
        conexao.execute("PRAGMA foreign_keys = ON")
        return Database(conexao, "sqlite")

    raise ValueError(f"DATABASE_URL não suportada: {url}")


def get_db():
    """Uma conexão por requisição, guardada em flask.g."""
    if "db" not in g:
        g.db = conectar(current_app.config["DATABASE_URL"])
    return g.db


def fechar_db(_erro=None):
    db = g.pop("db", None)
    if db is not None:
        db.fechar()


def criar_tabelas(com_exemplos=False):
    db = get_db()
    arquivo = "schema.sql" if db.dialeto == "postgres" else "schema_sqlite.sql"
    db.executar_script((PASTA_DATABASE / arquivo).read_text(encoding="utf-8"))
    if com_exemplos:
        db.executar_script((PASTA_DATABASE / "seed.sql").read_text(encoding="utf-8"))


def tabelas_existem():
    db = get_db()
    try:
        db.buscar_um("SELECT 1 FROM produto LIMIT 1")
        return True
    except Exception:
        db.conexao.rollback()  # no PostgreSQL, a transação com erro precisa ser desfeita
        return False


@click.command("init-db")
@click.option("--exemplos", is_flag=True, help="Também insere produtos de exemplo.")
@click.option("--se-vazio", is_flag=True,
              help="Só cria as tabelas se ainda não existirem (não apaga dados). Use na hospedagem.")
@with_appcontext
def init_db_command(exemplos, se_vazio):
    """Apaga e recria as tabelas do banco (ou só cria, com --se-vazio)."""
    if se_vazio and tabelas_existem():
        click.echo("Tabelas já existem; nada foi alterado.")
        return
    criar_tabelas(com_exemplos=exemplos)
    click.echo("Banco de dados criado." + (" Produtos de exemplo inseridos." if exemplos else ""))


def init_app(app):
    app.teardown_appcontext(fechar_db)
    app.cli.add_command(init_db_command)
