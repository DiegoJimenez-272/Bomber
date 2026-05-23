document.addEventListener('DOMContentLoaded', function() {
    const body = document.body;

    // Manejo seguro de localStorage para evitar errores de estado global
    let currentTheme = 'light';
    try {
        currentTheme = localStorage.getItem('theme') || 'light';
    } catch (e) {
        console.warn("No se pudo acceder al almacenamiento local.");
    }

    // Forzamos el estado global inicialmente
    if (currentTheme === 'dark') {
        body.classList.add('dark-mode');
    } else {
        body.classList.remove('dark-mode');
    }
    updateButtons(currentTheme);

    // Usamos Delegación de Eventos: escuchamos los clics en todo el documento.
    // Esto evita que el botón deje de funcionar tras cambiar su ícono interno (innerHTML)
    document.addEventListener('click', function(e) {
        const toggleBtn = e.target.closest('.theme-toggle-btn');
        
        if (toggleBtn) {
            e.preventDefault(); // Detenemos propagaciones y comportamientos del navegador default
            body.classList.toggle('dark-mode');
            currentTheme = body.classList.contains('dark-mode') ? 'dark' : 'light';
            try {
                localStorage.setItem('theme', currentTheme);
            } catch (e) {}
            updateButtons(currentTheme);
        }
    });

    function updateButtons(theme) {
        const themeToggleButtons = document.querySelectorAll('.theme-toggle-btn');
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