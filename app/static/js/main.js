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
                navbar.classList.remove('mobile-menu-open');
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

                // Odśwież Select2 po aktualizacji opcji
                powiatSelect.trigger('change');
            });
        } else {
            powiatSelect.empty().append('<option value="">Wybierz najpierw województwo</option>');
            powiatSelect.trigger('change');
        }
    }

    // Obsługa zmian województwa
    $('#wojewodztwo, #wojewodztwo-mobile').change(function() {
        updatePowiaty($(this).val(), $(this).attr('id').includes('mobile'));
    });

    // Inicjalizacja powiatów
    const initPowiaty = (selector, isMobile) => {
        const wojSelect = $(selector);
        if (wojSelect.val()) {
            updatePowiaty(wojSelect.val(), isMobile);
        }
    };

    initPowiaty('#wojewodztwo', false);
    initPowiaty('#wojewodztwo-mobile', true);

    // Handle company row click to show details
    $('.company-row').click(function() {
        const companyId = $(this).data('company-id');
        const detailsRow = $(`#details-${companyId}`);

        if (detailsRow.hasClass('d-none')) {
            // Show details row and load content
            detailsRow.removeClass('d-none');

            // Load details via AJAX
            $.get(`/company/${companyId}`, function(data) {
                const parser = new DOMParser();
                const htmlDoc = parser.parseFromString(data, 'text/html');
                const content = htmlDoc.querySelector('.company-details-content').innerHTML;
                detailsRow.find('td').html(content);
            });
        } else {
            // Hide details row
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