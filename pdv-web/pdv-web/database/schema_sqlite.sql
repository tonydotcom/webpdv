-- Versão SQLite do schema, usada apenas nos testes automatizados e para
-- rodar o sistema localmente sem instalar o PostgreSQL.
-- O projeto físico oficial é database/schema.sql (PostgreSQL).

DROP TABLE IF EXISTS item_venda;
DROP TABLE IF EXISTS venda;
DROP TABLE IF EXISTS produto;

CREATE TABLE produto (
    id              INTEGER       PRIMARY KEY AUTOINCREMENT,
    codigo_barras   VARCHAR(14)   NOT NULL UNIQUE,
    nome            VARCHAR(100)  NOT NULL CHECK (length(trim(nome)) >= 3),
    preco_centavos  INTEGER       NOT NULL CHECK (preco_centavos > 0),
    estoque         INTEGER       NOT NULL DEFAULT 0 CHECK (estoque >= 0),
    criado_em       TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX ix_produto_nome ON produto (nome);

CREATE TABLE venda (
    id                       INTEGER      PRIMARY KEY AUTOINCREMENT,
    data_hora                TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    total_centavos           INTEGER      NOT NULL CHECK (total_centavos > 0),
    forma_pagamento          VARCHAR(10)  NOT NULL CHECK (forma_pagamento IN ('DINHEIRO', 'DEBITO', 'CREDITO', 'PIX')),
    valor_recebido_centavos  INTEGER      NULL,
    troco_centavos           INTEGER      NOT NULL DEFAULT 0 CHECK (troco_centavos >= 0)
);

CREATE INDEX ix_venda_data_hora ON venda (data_hora);

CREATE TABLE item_venda (
    id                         INTEGER  PRIMARY KEY AUTOINCREMENT,
    venda_id                   INTEGER  NOT NULL REFERENCES venda (id) ON DELETE CASCADE,
    produto_id                 INTEGER  NOT NULL REFERENCES produto (id) ON DELETE RESTRICT,
    quantidade                 INTEGER  NOT NULL CHECK (quantidade > 0),
    preco_unitario_centavos    INTEGER  NOT NULL CHECK (preco_unitario_centavos > 0),
    UNIQUE (venda_id, produto_id)
);

CREATE INDEX ix_item_venda_produto ON item_venda (produto_id);
