document.addEventListener('DOMContentLoaded', function() {
    // Seleccionamos todos los botones con la clase indicada o el ID
    const themeToggleButtons = document.querySelectorAll('#theme-toggle, .theme-toggle-btn');
    const body = document.body;

    // Cargar la preferencia de tema desde localStorage
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        body.classList.add('dark-mode');
        updateButtons('dark');
    } else {
        updateButtons('light');
    }

    themeToggleButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            body.classList.toggle('dark-mode');
            const currentTheme = body.classList.contains('dark-mode') ? 'dark' : 'light';
            localStorage.setItem('theme', currentTheme);
            updateButtons(currentTheme);
        });
    });

    function updateButtons(theme) {
        themeToggleButtons.forEach(btn => {
            if (btn.classList.contains('nav-link')) {
                // Botón del sidebar (con texto)
                btn.innerHTML = theme === 'dark' ? '<i class="bi bi-sun-fill me-2"></i><span>Modo Claro</span>' : '<i class="bi bi-moon-fill me-2"></i><span>Modo Oscuro</span>';
            } else {
                // Botón del header (solo ícono, sin texto)
                btn.innerHTML = theme === 'dark' ? '<i class="bi bi-sun-fill" id="theme-icon"></i>' : '<i class="bi bi-moon-fill" id="theme-icon"></i>';
            }
        });
    }
});