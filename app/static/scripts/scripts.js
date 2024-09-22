function mascaraTelefone(telefone) {
    let valor = telefone.value;
    valor = valor.replace(/\D/g, ''); // Remove tudo que não for dígito
    valor = valor.replace(/^(\d{2})(\d)/g, "($1) $2"); // Coloca os parênteses no DDD
    valor = valor.replace(/(\d)(\d{4})$/, "$1-$2"); // Coloca o hífen entre o 4º e 5º dígito
    telefone.value = valor;
}

function mascaraCPF(cpf) {
    let valor = cpf.value;
    valor = valor.replace(/\D/g, ''); // Remove tudo que não for dígito
    valor = valor.replace(/(\d{3})(\d)/, "$1.$2"); // Coloca o primeiro ponto
    valor = valor.replace(/(\d{3})(\d)/, "$1.$2"); // Coloca o segundo ponto
    valor = valor.replace(/(\d{3})(\d{2})$/, "$1-$2"); // Coloca o hífen
    cpf.value = valor;
}

document.querySelector('form').addEventListener('submit', function(event) {
    const rg = document.getElementById('rg');
    const cpf = document.getElementById('cpf');
    const telefone = document.getElementById('telefone');

    if (rg.value.length < 9) {
        alert('O RG deve ter exatamente 9 caracteres');
        event.preventDefault(); // Impede o envio do formulário
    }

    if (cpf.value.length < 14) {
        alert('O CPF deve ter pelo menos 14 caracteres');
        event.preventDefault(); // Impede o envio do formulário
    }

    if (telefone.value.length < 15) {
        alert('O telefone deve ter pelo menos 15 caracteres');
        event.preventDefault(); // Impede o envio do formulário
    }
});
