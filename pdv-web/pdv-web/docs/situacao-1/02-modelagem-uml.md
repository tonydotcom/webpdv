# 2. Modelagem UML

Os diagramas estão em [Mermaid](https://mermaid.js.org/), que o GitHub desenha automaticamente ao abrir
este arquivo.

## 2.1 Diagrama de casos de uso

Ator: **Operador de caixa**, que também é quem cadastra os produtos.

```mermaid
flowchart LR
    operador(("👤<br/>Operador<br/>de caixa"))

    subgraph sistema [PDV Web]
        UC01([UC01 Manter produtos])
        UC02([UC02 Buscar produto])
        UC03([UC03 Registrar venda])
        UC04([UC04 Calcular troco])
        UC05([UC05 Consultar vendas])
        UC06([UC06 Ver painel do dia])
    end

    operador --- UC01
    operador --- UC03
    operador --- UC05
    operador --- UC06
    UC03 -. "«include»" .-> UC02
    UC04 -. "«extend» pagamento em dinheiro" .-> UC03
    UC01 -. "«include»" .-> UC02
```

### Especificação do caso de uso principal: UC03 Registrar venda

| Item | Descrição |
|---|---|
| **Ator** | Operador de caixa |
| **Pré-condição** | Existem produtos cadastrados com estoque |
| **Pós-condição** | A venda e seus itens estão gravados e o estoque foi reduzido |
| **Fluxo principal** | 1. O operador abre "Nova venda". 2. O sistema posiciona o cursor no campo de código de barras. 3. O operador lê ou digita o código, informa a quantidade e tecla Enter. 4. O sistema busca o produto e o adiciona à lista, atualizando o total. 5. Os passos 3 e 4 se repetem até o fim da compra. 6. O operador escolhe a forma de pagamento. 7. O operador finaliza com o botão ou com F10. 8. O sistema grava a venda, baixa o estoque e mostra o número da venda e o troco. |
| **Fluxo alternativo A1**: produto sem código | No passo 3, o operador abre "Buscar pelo nome", digita parte do nome e clica no produto. |
| **Fluxo alternativo A2**: pagamento em dinheiro | No passo 6, o operador informa o valor recebido e o sistema mostra o troco (UC04). |
| **Fluxo alternativo A3**: remover item | A qualquer momento, o operador clica em "Remover" num item ou em "Limpar venda" (Esc). |
| **Exceção E1** | Código inexistente: o sistema mostra "Nenhum produto com o código X". |
| **Exceção E2** | Quantidade maior que o estoque: o sistema mostra "Estoque insuficiente… Disponível: N" e não adiciona o item. |
| **Exceção E3** | Valor recebido menor que o total: o botão Finalizar fica desabilitado e o troco aparece como "—". |
| **Exceção E4** | Falha de conexão: o sistema mostra "Sem conexão com o servidor. A venda não foi gravada." |

## 2.2 Diagrama de classes

```mermaid
classDiagram
    direction LR

    class Produto {
        +int id
        +str codigo_barras
        +str nome
        +int preco_centavos
        +int estoque
        +datetime criado_em
        +a_partir_do_formulario(dados, produto_id) Produto$
        +listar(busca) list~Produto~$
        +listar_estoque_baixo() list~Produto~$
        +buscar_por_id(id) Produto$
        +buscar_por_codigo(codigo) Produto$
        +salvar() Produto
        +excluir(id) Produto$
        +estoque_baixo() bool
    }

    class Venda {
        +int id
        +datetime data_hora
        +int total_centavos
        +str forma_pagamento
        +int valor_recebido_centavos
        +int troco_centavos
        +list~ItemVenda~ itens
        +registrar(itens, forma_pagamento, valor_recebido) Venda$
        +listar(data) list~Venda~$
        +buscar_por_id(id) Venda$
        +resumo_do_dia(data) dict$
    }

    class ItemVenda {
        +int produto_id
        +int quantidade
        +int preco_unitario_centavos
        +subtotal_centavos() int
    }

    class FormaPagamento {
        <<enumeration>>
        DINHEIRO
        DEBITO
        CREDITO
        PIX
    }

    Venda "1" *-- "1..*" ItemVenda : contém
    ItemVenda "0..*" --> "1" Produto : refere-se a
    Venda ..> FormaPagamento : usa
```

> O `preco_unitario_centavos` fica gravado no item para que o histórico não mude quando o preço do produto
> for alterado depois.

## 2.3 Diagrama de sequência: finalizar venda

```mermaid
sequenceDiagram
    actor Operador
    participant Tela as View (nova.html + pdv.js)
    participant Ctrl as VendaController
    participant Venda as Model Venda
    participant BD as PostgreSQL

    Operador->>Tela: F10 / clica em Finalizar
    Tela->>Ctrl: POST /vendas/ {itens, forma_pagamento, valor_recebido}
    Ctrl->>Venda: registrar(itens, forma, recebido)
    Venda->>Venda: valida itens e forma de pagamento
    Venda->>BD: BEGIN
    loop para cada item
        Venda->>BD: SELECT produto (preço e estoque)
    end
    alt estoque insuficiente ou valor recebido menor que o total
        Venda->>BD: ROLLBACK
        Venda-->>Ctrl: ErroValidacao
        Ctrl-->>Tela: 400 {erro}
        Tela-->>Operador: mostra a mensagem de erro
    else tudo certo
        Venda->>BD: INSERT venda
        loop para cada item
            Venda->>BD: INSERT item_venda
            Venda->>BD: UPDATE produto SET estoque = estoque - qtd
        end
        Venda->>BD: COMMIT
        Venda-->>Ctrl: venda
        Ctrl-->>Tela: 201 {id, total, troco}
        Tela-->>Operador: "Venda #N finalizada! Troco: R$ X"
    end
```

## 2.4 Diagrama de atividades: registrar venda

```mermaid
flowchart TD
    inicio((●)) --> abrir[Abrir Nova venda]
    abrir --> ler[Ler ou digitar o código e a quantidade]
    ler --> existe{Produto existe?}
    existe -- Não --> erro1[Mostrar: produto não encontrado] --> ler
    existe -- Sim --> estoque{Quantidade ≤ estoque?}
    estoque -- Não --> erro2[Mostrar: estoque insuficiente] --> ler
    estoque -- Sim --> add[Adicionar à lista e atualizar o total]
    add --> mais{Mais produtos?}
    mais -- Sim --> ler
    mais -- Não --> forma[Escolher a forma de pagamento]
    forma --> dinheiro{É dinheiro?}
    dinheiro -- Sim --> recebido[Informar o valor recebido]
    recebido --> suficiente{Recebido ≥ total?}
    suficiente -- Não --> recebido
    suficiente -- Sim --> finalizar
    dinheiro -- Não --> finalizar[Finalizar venda]
    finalizar --> gravar[Gravar venda e baixar estoque]
    gravar --> comprovante[Mostrar número e troco]
    comprovante --> fim((◉))
```

## 2.5 Diagrama de estados: venda na tela de caixa

```mermaid
stateDiagram-v2
    [*] --> Vazia
    Vazia --> EmAndamento: adiciona item
    EmAndamento --> EmAndamento: adiciona ou remove item
    EmAndamento --> Vazia: remove último item / limpar (Esc)
    EmAndamento --> Enviando: finalizar (F10)
    Enviando --> EmAndamento: erro (mensagem na tela)
    Enviando --> Finalizada: gravada com sucesso
    Finalizada --> Vazia: nova venda
```
