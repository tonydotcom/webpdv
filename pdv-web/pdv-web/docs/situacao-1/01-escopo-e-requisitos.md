# 1. Escopo e requisitos

## 1.1 Visão geral

O **PDV Web** é um sistema de ponto de venda simples para pequenos comércios (mercearias, lojas de
conveniência, papelarias). O operador cadastra os produtos com preço e estoque, registra vendas lendo o
código de barras e o sistema calcula o total e o troco e baixa o estoque automaticamente.

**Problema.** Muitos pequenos comércios ainda anotam vendas em caderno ou planilha. Isso gera erro no
troco, estoque que não bate com a prateleira e nenhuma visão de quanto foi vendido no dia.

**Objetivo.** Oferecer um sistema web, acessível pelo navegador do computador do caixa, que registre
vendas de forma rápida e mantenha o estoque correto.

**Público-alvo (usuário).** O operador de caixa, que normalmente também é o dono ou o gerente da loja.

## 1.2 Escopo

| Dentro do escopo | Fora do escopo |
|---|---|
| Cadastro, edição, exclusão e busca de produtos | Emissão de nota fiscal (NFC-e/SAT) |
| Registro de vendas por código de barras ou nome | Integração com maquininha de cartão (TEF) |
| Pagamento em dinheiro (com troco), débito, crédito ou Pix | Controle de usuários e permissões |
| Baixa automática de estoque | Cadastro de clientes e fiado |
| Histórico de vendas com filtro por dia e comprovante | Compras e fornecedores |
| Painel do dia: total vendido e alerta de estoque baixo | Relatórios avançados e gráficos |

> **Revisão (Kaizen).** Em relação a uma primeira ideia mais ampla, que incluía clientes, usuários e nota
> fiscal, o escopo foi reduzido ao núcleo que entrega valor ao usuário: **vender e controlar o estoque**.
> Os itens fora do escopo ficam registrados como evolução futura.

## 1.3 Requisitos funcionais

| ID | Requisito | Prioridade |
|---|---|---|
| RF01 | Cadastrar produto (código de barras, nome, preço, estoque) | Alta |
| RF02 | Editar produto | Alta |
| RF03 | Excluir produto que ainda não foi vendido | Média |
| RF04 | Listar e buscar produtos por nome ou código de barras | Alta |
| RF05 | Adicionar produto à venda pelo código de barras, informando a quantidade | Alta |
| RF06 | Adicionar produto à venda buscando pelo nome | Média |
| RF07 | Remover item da venda em andamento e limpar a venda | Alta |
| RF08 | Escolher a forma de pagamento e, se for dinheiro, calcular o troco | Alta |
| RF09 | Finalizar a venda, gravando-a e baixando o estoque | Alta |
| RF10 | Listar vendas, com filtro por dia, e ver o comprovante de cada venda | Média |
| RF11 | Exibir painel com vendas e faturamento do dia e produtos com estoque baixo | Média |

## 1.4 Requisitos não funcionais

| ID | Requisito |
|---|---|
| RNF01 | Aplicação web acessível por navegador moderno (Chrome, Edge, Firefox), também em telas de celular |
| RNF02 | Back-end em Python (Flask) seguindo o padrão MVC |
| RNF03 | Banco de dados PostgreSQL |
| RNF04 | Valores em dinheiro armazenados em centavos (inteiros), sem erro de arredondamento |
| RNF05 | A venda é gravada de forma atômica: ou tudo é gravado, ou nada |
| RNF06 | Mensagens de erro claras, em português, dizendo o que corrigir |
| RNF07 | Operação de caixa pelo teclado: Enter adiciona o item, F10 finaliza e Esc limpa a venda |
| RNF08 | Código coberto por testes automatizados (pytest no back-end e node:test no front-end) |

## 1.5 Regras de negócio

| ID | Regra |
|---|---|
| RN01 | O código de barras é obrigatório, tem de 8 a 14 dígitos numéricos e não pode se repetir |
| RN02 | O nome do produto tem de 3 a 100 caracteres |
| RN03 | O preço deve ser maior que zero |
| RN04 | O estoque é um número inteiro igual ou maior que zero |
| RN05 | Uma venda deve ter pelo menos um item |
| RN06 | A quantidade de cada item é inteira, maior que zero e não pode passar do estoque disponível |
| RN07 | Formas de pagamento aceitas: Dinheiro, Cartão de débito, Cartão de crédito e Pix |
| RN08 | No pagamento em dinheiro, o valor recebido deve ser maior ou igual ao total; troco = recebido − total |
| RN09 | Ao finalizar a venda, o estoque de cada produto é reduzido pela quantidade vendida |
| RN10 | Um produto que já aparece em alguma venda não pode ser excluído (preserva o histórico) |
| RN11 | Produtos com estoque igual ou menor que 5 aparecem como "estoque baixo" |
| RN12 | O preço da venda é sempre lido do banco, nunca do navegador |
