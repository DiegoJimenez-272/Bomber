document.addEventListener('DOMContentLoaded', function() {
    const themeToggleButton = document.getElementById('theme-toggle');
    const body = document.body;

    // Cargar la preferencia de tema desde localStorage
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        body.classList.add('dark-mode');
        if (themeToggleButton) {
            themeToggleButton.innerHTML = '<i class="bi bi-sun-fill me-2"></i>Modo Claro';
        }
    } else {
        if (themeToggleButton) {
            themeToggleButton.innerHTML = '<i class="bi bi-moon-fill me-2"></i>Modo Oscuro';
        }
    }

    if (themeToggleButton) {
        themeToggleButton.addEventListener('click', function() {
            body.classList.toggle('dark-mode');
            const currentTheme = body.classList.contains('dark-mode') ? 'dark' : 'light';
            localStorage.setItem('theme', currentTheme);
            this.innerHTML = currentTheme === 'dark' ? '<i class="bi bi-sun-fill me-2"></i>Modo Claro' : '<i class="bi bi-moon-fill me-2"></i>Modo Oscuro';
        });
    }
});