/*
 * Lógica do carrinho da tela de venda, sem nenhuma dependência da página.
 * Por não mexer no HTML, pode ser testada com `node --test tests/js/carrinho.test.js`.
 * Valores sempre em centavos (inteiros).
 */
(function (global) {
  "use strict";

  function formatarReais(centavos) {
    var sinal = centavos < 0 ? "-" : "";
    var abs = Math.abs(Math.round(centavos));
    var reais = Math.floor(abs / 100).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
    var cents = String(abs % 100).padStart(2, "0");
    return sinal + "R$ " + reais + "," + cents;
  }

  /** "12,50" -> 1250. Devolve null se o texto não for um valor válido. */
  function reaisParaCentavos(texto) {
    if (texto === null || texto === undefined) return null;
    var limpo = String(texto).replace(/R\$|\s/g, "");
    if (limpo.indexOf(",") >= 0) limpo = limpo.replace(/\./g, "");
    if (!/^\d+([.,]\d{1,2})?$/.test(limpo)) return null;
    var partes = limpo.replace(",", ".").split(".");
    var decimais = (partes[1] || "").padEnd(2, "0");
    return parseInt(partes[0], 10) * 100 + parseInt(decimais, 10);
  }

  function Carrinho() {
    this.itens = []; // { produto: {id, nome, preco_centavos, estoque, codigo_barras}, quantidade }
  }

  /**
   * Adiciona um produto. Se já estiver no carrinho, soma a quantidade.
   * Lança Error com mensagem amigável se a quantidade for inválida ou passar do estoque.
   */
  Carrinho.prototype.adicionar = function (produto, quantidade) {
    quantidade = Number(quantidade);
    if (!Number.isInteger(quantidade) || quantidade < 1) {
      throw new Error("A quantidade deve ser um número inteiro maior que zero.");
    }
    var existente = this.itens.find(function (i) { return i.produto.id === produto.id; });
    var novaQuantidade = (existente ? existente.quantidade : 0) + quantidade;
    if (novaQuantidade > produto.estoque) {
      throw new Error('Estoque insuficiente para "' + produto.nome + '". Disponível: ' + produto.estoque + ".");
    }
    if (existente) {
      existente.quantidade = novaQuantidade;
    } else {
      this.itens.push({ produto: produto, quantidade: quantidade });
    }
  };

  Carrinho.prototype.remover = function (produtoId) {
    this.itens = this.itens.filter(function (i) { return i.produto.id !== produtoId; });
  };

  Carrinho.prototype.limpar = function () {
    this.itens = [];
  };

  Carrinho.prototype.estaVazio = function () {
    return this.itens.length === 0;
  };

  Carrinho.prototype.totalCentavos = function () {
    return this.itens.reduce(function (soma, i) { return soma + i.produto.preco_centavos * i.quantidade; }, 0);
  };

  Carrinho.prototype.quantidadeItens = function () {
    return this.itens.reduce(function (soma, i) { return soma + i.quantidade; }, 0);
  };

  /** Troco em centavos, ou null se o valor recebido for inválido ou menor que o total. */
  Carrinho.prototype.troco = function (valorRecebidoCentavos) {
    if (valorRecebidoCentavos === null || valorRecebidoCentavos < this.totalCentavos()) return null;
    return valorRecebidoCentavos - this.totalCentavos();
  };

  /** Formato enviado ao servidor. Só vão o id e a quantidade: o preço vem do banco. */
  Carrinho.prototype.paraEnvio = function () {
    return this.itens.map(function (i) { return { produto_id: i.produto.id, quantidade: i.quantidade }; });
  };

  var api = { Carrinho: Carrinho, formatarReais: formatarReais, reaisParaCentavos: reaisParaCentavos };
  if (typeof module !== "undefined" && module.exports) {
    module.exports = api;
  } else {
    global.PDVCarrinho = api;
  }
})(this);
