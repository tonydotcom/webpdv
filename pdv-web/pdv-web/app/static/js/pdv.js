/*
 * Liga a tela de venda (HTML) à lógica do carrinho (carrinho.js) e ao servidor.
 */
(function () {
  "use strict";

  var C = window.PDVCarrinho;
  var carrinho = new C.Carrinho();
  var enviando = false;

  var $ = function (id) { return document.getElementById(id); };
  var campoCodigo = $("codigo");
  var campoQtd = $("quantidade");
  var campoRecebido = $("valor-recebido");
  var selectPagamento = $("forma-pagamento");
  var botaoFinalizar = $("finalizar");
  var caixaMensagem = $("mensagem");
  var dialogo = $("dialogo-sucesso");

  function mostrarMensagem(texto, tipo) {
    caixaMensagem.textContent = texto;
    caixaMensagem.className = "alerta alerta-" + (tipo || "erro");
    caixaMensagem.hidden = false;
  }

  function esconderMensagem() {
    caixaMensagem.hidden = true;
  }

  function focarCodigo() {
    campoCodigo.value = "";
    campoQtd.value = 1;
    campoCodigo.focus();
  }

  function render() {
    var corpo = $("itens");
    corpo.innerHTML = "";
    if (carrinho.estaVazio()) {
      corpo.innerHTML = '<tr class="linha-vazia"><td colspan="5">Nenhum item. Leia o código de barras para começar.</td></tr>';
    }
    carrinho.itens.forEach(function (item) {
      var tr = document.createElement("tr");
      var celulas = [
        item.produto.nome,
        item.quantidade,
        C.formatarReais(item.produto.preco_centavos),
        C.formatarReais(item.produto.preco_centavos * item.quantidade)
      ];
      celulas.forEach(function (valor, indice) {
        var td = document.createElement("td");
        td.textContent = valor; // textContent evita injeção de HTML
        if (indice > 0) td.className = "num";
        tr.appendChild(td);
      });
      var tdAcao = document.createElement("td");
      var botao = document.createElement("button");
      botao.type = "button";
      botao.className = "link-perigo";
      botao.textContent = "Remover";
      botao.setAttribute("aria-label", "Remover " + item.produto.nome);
      botao.addEventListener("click", function () {
        carrinho.remover(item.produto.id);
        render();
        campoCodigo.focus();
      });
      tdAcao.appendChild(botao);
      tr.appendChild(tdAcao);
      corpo.appendChild(tr);
    });

    $("total").textContent = C.formatarReais(carrinho.totalCentavos());
    var qtd = carrinho.quantidadeItens();
    $("qtd-itens").textContent = qtd + (qtd === 1 ? " item" : " itens");
    atualizarPagamento();
  }

  function atualizarPagamento() {
    var dinheiro = selectPagamento.value === "DINHEIRO";
    $("grupo-recebido").hidden = !dinheiro;
    var pronto = !carrinho.estaVazio();
    if (dinheiro) {
      var troco = carrinho.troco(C.reaisParaCentavos(campoRecebido.value));
      $("troco").textContent = troco === null ? "—" : C.formatarReais(troco);
      pronto = pronto && troco !== null;
    }
    botaoFinalizar.disabled = !pronto || enviando;
  }

  function buscarProduto(codigo) {
    return fetch(window.PDV.urlProduto + "codigo/" + encodeURIComponent(codigo))
      .then(function (resposta) {
        return resposta.json().then(function (dados) {
          if (!resposta.ok) throw new Error(dados.erro || "Produto não encontrado.");
          return dados;
        });
      });
  }

  function adicionar(produto, quantidade) {
    try {
      carrinho.adicionar(produto, quantidade);
      esconderMensagem();
      render();
    } catch (erro) {
      mostrarMensagem(erro.message);
    }
    focarCodigo();
  }

  $("form-item").addEventListener("submit", function (evento) {
    evento.preventDefault();
    var codigo = campoCodigo.value.trim();
    if (!codigo) {
      mostrarMensagem("Digite ou leia um código de barras.");
      return;
    }
    if (!/^\d{8,14}$/.test(codigo)) {
      mostrarMensagem("Código inválido: use de 8 a 14 números.");
      campoCodigo.select();
      return;
    }
    var quantidade = campoQtd.value;
    buscarProduto(codigo)
      .then(function (produto) { adicionar(produto, quantidade); })
      .catch(function (erro) {
        mostrarMensagem(erro.message === "Failed to fetch" ? "Sem conexão com o servidor." : erro.message);
        campoCodigo.select();
      });
  });

  // Busca por nome (para produtos sem código legível)
  var temporizador;
  $("busca-nome").addEventListener("input", function (evento) {
    clearTimeout(temporizador);
    var termo = evento.target.value.trim();
    var lista = $("resultado-busca");
    temporizador = setTimeout(function () {
      if (termo.length < 2) { lista.innerHTML = ""; return; }
      fetch(window.PDV.urlProduto + "busca?q=" + encodeURIComponent(termo))
        .then(function (r) { return r.json(); })
        .then(function (produtos) {
          lista.innerHTML = "";
          if (!produtos.length) {
            var vazio = document.createElement("li");
            vazio.textContent = "Nenhum produto encontrado.";
            lista.appendChild(vazio);
          }
          produtos.forEach(function (p) {
            var li = document.createElement("li");
            var botao = document.createElement("button");
            botao.type = "button";
            botao.textContent = p.nome + " — " + C.formatarReais(p.preco_centavos) + " (estoque " + p.estoque + ")";
            botao.addEventListener("click", function () {
              adicionar(p, campoQtd.value);
              lista.innerHTML = "";
              $("busca-nome").value = "";
            });
            li.appendChild(botao);
            lista.appendChild(li);
          });
        })
        .catch(function () { mostrarMensagem("Sem conexão com o servidor."); });
    }, 250);
  });

  selectPagamento.addEventListener("change", atualizarPagamento);
  campoRecebido.addEventListener("input", atualizarPagamento);

  function finalizar() {
    if (botaoFinalizar.disabled) return;
    enviando = true;
    atualizarPagamento();
    fetch(window.PDV.urlFinalizar, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        itens: carrinho.paraEnvio(),
        forma_pagamento: selectPagamento.value,
        valor_recebido: campoRecebido.value
      })
    })
      .then(function (resposta) {
        return resposta.json().then(function (dados) {
          if (!resposta.ok) throw new Error(dados.erro || "Não foi possível finalizar a venda.");
          return dados;
        });
      })
      .then(function (venda) {
        $("numero-venda").textContent = "#" + venda.id;
        $("sucesso-total").textContent = C.formatarReais(venda.total_centavos);
        $("sucesso-troco").textContent = C.formatarReais(venda.troco_centavos);
        $("sucesso-troco-linha").hidden = selectPagamento.value !== "DINHEIRO";
        $("ver-comprovante").href = venda.url;
        dialogo.showModal();
        $("nova-venda").focus();
      })
      .catch(function (erro) {
        mostrarMensagem(erro.message === "Failed to fetch" ? "Sem conexão com o servidor. A venda não foi gravada." : erro.message);
      })
      .finally(function () {
        enviando = false;
        atualizarPagamento();
      });
  }

  function novaVenda() {
    carrinho.limpar();
    campoRecebido.value = "";
    selectPagamento.value = "DINHEIRO";
    esconderMensagem();
    if (dialogo.open) dialogo.close();
    render();
    focarCodigo();
  }

  botaoFinalizar.addEventListener("click", finalizar);
  $("nova-venda").addEventListener("click", novaVenda);
  $("cancelar").addEventListener("click", function () {
    if (carrinho.estaVazio() || window.confirm("Limpar todos os itens desta venda?")) novaVenda();
  });
  dialogo.addEventListener("close", novaVenda);

  document.addEventListener("keydown", function (evento) {
    if (evento.key === "F10") {
      evento.preventDefault();
      finalizar();
    } else if (evento.key === "Escape" && !dialogo.open) {
      $("cancelar").click();
    }
  });

  render();
})();
