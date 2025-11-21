// ===========================================
// script.js - Focado em Interação da Interface (Compatível com Flask/Jinja)
// ===========================================

// --- Seletores do DOM ---
let productModal, stockMovementModal, deleteConfirmModal, manageAccountsModal;
let openProductModalBtn, cancelProductModalBtn;
let openEntryModalBtn, openExitModalBtn, cancelMovementModalBtn;
let cancelDeleteBtn, manageAccountsBtn, closeManageAccountsBtn;
let productForm, stockMovementForm, deleteConfirmForm, createAccountForm; 
let movementTypeInput, movementModalTitle, movementSubmitButton;
let prodObjectSelect, prodSizeSelect;
let changePasswordModal;
let closeChangePassBtn, cancelChangePassBtn; // Botões de fechar

// --- Inicialização do App ---
document.addEventListener('DOMContentLoaded', () => {
    
    // 1. Seleciona todos os elementos do DOM
    findAllElements();

    // 2. Configura os listeners de navegação (abas)
    setupNavigation();

    // 3. Configura todos os modais (abrir/fechar)
    setupModalLogic();
    
    // 4. Configura o formulário dinâmico de Objeto/Tamanho
    setupDynamicFormLogic();
    
    // 5. Configura botões de conta (logout, etc.)
    setupButtonListeners();
});

// --- Funções Principais de Configuração ---

function findAllElements() {
    // --- Modais ---
    productModal = document.getElementById('productModal');
    stockMovementModal = document.getElementById('stockMovementModal');
    deleteConfirmModal = document.getElementById('deleteConfirmModal');
    manageAccountsModal = document.getElementById('manageAccountsModal');
    
    // --- Formulários ---
    productForm = document.getElementById('productForm');
    stockMovementForm = document.getElementById('stockMovementForm');
    deleteConfirmForm = document.getElementById('deleteConfirmForm');
    // createAccountForm = document.getElementById('createAccountForm'); // Se for usado para cadastrar novas contas

    // --- Botões ---
    openProductModalBtn = document.getElementById('openProductModalBtn');
    cancelProductModalBtn = document.getElementById('cancelModalBtn'); 
    openEntryModalBtn = document.getElementById('openEntryModalBtn');
    openExitModalBtn = document.getElementById('openExitModalBtn');
    cancelMovementModalBtn = document.getElementById('cancelMovementModalBtn');
    cancelDeleteBtn = document.getElementById('cancelDeleteBtn');
    manageAccountsBtn = document.getElementById('manageAccountsBtn');
    closeManageAccountsBtn = document.getElementById('closeManageAccountsBtn');

    // --- Elementos do Modal de Movimentação ---
    movementTypeInput = document.getElementById('movementTypeInput');
    movementModalTitle = document.getElementById('movementModalTitle');
    movementSubmitButton = stockMovementForm ? stockMovementForm.querySelector('button[type="submit"]') : null;
    
    // --- Selects Dinâmicos (Cadastro Produto) ---
    prodObjectSelect = document.getElementById('prodObject');
    prodSizeSelect = document.getElementById('prodSize');
}

function setupNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    const pages = document.querySelectorAll('.page-content');
    
    if (navLinks && pages) {
        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const targetPageId = link.getAttribute('data-page');
                
                pages.forEach(page => page.classList.add('hidden'));
                const targetPage = document.getElementById(targetPageId);
                if (targetPage) targetPage.classList.remove('hidden');
                
                navLinks.forEach(navLink => navLink.classList.remove('active'));
                link.classList.add('active');
            });
        });
    }
}

function setupModalLogic() {
    // Função helper para fechar modal, limpando o formulário
    const setupCloseModal = (modal, form) => {
        if (modal) modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeModal(modal);
                if (form) form.reset();
            }
        });
    };
    // Selecione o botão de abrir (do seu HTML)
    const changePasswordBtn = document.getElementById('changePasswordBtn');
    
    // Selecione o MODAL de senha (ID do seu HTML)
    const changePasswordModal = document.getElementById('changePasswordModal');    


    // Selecione os botões de fechar do modal
    const closePassX = document.getElementById('closeChangePassBtn');
    const closePassCancel = document.getElementById('cancelChangePassBtn');
    
    // Lógica para ABRIR
    if (changePasswordBtn && changePasswordModal) {
        changePasswordBtn.addEventListener('click', (e) => {
            e.preventDefault(); // Necessário para links/botões que não são submit
            openModal(changePasswordModal); // Usa sua função helper openModal
        });
    }

    // Lógica para FECHAR
    if (changePasswordModal) {
        if (closePassX) closePassX.addEventListener('click', () => closeModal(changePasswordModal));
        if (closePassCancel) closePassCancel.addEventListener('click', () => closeModal(changePasswordModal));
    }

    // --- Modal de Produto ---
    if (openProductModalBtn) openProductModalBtn.addEventListener('click', () => openModal(productModal));
    if (cancelProductModalBtn) cancelProductModalBtn.addEventListener('click', () => {
        closeModal(productModal);
        if (productForm) productForm.reset();
        resetDynamicForm(); // Limpa selects de tamanho
    });
    setupCloseModal(productModal, productForm);
    
    // --- Modal de Movimentação ---
    if (openEntryModalBtn) openEntryModalBtn.addEventListener('click', () => openMovementModal('entrada'));
    if (openExitModalBtn) openExitModalBtn.addEventListener('click', () => openMovementModal('saida'));
    if (cancelMovementModalBtn) cancelMovementModalBtn.addEventListener('click', () => {
        closeModal(stockMovementModal);
        if (stockMovementForm) stockMovementForm.reset();
    });
    setupCloseModal(stockMovementModal, stockMovementForm);

    // --- Modal de Exclusão ---
    if (cancelDeleteBtn) cancelDeleteBtn.addEventListener('click', () => closeModal(deleteConfirmModal));
    setupCloseModal(deleteConfirmModal, deleteConfirmForm);

    // --- Modal de Gerenciar Contas ---
    if (manageAccountsBtn) manageAccountsBtn.addEventListener('click', () => openModal(manageAccountsModal));
    if (closeManageAccountsBtn) closeManageAccountsBtn.addEventListener('click', () => closeModal(manageAccountsModal));
    setupCloseModal(manageAccountsModal, null);
}

/*function setupButtonListeners() {
    // Simplesmente redireciona o formulário de logout via POST
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) logoutBtn.addEventListener('click', (e) => {
        e.preventDefault();
        // Assume que existe um formulário de logout no HTML com id="logoutForm"
        const logoutForm = document.getElementById('logoutForm'); 
        if (logoutForm) logoutForm.submit();
    });
    
    // Outros botões (Trocar Senha, IA, etc.)
    const changePasswordBtn = document.getElementById('changePasswordBtn');
    if(changePasswordBtn) changePasswordBtn.addEventListener('click', () => showToast('Função "Trocar Senha" ainda não implementada.', 'error'));
}
*/
function setupDynamicFormLogic() {
    if (prodObjectSelect) {
        prodObjectSelect.addEventListener('change', atualizarTamanhos);
        // Não chame atualizarTamanhos() aqui, o Jinja deve definir o estado inicial.
    }
}

// --- Funções Helpers ---

// Define os tamanhos (deve refletir a lógica do Flask/Python)
const tamanhosPorObjeto = {
    'Camisa': ['PP', 'P', 'M', 'G', 'GG'],
    'Calça': ['36', '38', '40', '42'],
    'Bermuda': ['36', '38', '40', '42']
};

function atualizarTamanhos() {
    const objetoSelecionado = prodObjectSelect.value;
    const tamanhos = tamanhosPorObjeto[objetoSelecionado] || [];

    prodSizeSelect.innerHTML = '';

    if (tamanhos.length === 0) {
        const option = document.createElement('option');
        option.textContent = 'Selecione um objeto primeiro';
        option.value = '';
        prodSizeSelect.appendChild(option);
        prodSizeSelect.disabled = true;
    } else {
        prodSizeSelect.disabled = false;
        tamanhos.forEach(tamanho => {
            const option = document.createElement('option');
            option.value = tamanho;
            option.textContent = tamanho;
            prodSizeSelect.appendChild(option);
        });
    }
}

function resetDynamicForm() {
    if (prodSizeSelect) {
        prodSizeSelect.innerHTML = '<option value="">Selecione um objeto primeiro</option>';
        prodSizeSelect.disabled = true;
    }
    if (prodObjectSelect) {
        prodObjectSelect.value = ""; 
    }
}


function openModal(modalElement) {
    if (!modalElement) return;
    modalElement.classList.remove('hidden');
    setTimeout(() => modalElement.classList.add('open'), 10); 
}

function closeModal(modalElement) {
    if (!modalElement) return;
    modalElement.classList.remove('open');
    setTimeout(() => modalElement.classList.add('hidden'), 300);
}

function openMovementModal(type) {
    if (!stockMovementModal || !movementTypeInput || !movementModalTitle || !movementSubmitButton) return;
    
    // Configura texto e cores
    if (type === 'entrada') {
        movementModalTitle.textContent = "Registrar Entrada no Estoque";
        movementSubmitButton.className = "bg-green-600 text-white px-5 py-2 rounded-lg shadow-md hover:bg-green-700 transition-colors";
    } else {
        movementModalTitle.textContent = "Registrar Saída do Estoque";
        movementSubmitButton.className = "bg-red-600 text-white px-5 py-2 rounded-lg shadow-md hover:bg-red-700 transition-colors";
    }
    
    // Configura o valor do input hidden para o Flask
    movementTypeInput.value = type;
    
    // Preenche a data/hora atual
    const dateInput = document.getElementById('movementDate');
    if (dateInput) {
        const now = new Date();
        now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
        dateInput.value = now.toISOString().slice(0, 16);
    }
    
    // O Flask já preencheu a lista de produtos no HTML.
    openModal(stockMovementModal);
}

function showToast(message, type) {
    // Função simples de notificação para debug
    console.log(`[TOAST ${type.toUpperCase()}]: ${message}`);
    // Adicione a implementação visual do seu 'toast' aqui.
}

  setTimeout(function() {
      const flash = document.getElementById("flash-messages");
      if (flash) {
          flash.style.display = "none";
      }
  }, 2500); // 5000ms = 5 segundos

document.addEventListener("DOMContentLoaded", function () {
    const input = document.getElementById("productSearchInput");
    const table = document.getElementById("estoqueTable");
    const rows = table.getElementsByTagName("tr");

    input.addEventListener("keyup", function () {
        const filter = input.value.toLowerCase();

        for (let i = 1; i < rows.length; i++) { 
            const rowText = rows[i].innerText.toLowerCase();

            if (rowText.includes(filter)) {
                rows[i].style.display = "";
            } else {
                rows[i].style.display = "none";
            }
        }
    });
});

document.getElementById('stockSearchInput').addEventListener('input', function () {
    const searchText = this.value.toLowerCase();
    const rows = document.querySelectorAll('#estoqueTabela tbody tr');

    rows.forEach(row => {
        const text = row.innerText.toLowerCase();
        row.style.display = text.includes(searchText) ? '' : 'none';
    });
});









//grafico de barra do dashboard

    // === GRÁFICO 1: Entradas vs Saídas ===
document.addEventListener('DOMContentLoaded', () => {
  // Certifica que as variáveis globais vindas do template estão definidas
  const entradas = typeof ENTRADAS !== 'undefined' ? ENTRADAS : [];
  const saidas = typeof SAIDAS !== 'undefined' ? SAIDAS : [];
  const catLabels = typeof CATEGORIAS_LABELS !== 'undefined' ? CATEGORIAS_LABELS : [];
  const catQtd = typeof CATEGORIAS_QTD !== 'undefined' ? CATEGORIAS_QTD : [];

  // --- Gráfico Entradas vs Saídas ---
try {
  const ctx1 = document.getElementById('entradaSaidaChart');
  if (ctx1) {
    // Se entradas for array -> usamos labels mensais (1..n). Se número -> duas barras.
    let cfg;
    if (Array.isArray(entradas) && Array.isArray(saidas)) {
      const n = Math.max(entradas.length, saidas.length);
      const labels = Array.from({length: n}, (_, i) => `Mês ${i+1}`);
      cfg = {
        type: 'bar',
        data: {
          labels,
          datasets: [
            { label: 'Entradas', data: entradas, stack: 'stack1', backgroundColor: 'rgba(134,239,172,0.7)' }, // verde claro
            { label: 'Saídas',   data: saidas,   stack: 'stack1', backgroundColor: 'rgba(252,165,165,0.7)' }  // vermelho claro
          ]
        },
        options: {
          responsive: true,
          plugins: { legend: { position: 'top' } },
          scales: { y: { beginAtZero: true } }
        }
      };
    } else {
      // trata como números simples
      const e = Number(entradas) || 0;
      const s = Number(saidas) || 0;
      cfg = {
        type: 'bar',
        data: {
          labels: ['Entradas', 'Saídas'],
          datasets: [
            { label: 'Quantidade', data: [e, s], backgroundColor: ['rgba(134,239,172,0.7)', 'rgba(252,165,165,0.7)'] }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,   // OBRIGATÓRIO
          plugins: { legend: { display: false } },
          scales: { y: { beginAtZero: true } }
        }
      };
    }
    // destrói instancia antiga se existir (atualizações)
    if (ctx1.chart) ctx1.chart.destroy();
    ctx1.chart = new Chart(ctx1, cfg);
  }
} catch (err) {
  console.error('Erro ao criar entrada/saída chart:', err);
}

  // --- Gráfico Categorias (pizza) ---
  try {
    const ctx2 = document.getElementById('categoriasChart');
    if (ctx2) {
      const labels = Array.isArray(catLabels) ? catLabels : [];
      const data = Array.isArray(catQtd) ? catQtd : [];

      const cfg2 = {
        type: 'pie',
        data: {
          labels,
          datasets: [{
            label: 'Categorias',
            data,
            // sem cores fixas para respeitar seu requisito (Chart.js define cores por padrão)
          }]
        },
            options: {
                responsive: true,
                maintainAspectRatio: false,  // deixa o gráfico usar a altura total do container
                plugins: {
                    legend: {
                        position: 'right',
                        labels: {
                            boxWidth: 15,
                            padding: 15,
                            font: {
                                size: 15
                            }
                        }
                    }
                },
                layout: {
                    padding: 35
                }
            }
      };

      if (ctx2.chart) ctx2.chart.destroy();
      ctx2.chart = new Chart(ctx2, cfg2);
    }
  } catch (err) {
    console.error('Erro ao criar categorias chart:', err);
  }
});


const input = document.getElementById('reportSearchInput');
const table = document.getElementById('reportTable');
const rows = table.getElementsByTagName('tr');

input.addEventListener('keyup', function() {
    const filter = input.value.toLowerCase();

    // Começa de 1 para pular o cabeçalho
    for (let i = 1; i < rows.length; i++) {
        const cells = rows[i].getElementsByTagName('td');
        let found = false;

        for (let j = 0; j < cells.length; j++) {
            if (cells[j].textContent.toLowerCase().includes(filter)) {
                found = true;
                break;
            }
        }

        rows[i].style.display = found ? '' : 'none';
    }
});



//relatorio com ia 
// Função para fechar a caixa de análise
    function closeAiAnalysis() {
        document.getElementById('reportAnalysisContainer').classList.add('hidden');
    }

    document.getElementById('analyzeReportBtn').addEventListener('click', function() {
        const container = document.getElementById('reportAnalysisContainer');
        const loading = document.getElementById('reportAnalysisLoading');
        const result = document.getElementById('reportAnalysisResult');
        
        // Mostra container e loading
        container.classList.remove('hidden');
        loading.classList.remove('hidden');
        result.innerHTML = ''; // Limpa anterior

        // --- AQUI A MUDANÇA: BUSCA DADOS REAIS DO PYTHON ---
        fetch('/api/analise-ia')
            .then(response => response.json())
            .then(data => {
                // Esconde loading
                loading.classList.add('hidden');

                // Verifica se tem produto crítico (se veio null do python, trata aqui)
                const textoCritico = data.critico_produto 
                    ? `Baixo estoque detectado em <strong>${data.critico_produto}</strong> (Restam: ${data.critico_qtd}). Risco de ruptura.` 
                    : "Seu estoque está equilibrado. Nenhum produto em nível crítico.";

                const textoTop = data.top_produto !== "Nenhum dado"
                    ? `O item <strong>${data.top_produto}</strong> é o campeão de vendas com ${data.top_qtd} saídas.`
                    : "Ainda não há dados de vendas suficientes para análise.";

                // Monta o HTML com os DADOS REAIS
            const htmlCritico = data.mensagem_critico;
            const htmlTop = data.mensagem_top; 

            result.innerHTML = `
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div class="bg-green-100 border-l-4 border-green-500 p-4 rounded shadow-sm">
                        <h4 class="font-bold text-green-800 mb-1">🚀 Top 3 Mais Vendidos</h4>
                        <div class="text-green-700 text-sm">${htmlTop}</div>
                    </div>

                    <div class="bg-red-100 border-l-4 border-red-500 p-4 rounded shadow-sm">
                        <h4 class="font-bold text-red-800 mb-1">⚠️ Atenção ao Estoque</h4>
                        <p class="text-red-700 text-sm">${htmlCritico}</p>
                    </div>

                    <div class="bg-blue-100 border-l-4 border-blue-500 p-4 rounded shadow-sm">
                        <h4 class="font-bold text-blue-800 mb-1">💡 Sugestão do Sistema</h4>
                        <p class="text-blue-700 text-sm">${data.sugestao}</p>
                    </div>
                </div>
            `;
        })
            .catch(error => {
                loading.classList.add('hidden');
                result.innerHTML = `<p class="text-red-500">Erro ao analisar dados: ${error}</p>`;
            });
    });

function abrirModalEditar(id, nome, tamanho, categoria, objeto, valorVenda) {
        // Preenche os campos
        document.getElementById('editNome').value = nome;
        document.getElementById('editTamanho').value = tamanho;
        document.getElementById('editCategoria').value = categoria;
        document.getElementById('editObjeto').value = objeto;
        
        // Apenas Valor de Venda
        document.getElementById('editValorVenda').value = parseFloat(valorVenda || 0);

        // Atualiza a rota do formulário
        document.getElementById('formEditar').action = "/estoque/editar/" + id;

        // Mostra o modal
        document.getElementById('modalEditar').classList.remove('hidden');
    }

    function fecharModalEditar() {
        document.getElementById('modalEditar').classList.add('hidden');
    }


    // ===========================================================
// LÓGICA DOS TAMANHOS NO MODAL DE EDIÇÃO
// ===========================================================

// 1. Definição dos tamanhos
const tamanhosEdicao = {
    'Camisa': ['PP', 'P', 'M', 'G', 'GG', 'XG'],
    'Calça': ['36', '38', '40', '42', '44', '46', '48'],
    'Bermuda': ['36', '38', '40', '42', '44', '46', '48'],
};

// 2. Função chamada quando clica no botão "Editar" na tabela
function abrirModalEditar(id, nome, tamanhoAtual, categoria, objeto, valorVenda) {
    // Preenche os campos básicos
    document.getElementById('editNome').value = nome;
    document.getElementById('editCategoria').value = categoria;
    document.getElementById('editValorVenda').value = parseFloat(valorVenda || 0);
    
    // Preenche o Tipo (Objeto)
    const selectObjeto = document.getElementById('editObjeto');
    selectObjeto.value = objeto;

    // GERA A LISTA DE TAMANHOS CORRETA E SELECIONA O ATUAL
    atualizarSelectTamanhosEdicao(objeto, tamanhoAtual);

    // Atualiza a rota do formulário para salvar no ID certo
    document.getElementById('formEditar').action = "/estoque/editar/" + id;

    // Mostra o modal
    document.getElementById('modalEditar').classList.remove('hidden');
}

// 3. Função que desenha as opções dentro do <select>
function atualizarSelectTamanhosEdicao(tipoSelecionado, tamanhoParaSelecionar = null) {
    const selectTamanho = document.getElementById('editTamanho');
    
    // Limpa as opções antigas
    selectTamanho.innerHTML = "";

    // Pega a lista correta (ou usa padrão P/M/G se não achar)
    const lista = tamanhosEdicao[tipoSelecionado] || ['P', 'M', 'G'];

    // Cria cada opção no HTML
    lista.forEach(tam => {
        const option = document.createElement("option");
        option.value = tam;
        option.text = tam;
        
        // Se for o tamanho que o produto já tem, marca como selecionado
        if (tamanhoParaSelecionar && tam === tamanhoParaSelecionar) {
            option.selected = true;
        }
        
        selectTamanho.appendChild(option);
    });
}

// 4. Adiciona o evento: Se mudar o Tipo dentro do modal, muda os tamanhos
const selectObjetoEdit = document.getElementById('editObjeto');
if (selectObjetoEdit) {
    selectObjetoEdit.addEventListener('change', function() {
        // Chama a função sem passar tamanho pré-selecionado (vai pegar o primeiro)
        atualizarSelectTamanhosEdicao(this.value);
    });
}

// 5. Função para fechar
function fecharModalEditar() {
    document.getElementById('modalEditar').classList.add('hidden');
}


// ===========================================================
// VALIDAÇÃO DE SEGURANÇA: ENTRADA > 100 ITENS
// ===========================================================
const formMovimentacao = document.getElementById('stockMovementForm');

if (formMovimentacao) {
    formMovimentacao.addEventListener('submit', function(event) {
        // 1. Pega os valores do formulário
        const tipo = document.getElementById('movementTypeInput').value; // 'entrada' ou 'saida'
        const quantidade = parseFloat(document.getElementById('movementQuantityInput').value);

        // 2. Verifica: É Entrada? É maior que 100?
        if (tipo === 'entrada' && quantidade > 100) {
            
            // 3. Mostra o alerta na tela
            const confirmacao = confirm(
                `⚠️ ATENÇÃO: QUANTIDADE MUITO ALTA!\n\n` +
                `Você está registrando uma ENTRADA de ${quantidade} itens.\n` +
                `Tem certeza que este número está correto?`
            );

            // 4. Se clicar em "Cancelar", bloqueia o envio
            if (!confirmacao) {
                event.preventDefault(); 
            }
            // Se clicar em "OK", deixa passar normal
        }
    });
}

// ===========================================================
// VALIDAÇÃO: QUANTIDADE INICIAL ALTA (NOVO PRODUTO)
// ===========================================================

document.addEventListener('DOMContentLoaded', () => {
    const formCadastro = document.getElementById('productForm');

    if (formCadastro) {
        formCadastro.addEventListener('submit', function(event) {
            // 1. Pega o campo de quantidade inicial
            const inputQtd = document.getElementById('prodQuantity');
            
            // Se por algum motivo o campo não existir, para a execução
            if (!inputQtd) return;

            const quantidade = parseFloat(inputQtd.value);

            // 2. Validação de Segurança: Números Negativos
            if (quantidade < 0) {
                alert("❌ Erro: A quantidade inicial não pode ser negativa.");
                event.preventDefault(); // Impede o envio
                return;
            }

            // 3. Validação de Alerta: Quantidade maior que 100
            if (quantidade > 200) {
                const confirmacao = confirm(
                    `⚠️ ATENÇÃO: ESTOQUE INICIAL ALTO!\n\n` +
                    `Você está cadastrando um produto novo já com ${quantidade} unidades.\n` +
                    `Confirma que esse número está correto?`
                );

                // Se clicar em "Cancelar", bloqueia o envio
                if (!confirmacao) {
                    event.preventDefault();
                    // Foca no campo para a pessoa corrigir
                    inputQtd.focus(); 
                }
            }
        });
    }
});




// --- Lógica do Modal de Contas e Campo de Segurança ---

document.addEventListener('DOMContentLoaded', () => {
    
    // 1. Abrir e Fechar o Modal de Contas
    const manageBtn = document.getElementById('manageAccountsBtn');
    const closeManageBtn = document.getElementById('closeManageAccountsBtn');
    const manageModal = document.getElementById('manageAccountsModal');

    if (manageBtn && manageModal) {
        manageBtn.addEventListener('click', () => {
            manageModal.classList.remove('hidden');
        });
    }

    if (closeManageBtn && manageModal) {
        closeManageBtn.addEventListener('click', () => {
            manageModal.classList.add('hidden');
        });
    }

    // 2. Mostrar/Esconder Palavra de Segurança (Se for Gerente)
    const roleSelect = document.getElementById('newRoleSelect');
    const securityBox = document.getElementById('securityWordBox');
    const securityInput = securityBox ? securityBox.querySelector('input') : null;

    if (roleSelect && securityBox) {
        roleSelect.addEventListener('change', function() {
            if (this.value === 'gerente') {
                securityBox.classList.remove('hidden');
                if(securityInput) securityInput.required = true;
            } else {
                securityBox.classList.add('hidden');
                if(securityInput) securityInput.required = false;
            }
        });
    }
});


// ===========================================================
// VALIDAÇÃO DE SEGURANÇA (> 100) - VERSÃO FINAL
// ===========================================================

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('stockMovementForm');
    
    if (form) {
        console.log("✅ Formulário de movimentação encontrado! Validação ativa.");

        form.addEventListener('submit', function(event) {
            const inputQtd = document.getElementById('movementQuantityInput');
            
            if (inputQtd) {
                const quantidade = parseFloat(inputQtd.value);
                console.log("Tentando enviar quantidade:", quantidade);

                if (quantidade > 100) {
                    const confirmacao = confirm(
                        `⚠️ ALERTA DE QUANTIDADE ALTA!\n\n` +
                        `Você digitou ${quantidade} unidades.\n` +
                        `Tem certeza que esse número está certo?`
                    );

                    if (!confirmacao) {
                        event.preventDefault(); // Cancela o envio
                        console.log("❌ Envio cancelado pelo usuário.");
                        return false;
                    }
                    console.log("✅ Usuário confirmou quantidade alta.");
                }
            }
        });
    } else {
        console.error("❌ ERRO: O JavaScript não encontrou o formulário 'stockMovementForm'.");
    }
});


document.addEventListener("DOMContentLoaded", function() {
    // ... seus outros códigos ...

    // LÓGICA DA PALAVRA DE SEGURANÇA
    const roleSelect = document.getElementById('newRoleSelect');
    const securityBox = document.getElementById('securityWordBox');
    const securityInput = securityBox.querySelector('input[name="security_word"]');

    if(roleSelect && securityBox) {
        roleSelect.addEventListener('change', function() {
            if (this.value === 'gerente') {
                securityBox.classList.remove('hidden');
                securityInput.setAttribute('required', 'required'); // Torna obrigatório
            } else {
                securityBox.classList.add('hidden');
                securityInput.removeAttribute('required'); // Remove obrigatóriedade
                securityInput.value = ''; // Limpa o campo
            }
        });
    }
});