document.addEventListener('DOMContentLoaded', () => {
    const navLinks = document.querySelectorAll('.nav-link');
    const pages = document.querySelectorAll('.page-content');

    // Função para mostrar a página
    function showPage(pageId) {
        // Esconde todas as páginas
        pages.forEach(page => {
            page.classList.add('hidden');
        });

        // Mostra a página alvo
        const targetPage = document.getElementById(pageId);
        if (targetPage) {
            targetPage.classList.remove('hidden');
        }

        // Atualiza o link ativo
        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('data-page') === pageId) {
                link.classList.add('active');
            }
        });
    }

    // Adiciona o evento de clique para cada link da navegação
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault(); // Impede o comportamento padrão do link
            const targetPageId = link.getAttribute('data-page');
            showPage(targetPageId);
        });
    });

    // Mostra a primeira página (Dashboard) por padrão ao carregar
    showPage('page-1');
});
