document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    // Pega o botão de submit
    const submitButton = loginForm.querySelector('button[type="submit"]');

    if (loginForm) {
        loginForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const username = usernameInput.value;
            const password = passwordInput.value;

            // Desabilita o botão para evitar cliques duplos e dá feedback
            submitButton.disabled = true;
            submitButton.textContent = 'Verificando...';

            // TODO: Substitua esta lógica de simulação por uma chamada fetch('/api/login')
            // O backend (Flask) deve validar o usuário e retornar o 'role' (admin ou employee)

            // --- LÓGICA DE SIMULAÇÃO (CORRIGIDA E MELHORADA) ---
            if (username === 'Administrador' && password === 'Impacto22') {
                // Login de Admin
                showToast('Login com sucesso! Carregando...', 'success');
                sessionStorage.setItem('userRole', 'admin');
                sessionStorage.setItem('username', username);
                // Adiciona um pequeno atraso para o usuário ver o toast antes de redirecionar
                setTimeout(() => {
                    window.location.href = 'index.html'; // Redireciona para o dashboard principal
                }, 500); // 0.5 segundos
            
            } else if (username === 'funcionario' && password === '123') { 
                // Login de Funcionário (PARA TESTE)
                showToast('Login com sucesso! Carregando...', 'success');
                sessionStorage.setItem('userRole', 'employee');
                sessionStorage.setItem('username', username);
                // Adiciona um pequeno atraso
                setTimeout(() => {
                    window.location.href = 'Funcionario.html'; // Redireciona para o dashboard limitado
                }, 500); // 0.5 segundos
            
            } else {
                // Login Inválido
                showToast('Usuário ou senha inválidos', 'error');
                // Reabilita o botão se o login falhar
                submitButton.disabled = false;
                submitButton.textContent = 'Entrar';
            }
            // --- FIM DA LÓGICA DE SIMULAÇÃO ---
        });
    }
});


// Função de Toast (copiada para o login)
function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;

    container.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 3000);
}
setTimeout(function() {
    const flash = document.getElementById("flash-messages");
    if (flash) {
        flash.style.transition = "opacity 0.5s";
        flash.style.opacity = "0";
        setTimeout(() => flash.remove(), 500); // remove de fato depois do fade
    }
}, 2500);




    // --- Lógica do Modal de Recuperação ---
    if (forgotPasswordLink) {
        forgotPasswordLink.addEventListener('click', (e) => {
            e.preventDefault();
            recoverPasswordModal.classList.remove('hidden');
            setTimeout(() => recoverPasswordModal.classList.add('open'), 10);
        });
    }

    if (closeRecoverBtn) {
        closeRecoverBtn.addEventListener('click', () => {
            closeRecoverModal();
        });
    }

    // Fechar ao clicar fora
    if (recoverPasswordModal) {
        recoverPasswordModal.addEventListener('click', (e) => {
            if (e.target === recoverPasswordModal) closeRecoverModal();
        });
    }

    function closeRecoverModal() {
        recoverPasswordModal.classList.remove('open');
        setTimeout(() => recoverPasswordModal.classList.add('hidden'), 300);
        recoverForm.reset();
    }

    // --- Lógica de Submissão da Recuperação ---
    if (recoverForm) {
        recoverForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const recData = {
                username: document.getElementById('recUsername').value,
                cpf: document.getElementById('recCPF').value,
                city: document.getElementById('recCity').value,
                securityWord: document.getElementById('recSecurityWord').value
            };

            // Botão feedback
            const recBtn = recoverForm.querySelector('button[type="submit"]');
            const originalText = recBtn.textContent;
            recBtn.disabled = true;
            recBtn.textContent = 'Verificando...';

            try {
                // TODO: Substituir por fetch real:
                // const response = await fetch('/api/recover-password', { ...body: JSON.stringify(recData) });
                
                // SIMULAÇÃO DE SUCESSO PARA TESTE
                // Lógica simulada: Se preencher tudo, "recupera".
                // No backend real, você validaria os dados no banco.
                
                await new Promise(r => setTimeout(r, 1500)); // Delay falso

                // Simulação simples:
                if (recData.username === 'Administrador' && recData.securityWord !== 'ImpactoSegura') { 
                    // Exemplo: Admin precisa de palavra certa (simulação)
                    // showToast('Palavra de segurança incorreta para Admin.', 'error'); 
                    // throw new Error('Dados incorretos');
                }

                // Se tudo "der certo":
                showToast('Dados confirmados! Sua senha é: [SenhaSimulada123]', 'success');
                
                // Fecha modal após um tempo para ler a senha no toast? 
                // Ou melhor, mostrar num alert/modal de sucesso. O Toast é rápido.
                alert(`Sucesso! Sua senha é: [SenhaDoUsuario]`); 
                closeRecoverModal();

            } catch (error) {
                showToast('Dados incorretos. Verifique e tente novamente.', 'error');
            } finally {
                recBtn.disabled = false;
                recBtn.textContent = originalText;
            }
        });
    }
});

function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    if (!container) return;
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(() => { toast.remove(); }, 3000);