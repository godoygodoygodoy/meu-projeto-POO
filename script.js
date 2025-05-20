const form = document.getElementById("form-lanche");
const lista = document.getElementById("lista-lanches");

let lanchesGodoy = [];

form.addEventListener("submit", function(event) {
  event.preventDefault();

  const nome = document.getElementById("nome").value;
  const preco = parseFloat(document.getElementById("preco").value);

  const lanche = {
    nome: nome,
    preco: preco
  };

  lanchesGodoy.push(lanche);
  atualizarLista();

  form.reset();
});

function atualizarLista() {
  lista.innerHTML = "";

  lanchesGodoy.forEach((lanche, index) => {
    const item = document.createElement("li");
    item.innerHTML = `
      ${lanche.nome} <span>R$ ${lanche.preco.toFixed(2)}</span>
      <button onclick="removerLanche(${index})">🗑️</button>
    `;
    lista.appendChild(item);
  });
}

function removerLanche(index) {
  lanchesGodoy.splice(index, 1);
  atualizarLista();
}

