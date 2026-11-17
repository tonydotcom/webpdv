# Roteiro dos vídeos

> **Atenção ao tempo:** o material pede, na Situação 2, um vídeo narrado de "pelo menos cinco minutos" e,
> na Situação 3, um vídeo "de até cinco minutos". Confirme com o tutor. Este roteiro dura cerca de
> **5 minutos**, o que atende às duas exigências.

Dica: antes de gravar, rode `flask --app run init-db --exemplos` para começar com o banco limpo.
Grave a tela em 1280×720 ou mais (OBS Studio ou a gravação de tela do Windows, Win+Alt+R).

## Vídeo 1: Solução em funcionamento (Situação 2)

| Tempo | Tela | Fala (sugestão) |
|---|---|---|
| 0:00–0:30 | README no GitHub | "Olá, sou o Tony. Este é o PDV Web, um ponto de venda para pequenos comércios, feito em Python com Flask no padrão MVC e banco PostgreSQL. O código e toda a documentação estão neste repositório." |
| 0:30–1:00 | Pastas no VS Code | Mostrar `app/models`, `app/controllers`, `app/templates`: "Aqui ficam o Model, com as regras de negócio, o Controller, com as rotas, e as Views." |
| 1:00–1:20 | Painel | "A tela inicial mostra as vendas do dia e os produtos com estoque baixo." |
| 1:20–2:10 | Produtos | Cadastrar um produto com erro (código `123`, preço `abc`) e mostrar as mensagens; corrigir e salvar; buscar pelo nome; tentar excluir um produto já vendido e mostrar o aviso. |
| 2:10–3:30 | Nova venda | Ler 2 produtos pelo código, um com quantidade 2; mostrar o erro de código inexistente; mostrar o erro de estoque insuficiente; adicionar um produto pela busca por nome; remover um item; escolher Dinheiro, digitar o valor e mostrar o troco; finalizar com F10. |
| 3:30–4:00 | Comprovante e Vendas | Abrir o comprovante; mostrar a lista de vendas e o filtro por dia; voltar ao painel e mostrar o faturamento e o estoque atualizados. |
| 4:00–4:40 | Terminal | Rodar `pytest -v` e `node --test tests/js/carrinho.test.js`: "São 102 testes automatizados, do back-end e do front-end, todos passando." |
| 4:40–5:00 | README | "Obrigado! O link do sistema para teste e o formulário de avaliação estão no README." |

## Vídeo 2: Mudanças após os testes com usuários (Situação 3)

| Tempo | Conteúdo |
|---|---|
| 0:00–0:30 | Apresentação: quem testou (5 pessoas) e onde estão as avaliações (`docs/situacao-3/`) |
| 0:30–3:30 | Para cada problema relevante: mostrar como era, o que o testador relatou e como ficou depois da correção |
| 3:30–4:30 | Sugestões não adotadas e o motivo (fora do escopo, por exemplo) |
| 4:30–5:00 | Testes automatizados passando depois das correções e encerramento |
