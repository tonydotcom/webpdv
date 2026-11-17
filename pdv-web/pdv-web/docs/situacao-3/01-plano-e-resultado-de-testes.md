# Plano e resultado de testes

Os testes são de dois tipos:

- **Verificação**: "construímos o produto **certo do jeito certo**?" São os testes automatizados e os casos
  de teste executados pelo desenvolvedor, conferindo cada requisito e regra de negócio.
- **Validação**: "construímos o produto **certo**?" São os testes feitos por 5 usuários (colegas ou
  profissionais), registrados no formulário de avaliação.

## 1. Verificação: testes automatizados

| Suíte | Ferramenta | Arquivo | O que cobre | Testes |
|---|---|---|---|---|
| Utilitário de dinheiro | pytest | `tests/test_dinheiro.py` | Conversão e formatação de R$ | 20 |
| Model Produto | pytest | `tests/test_produto_model.py` | RN01–RN04, RN10, RN11, busca | 26 |
| Model Venda | pytest | `tests/test_venda_model.py` | RN05–RN09, RN12, transação, resumo do dia | 18 |
| Controllers | pytest (cliente de teste do Flask) | `tests/test_controllers.py` | Todas as rotas, respostas HTTP, mensagens, páginas 404/500 | 26 |
| Comando de inicialização do banco | pytest | `tests/test_init_db.py` | Criação das tabelas e `--se-vazio` (não apaga dados na hospedagem) | 3 |
| Front-end (carrinho) | node:test | `tests/js/carrinho.test.js` | Total, troco, estoque, quantidade, formato do envio | 9 |
| **Total** | | | | **102** |

**Como executar**

```bash
pytest -v                               # back-end
node --test tests/js/carrinho.test.js   # front-end
```

**Resultado:** 102 de 102 aprovados. A saída completa está em
[`resultado-testes-automatizados.txt`](resultado-testes-automatizados.txt).

> Os testes do back-end rodam num banco SQLite temporário, recriado a cada teste, para serem rápidos e
> independentes. O script oficial do PostgreSQL foi validado à parte (ver
> [Projeto do banco, seção 4.3](../situacao-1/04-projeto-banco-de-dados.md#validação-do-projeto-físico)).

## 2. Verificação: casos de teste funcionais (pelo navegador)

Executados de ponta a ponta no navegador Chrome, com o banco de exemplo (`init-db --exemplos`).

| ID | Requisito | Passos | Resultado esperado | Resultado obtido |
|---|---|---|---|---|
| CT01 | RF01 | Cadastrar o produto 7891234567895, "Biscoito Recheado 140g", 3,79, estoque 24 | Mensagem "cadastrado com sucesso" e produto na lista | ✅ Aprovado |
| CT02 | RF01 / RN01–RN04 | Salvar com código `123`, nome vazio, preço `abc` | Os 4 campos ficam em vermelho com mensagens; o texto digitado continua nos campos | ✅ Aprovado |
| CT03 | RF02 | Editar o preço do leite para 5,99 | Novo preço na lista | ✅ Aprovado |
| CT04 | RF03 / RN10 | Excluir um produto já vendido | Mensagem "não pode ser excluído" | ✅ Aprovado |
| CT05 | RF04 | Buscar "leite" | Somente produtos com "leite" no nome | ✅ Aprovado |
| CT06 | RF05 | Abrir Nova venda | Cursor no campo de código | ✅ Aprovado |
| CT07 | RF05 | Ler 7891000100103 com Qtd. 2 | Leite com qtd. 2 e subtotal R$ 10,98 | ✅ Aprovado |
| CT08 | RF05 | Ler 0000000000000 | "Nenhum produto com o código 0000000000000." | ✅ Aprovado |
| CT09 | RN06 | Ler o achocolatado (estoque 3) com Qtd. 9 | "Estoque insuficiente… Disponível: 3." e item não adicionado | ✅ Aprovado |
| CT10 | RF06 | Buscar "caf" pelo nome e clicar no resultado | Café adicionado à venda | ✅ Aprovado |
| CT11 | RF08 / RN08 | Dinheiro, total R$ 32,67, recebido 50 | Troco R$ 17,33 | ✅ Aprovado |
| CT12 | RN08 | Dinheiro sem valor recebido | Botão Finalizar desabilitado | ✅ Aprovado |
| CT13 | RF09 / RN09 | Finalizar com F10 | Janela "Venda #1 finalizada!" e estoque reduzido | ✅ Aprovado |
| CT14 | RF10 | Abrir Ver comprovante | Itens, total, valor recebido e troco corretos | ✅ Aprovado |
| CT15 | RF11 | Abrir o painel após a venda | Vendas hoje = 1, faturamento R$ 32,67, estoque baixo listado | ✅ Aprovado |
| CT16 | RNF06 | Acessar /xyz | Página 404 amigável | ✅ Aprovado |
| CT17 | RNF01 | Abrir Nova venda em tela de celular (390 px) | Layout em uma coluna, todos os campos utilizáveis | ✅ Aprovado |

As capturas de tela desses testes estão em [`docs/imagens/`](../imagens/).

## 3. Validação: testes com usuários

1. Publicar o sistema num endereço acessível (ver README, seção "Publicar para os testadores").
2. Enviar aos 5 testadores o link do sistema e o [formulário de avaliação](02-formulario-de-avaliacao.md).
3. Consolidar as respostas em [`03-relatorio-de-validacao.md`](03-relatorio-de-validacao.md).
4. Corrigir o que for pertinente, rodar os testes automatizados de novo e registrar as mudanças no relatório.
5. Gerar o PDF das 5 avaliações e gravar o vídeo das mudanças.
