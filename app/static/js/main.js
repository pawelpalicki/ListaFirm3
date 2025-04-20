document.addEventListener('DOMContentLoaded', function() {
    const normalizeText = (text) => {
        return text
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '')
            .toLowerCase();
    };

    const choicesDesktop = new Choices('#specialties', {
        removeItemButton: true,
        fuseOptions: {
            includeScore: true,
            shouldSort: true,
            keys: [{
                name: 'label',
                weight: 1
            }],
            threshold: 0.6
        },
        searchPlaceholderValue: 'Szukaj specjalności...',
    });

    const choicesMobile = new Choices('#specialties-mobile', {
        removeItemButton: true,
        fuseOptions: {
            includeScore: true,
            shouldSort: true,
            keys: [{
                name: 'label',
                weight: 1
            }],
            threshold: 0.6
        },
        searchPlaceholderValue: 'Szukaj specjalności...',
        // Możesz dodać inne opcje specyficzne dla mobile, jeśli potrzebujesz
    });

    // Obsługa nawigacji mobilnej (bez zmian)
    const navbar = document.querySelector('.navbar');
    const navbarToggler = document.querySelector('.navbar-toggler');
    if (navbarToggler) {
        navbarToggler.addEventListener('click', function() {
            navbar.classList.toggle('mobile-menu-open');
        });
    }
    const navbarCollapse = document.querySelector('.navbar-collapse');
    if (navbarCollapse) {
        navbarCollapse.addEventListener('click', function(e) {
            if(e.target.classList.contains('nav-link')) {
                navbar.classList.remove('mobile-menu-open');
            }
        });
    }

    // Obsługa filtra mobilnego (bez zmian)
    const filterToggleBtn = document.querySelector('.filter-toggle-btn');
    if (filterToggleBtn) {
        filterToggleBtn.addEventListener('click', () => {
            toggleMobileFilter(true);
        });
    }
    const mobileFilterOverlay = document.querySelector('#mobile-filter-overlay');
    if (mobileFilterOverlay) {
        mobileFilterOverlay.addEventListener('click', (e) => {
            if(e.target === mobileFilterOverlay) {
                toggleMobileFilter(false);
            }
        });
    }
});

// Funkcja do obsługi filtra mobilnego (bez zmian)
function toggleMobileFilter(show) {
    const overlay = document.getElementById('mobile-filter-overlay');
    if (!overlay) return;

    if(show) {
        overlay.style.display = 'block';
        document.body.style.overflow = 'hidden';
        const navbar = document.querySelector('.navbar');
        if (navbar) navbar.style.zIndex = '1500';
    } else {
        overlay.style.display = 'none';
        document.body.style.overflow = '';
        const navbar = document.querySelector('.navbar');
        if (navbar) navbar.style.zIndex = '';
    }
}
