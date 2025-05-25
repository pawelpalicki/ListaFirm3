$(document).ready(function() {
    // Inicjalizacja Select2 jest teraz obsługiwana przez select2_config.js

    // Obsługa nawigacji mobilnej
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
            if (e.target.classList.contains('nav-link')) {
                if (navbar.classList.contains('mobile-menu-open')) { // Zamknij tylko jeśli jest otwarte
                    navbar.classList.remove('mobile-menu-open');
                     // Upewnij się, że stan przycisku togglera jest zresetowany, jeśli Bootstrap tego nie robi
                    if (navbarToggler.getAttribute('aria-expanded') === 'true') {
                        navbarToggler.click();
                    }
                }
            }
        });
    }

    // Obsługa filtra mobilnego
    const filterToggleBtn = document.querySelector('#mobile-filter-toggle');
    const mobileFilterOverlay = document.querySelector('#mobile-filter-overlay');
    const closeMobileFilterBtn = document.querySelector('#close-mobile-filter');
    if (filterToggleBtn) {
        filterToggleBtn.addEventListener('click', () => {
            toggleMobileFilter(true);
        });
    }
    if (mobileFilterOverlay && closeMobileFilterBtn) {
        closeMobileFilterBtn.addEventListener('click', () => {
            toggleMobileFilter(false);
        });
        mobileFilterOverlay.addEventListener('click', (e) => {
            if (e.target === mobileFilterOverlay) {
                toggleMobileFilter(false);
            }
        });
    }

    // Funkcja aktualizacji powiatów
    function updatePowiaty(wojewodztwoId, isMobile) {
        const powiatSelect = isMobile ? $('#powiat-mobile') : $('#powiat');

        if (wojewodztwoId) {
            $.getJSON(`/api/powiaty/${wojewodztwoId}`, function(data) {
                const currentPowiat = powiatSelect.val();
                powiatSelect.empty();
                powiatSelect.append('<option value="">Wybierz powiat</option>');
                $.each(data, function(i, item) {
                    powiatSelect.append($('<option>').attr('value', item.id).text(item.name));
                });
                if (currentPowiat) powiatSelect.val(currentPowiat);
                powiatSelect.trigger('change'); // Odśwież Select2
            });
        } else {
            powiatSelect.empty().append('<option value="">Wybierz najpierw województwo</option>');
            powiatSelect.trigger('change'); // Odśwież Select2
        }
    }

    $('#wojewodztwo, #wojewodztwo-mobile').change(function() {
        updatePowiaty($(this).val(), $(this).attr('id').includes('mobile'));
    });

    const initPowiaty = (selector, isMobile) => {
        const wojSelect = $(selector);
        if (wojSelect.length > 0 && wojSelect.val()) { // Sprawdź czy element istnieje
            updatePowiaty(wojSelect.val(), isMobile);
        }
    };

    initPowiaty('#wojewodztwo', false);
    initPowiaty('#wojewodztwo-mobile', true);

    // Przełącznik motywu
    const themeToggle = $('#theme-toggle');
    const moonIcon = $('#theme-toggle-icon-moon');
    const sunIcon = $('#theme-toggle-icon-sun');
    const docElement = $(document.documentElement); // Celujemy w <html>

    function applyTheme(theme) {
        if (theme === 'dark') {
            docElement.attr('data-theme', 'dark');
            if(moonIcon.length) moonIcon.hide(); // Sprawdź czy element istnieje
            if(sunIcon.length) sunIcon.show();   // Sprawdź czy element istnieje
            localStorage.setItem('theme', 'dark');
        } else {
            docElement.attr('data-theme', 'light');
            if(sunIcon.length) sunIcon.hide();   // Sprawdź czy element istnieje
            if(moonIcon.length) moonIcon.show(); // Sprawdź czy element istnieje
            localStorage.setItem('theme', 'light');
        }
    }

    // Ustawienie ikony przy ładowaniu strony (skrypt w <head> już ustawił atrybut data-theme)
    const currentTheme = docElement.attr('data-theme'); // Odczytaj z <html>
    if (currentTheme === 'dark') {
        if(moonIcon.length) moonIcon.hide();
        if(sunIcon.length) sunIcon.show();
    } else {
        if(sunIcon.length) sunIcon.hide();
        if(moonIcon.length) moonIcon.show();
    }

    if (themeToggle.length) { // Sprawdź czy przycisk istnieje
        themeToggle.on('click', function() {
            const newTheme = docElement.attr('data-theme') === 'dark' ? 'light' : 'dark';
            applyTheme(newTheme);
        });
    }


    // Obsługa kliknięcia wiersza firmy, aby pokazać szczegóły
    $('.company-row').click(function() {
        const companyId = $(this).data('company-id');
        const detailsRow = $(`#details-${companyId}`);

        if (detailsRow.hasClass('d-none')) {
            detailsRow.removeClass('d-none');
            // Załaduj szczegóły przez AJAX z parametrem 'ajax=true'
            $.get(`/company/${companyId}?ajax=true`, function(data) {
                const parser = new DOMParser();
                const htmlDoc = parser.parseFromString(data, 'text/html');
                const content = htmlDoc.querySelector('.company-details-content');
                if (content) {
                    detailsRow.find('td').html(content.innerHTML);
                } else {
                     console.error("Nie znaleziono elementu .company-details-content w odpowiedzi AJAX.");
                    detailsRow.find('td').html('<p class="text-danger">Błąd ładowania szczegółów. Nie znaleziono treści.</p>');
                }
            }).fail(function(jqXHR, textStatus, errorThrown) {
                console.error("Błąd AJAX podczas ładowania szczegółów firmy:", textStatus, errorThrown);
                detailsRow.find('td').html('<p class="text-danger">Błąd ładowania szczegółów. Problem z serwerem lub siecią.</p>');
            });
        } else {
            detailsRow.addClass('d-none');
        }
    });
});

// Funkcja do obsługi filtra mobilnego
function toggleMobileFilter(show) {
    const overlay = document.getElementById('mobile-filter-overlay');
    if (!overlay) return;

    if (show) {
        overlay.style.display = 'block';
        document.body.style.overflow = 'hidden'; // Zapobiega scrollowaniu tła
        const navbar = document.querySelector('.navbar.fixed-top'); // Upewnij się, że celujesz w odpowiedni navbar
        if (navbar) {
            // Można tymczasowo obniżyć z-index paska nawigacji, jeśli filtr ma być nad nim
            // lub zwiększyć z-index filtra, jeśli ma być pod.
            // Dla filtra NAD paskiem nawigacji:
            // navbar.style.zIndex = '1020'; // Bootstrap używa ~1030 dla fixed-top navbar
            // Z-index overlay jest ustawiony na 2000 w CSS, więc powinien być na wierzchu.
        }
    } else {
        overlay.style.display = 'none';
        document.body.style.overflow = ''; // Przywraca scrollowanie
        const navbar = document.querySelector('.navbar.fixed-top');
        if (navbar) {
            // navbar.style.zIndex = ''; // Przywraca domyślny z-index
        }
    }
}
