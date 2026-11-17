-- Dados de exemplo para demonstração e testes com usuários.
-- Funciona tanto no PostgreSQL quanto no SQLite.

INSERT INTO produto (codigo_barras, nome, preco_centavos, estoque) VALUES
    ('7891000100103', 'Leite Integral 1L',            549,  40),
    ('7891910000197', 'Açúcar Refinado 1kg',          479,  25),
    ('7896004000015', 'Arroz Tipo 1 5kg',            2899,  15),
    ('7896102000106', 'Feijão Carioca 1kg',           849,  20),
    ('7891149101009', 'Café Torrado e Moído 500g',   1790,  12),
    ('7894900011517', 'Refrigerante Cola 2L',         999,  30),
    ('7891024134702', 'Creme Dental 90g',             459,  18),
    ('7896036090008', 'Sabão em Pó 1kg',             1299,   4),
    ('7891000053508', 'Achocolatado em Pó 400g',      799,   3),
    ('78912939',      'Chiclete Hortelã',             150, 100);
