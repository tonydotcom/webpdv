# 5. Dicionário de dados

Banco: `pdv` · SGBD: PostgreSQL 14+ · Script: [`database/schema.sql`](../../database/schema.sql)

Legenda: **PK** = chave primária · **FK** = chave estrangeira · **UK** = valor único · **NN** = obrigatório (NOT NULL)

## Tabela `produto`

Itens que a loja vende.

| Coluna | Tipo | Restrições | Padrão | Descrição | Exemplo |
|---|---|---|---|---|---|
| id | SERIAL | PK, NN | auto | Identificador do produto | 1 |
| codigo_barras | VARCHAR(14) | UK, NN, CHECK só dígitos (8 a 14) | – | Código EAN/GTIN da embalagem | 7891000100103 |
| nome | VARCHAR(100) | NN, CHECK ≥ 3 caracteres | – | Nome exibido na venda e no comprovante | Leite Integral 1L |
| preco_centavos | INTEGER | NN, CHECK > 0 | – | Preço de venda atual, em centavos | 549 (= R$ 5,49) |
| estoque | INTEGER | NN, CHECK ≥ 0 | 0 | Quantidade disponível | 40 |
| criado_em | TIMESTAMP | NN | CURRENT_TIMESTAMP | Data e hora do cadastro | 2026-11-16 14:20:00 |

Índices: `uq_produto_codigo_barras` (único), `ix_produto_nome`.

## Tabela `venda`

Cabeçalho de cada venda finalizada.

| Coluna | Tipo | Restrições | Padrão | Descrição | Exemplo |
|---|---|---|---|---|---|
| id | SERIAL | PK, NN | auto | Número da venda | 15 |
| data_hora | TIMESTAMP | NN | CURRENT_TIMESTAMP | Momento em que a venda foi finalizada | 2026-11-16 14:29:03 |
| total_centavos | INTEGER | NN, CHECK > 0 | – | Soma dos subtotais dos itens, em centavos | 3267 |
| forma_pagamento | VARCHAR(10) | NN, CHECK em (DINHEIRO, DEBITO, CREDITO, PIX) | – | Como o cliente pagou | DINHEIRO |
| valor_recebido_centavos | INTEGER | CHECK ≥ total se DINHEIRO; nulo nas outras formas | NULL | Valor entregue pelo cliente em dinheiro | 5000 |
| troco_centavos | INTEGER | NN, CHECK ≥ 0 | 0 | valor_recebido − total (0 se não for dinheiro) | 1733 |

Índices: `ix_venda_data_hora`.

## Tabela `item_venda`

Produtos de cada venda. Resolve a relação N:N entre `venda` e `produto`.

| Coluna | Tipo | Restrições | Padrão | Descrição | Exemplo |
|---|---|---|---|---|---|
| id | SERIAL | PK, NN | auto | Identificador do item | 42 |
| venda_id | INTEGER | FK → venda.id (ON DELETE CASCADE), NN | – | Venda a que o item pertence | 15 |
| produto_id | INTEGER | FK → produto.id (ON DELETE RESTRICT), NN | – | Produto vendido | 1 |
| quantidade | INTEGER | NN, CHECK > 0 | – | Unidades vendidas | 2 |
| preco_unitario_centavos | INTEGER | NN, CHECK > 0 | – | Preço do produto **no momento da venda** | 549 |

Restrições adicionais: `uq_item_venda_produto` (venda_id, produto_id) garante que um produto aparece uma
única vez por venda; quantidades repetidas são somadas. Índice: `ix_item_venda_produto`.

## Domínio: forma_pagamento

| Valor gravado | Exibido na tela | Exige valor recebido? |
|---|---|---|
| DINHEIRO | Dinheiro | Sim (calcula troco) |
| DEBITO | Cartão de débito | Não |
| CREDITO | Cartão de crédito | Não |
| PIX | Pix | Não |
