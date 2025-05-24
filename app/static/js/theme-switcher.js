// ===== THEME SWITCHER LOGIC =====
document.addEventListener('DOMContentLoaded', function () {
    const themeToggleButton = document.getElementById('theme-toggle-button');
    const themeToggleIcon = document.getElementById('theme-toggle-icon');
    const body = document.body;
    const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)');

    const lightIconClass = 'bi-brightness-high-fill'; // Icon for light mode
    const darkIconClass = 'bi-moon-stars-fill';    // Icon for dark mode

    function applyTheme(theme) {
        if (theme === 'dark') {
            body.classList.add('dark-mode');
            if (themeToggleIcon) {
                themeToggleIcon.classList.remove(lightIconClass);
                themeToggleIcon.classList.add(darkIconClass);
            }
        } else {
            body.classList.remove('dark-mode');
            if (themeToggleIcon) {
                themeToggleIcon.classList.remove(darkIconClass);
                themeToggleIcon.classList.add(lightIconClass);
            }
        }
    }

    function setTheme(theme) {
        localStorage.setItem('theme', theme);
        applyTheme(theme);
    }

    let currentTheme = localStorage.getItem('theme');
    if (!currentTheme) {
        currentTheme = prefersDarkScheme.matches ? 'dark' : 'light';
    }
    applyTheme(currentTheme); // Apply theme on initial load

    if (themeToggleButton) {
        themeToggleButton.addEventListener('click', function () {
            let newTheme = body.classList.contains('dark-mode') ? 'light' : 'dark';
            setTheme(newTheme);
        });
    }

    if (!localStorage.getItem('theme')) { // Only if no explicit user choice
        prefersDarkScheme.addEventListener('change', function (e) {
            if (!localStorage.getItem('theme')) { 
                applyTheme(e.matches ? 'dark' : 'light');
            }
        });
    }
});
// ===== END THEME SWITCHER LOGIC =====
