// fade ao carregar
window.onload = () => {
    document.body.style.opacity = 0;
    setTimeout(() => {
        document.body.style.opacity = 1;
    }, 100);
};

// confirmação resolver
function confirmarResolucao() {
    return confirm("Tem certeza que deseja marcar como resolvido?");
}

// CPF só número
document.addEventListener("DOMContentLoaded", () => {
    const cpfInput = document.querySelector("input[name='cpf']");

    if (cpfInput) {
        cpfInput.addEventListener("input", () => {
            cpfInput.value = cpfInput.value.replace(/\D/g, "");
        });
    }
});