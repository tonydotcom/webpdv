-- =====================================================================
-- PDV Web - Projeto físico do banco de dados
-- SGBD: PostgreSQL 14 ou superior
-- Execução: psql -U postgres -d pdv -f database/schema.sql
-- =====================================================================

DROP TABLE IF EXISTS item_venda;
DROP TABLE IF EXISTS venda;
DROP TABLE IF EXISTS produto;

-- ---------------------------------------------------------------------
-- PRODUTO: itens que a loja vende
-- ---------------------------------------------------------------------
CREATE TABLE produto (
    id              SERIAL        PRIMARY KEY,
    codigo_barras   VARCHAR(14)   NOT NULL,
    nome            VARCHAR(100)  NOT NULL,
    preco_centavos  INTEGER       NOT NULL,
    estoque         INTEGER       NOT NULL DEFAULT 0,
    criado_em       TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_produto_codigo_barras UNIQUE (codigo_barras),
    CONSTRAINT ck_produto_codigo_barras CHECK (codigo_barras ~ '^[0-9]{8,14}$'),
    CONSTRAINT ck_produto_nome          CHECK (char_length(trim(nome)) >= 3),
    CONSTRAINT ck_produto_preco         CHECK (preco_centavos > 0),
    CONSTRAINT ck_produto_estoque       CHECK (estoque >= 0)
);

CREATE INDEX ix_produto_nome ON produto (nome);

-- ---------------------------------------------------------------------
-- VENDA: cabeçalho de cada venda finalizada
-- ---------------------------------------------------------------------
CREATE TABLE venda (
    id                       SERIAL       PRIMARY KEY,
    data_hora                TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    total_centavos           INTEGER      NOT NULL,
    forma_pagamento          VARCHAR(10)  NOT NULL,
    valor_recebido_centavos  INTEGER      NULL,
    troco_centavos           INTEGER      NOT NULL DEFAULT 0,

    CONSTRAINT ck_venda_total     CHECK (total_centavos > 0),
    CONSTRAINT ck_venda_pagamento CHECK (forma_pagamento IN ('DINHEIRO', 'DEBITO', 'CREDITO', 'PIX')),
    CONSTRAINT ck_venda_troco     CHECK (troco_centavos >= 0),
    CONSTRAINT ck_venda_recebido  CHECK (
        (forma_pagamento = 'DINHEIRO' AND valor_recebido_centavos >= total_centavos)
        OR (forma_pagamento <> 'DINHEIRO' AND valor_recebido_centavos IS NULL)
    )
);

CREATE INDEX ix_venda_data_hora ON venda (data_hora);

-- ---------------------------------------------------------------------
-- ITEM_VENDA: produtos de cada venda (resolve o N:N entre venda e produto)
-- ---------------------------------------------------------------------
CREATE TABLE item_venda (
    id                         SERIAL   PRIMARY KEY,
    venda_id                   INTEGER  NOT NULL,
    produto_id                 INTEGER  NOT NULL,
    quantidade                 INTEGER  NOT NULL,
    preco_unitario_centavos    INTEGER  NOT NULL,

    CONSTRAINT fk_item_venda_venda   FOREIGN KEY (venda_id)   REFERENCES venda (id)   ON DELETE CASCADE,
    CONSTRAINT fk_item_venda_produto FOREIGN KEY (produto_id) REFERENCES produto (id) ON DELETE RESTRICT,
    CONSTRAINT uq_item_venda_produto UNIQUE (venda_id, produto_id),
    CONSTRAINT ck_item_quantidade    CHECK (quantidade > 0),
    CONSTRAINT ck_item_preco         CHECK (preco_unitario_centavos > 0)
);

CREATE INDEX ix_item_venda_produto ON item_venda (produto_id);
