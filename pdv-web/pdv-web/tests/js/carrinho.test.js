// Testes do front-end (lógica do carrinho). Executar: node --test tests/js/carrinho.test.js
const test = require("node:test");
const assert = require("node:assert/strict");
const { Carrinho, formatarReais, reaisParaCentavos } = require("../../app/static/js/carrinho.js");

const leite = { id: 1, nome: "Leite", preco_centavos: 549, estoque: 10 };
const arroz = { id: 2, nome: "Arroz", preco_centavos: 2899, estoque: 2 };

test("formatarReais", () => {
  assert.equal(formatarReais(0), "R$ 0,00");
  assert.equal(formatarReais(5), "R$ 0,05");
  assert.equal(formatarReais(123456), "R$ 1.234,56");
  assert.equal(formatarReais(-150), "-R$ 1,50");
});

test("reaisParaCentavos", () => {
  assert.equal(reaisParaCentavos("12,50"), 1250);
  assert.equal(reaisParaCentavos("12.5"), 1250);
  assert.equal(reaisParaCentavos("1.234,56"), 123456);
  assert.equal(reaisParaCentavos("20"), 2000);
  assert.equal(reaisParaCentavos("abc"), null);
  assert.equal(reaisParaCentavos(""), null);
  assert.equal(reaisParaCentavos(null), null);
});

test("adiciona itens e calcula o total", () => {
  const c = new Carrinho();
  c.adicionar(leite, 2);
  c.adicionar(arroz, 1);
  assert.equal(c.totalCentavos(), 2 * 549 + 2899);
  assert.equal(c.quantidadeItens(), 3);
});

test("somar o mesmo produto não duplica a linha", () => {
  const c = new Carrinho();
  c.adicionar(leite, 1);
  c.adicionar(leite, "3");
  assert.equal(c.itens.length, 1);
  assert.equal(c.itens[0].quantidade, 4);
});

test("não deixa passar do estoque", () => {
  const c = new Carrinho();
  c.adicionar(arroz, 2);
  assert.throws(() => c.adicionar(arroz, 1), /Estoque insuficiente/);
  assert.equal(c.itens[0].quantidade, 2);
});

test("rejeita quantidade inválida", () => {
  const c = new Carrinho();
  for (const qtd of [0, -1, 1.5, "abc"]) {
    assert.throws(() => c.adicionar(leite, qtd), /quantidade/);
  }
  assert.ok(c.estaVazio());
});

test("remove e limpa", () => {
  const c = new Carrinho();
  c.adicionar(leite, 1);
  c.adicionar(arroz, 1);
  c.remover(1);
  assert.deepEqual(c.itens.map((i) => i.produto.id), [2]);
  c.limpar();
  assert.ok(c.estaVazio());
  assert.equal(c.totalCentavos(), 0);
});

test("calcula troco", () => {
  const c = new Carrinho();
  c.adicionar(leite, 2); // 10,98
  assert.equal(c.troco(2000), 902);
  assert.equal(c.troco(1098), 0);
  assert.equal(c.troco(1000), null);
  assert.equal(c.troco(null), null);
});

test("envia só id e quantidade (o preço vem do servidor)", () => {
  const c = new Carrinho();
  c.adicionar(leite, 2);
  assert.deepEqual(c.paraEnvio(), [{ produto_id: 1, quantidade: 2 }]);
});
