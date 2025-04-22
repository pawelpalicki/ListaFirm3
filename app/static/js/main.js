$(document).ready(function() {
    // Funkcja normalizująca tekst
    const normalizeText = (text) => {
        return text
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '')
            .toLowerCase();
    };

    // Inicjalizacja Select2 dla desktopowej wersji
    $('#specialties').select2({
        placeholder: "Wybierz specjalność - wpisz by filtrować",
        allowClear: true,
        language: {
            noResults: function () {
                return "Nie znaleziono wyników";
            },
            searching: function () {
                return "Szukam...";
            }
        },
        dropdownCssClass: "select2-dropdown--custom",  // Dodano własne klasy CSS
        selectionCssClass: "select2-selection--custom",
        dropdownParent: $('body')
    });

    // Inicjalizacja Select2 dla mobilnej wersji
    $('#specialties-mobile').select2({
        placeholder: "Wybierz specjalność - wpisz by filtrować",
        allowClear: true,
        language: {
            noResults: function () {
                return "Nie znaleziono wyników";
            },
            searching: function () {
                return "Szukam...";
            }
        },
        dropdownCssClass: "select2-dropdown--custom",  // Dodano własne klasy CSS
        selectionCssClass: "select2-selection--custom",
        dropdownParent: $('#mobile-filter-overlay')
    });

    // Dodaj obsługę wyszukiwania niewrażliwego na polskie znaki i wielkość liter dla Select2
    $.fn.select2.amd.require(['select2/compat/matcher'], function(matcher) {
        $('#specialties, #specialties-mobile').select2({
            matcher: function(params, data) {
                if ($.trim(params.term) === '') {
                    return data;
                }
                if (typeof data.text === 'undefined') {
                    return null;
                }
                var normalizedSearchTerm = normalizeText(params.term);
                var normalizedDataText = normalizeText(data.text);
                if (normalizedDataText.indexOf(normalizedSearchTerm) > -1) {
                    return data;
                }
                return null;
            }
        });
    });


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


    // Handle wojewodztwo change to update powiaty list
    $('#wojewodztwo, #wojewodztwo-mobile').change(function() {
        const wojewodztwoId = $(this).val();
        const powiatSelect = $(this).attr('id').includes('mobile') ? $('#powiat-mobile') : $('#powiat');

        if (wojewodztwoId) {
            $.getJSON(`/api/powiaty/${wojewodztwoId}`, function(data) {
                powiatSelect.empty();
                powiatSelect.append('<option value="">Wybierz powiat</option>');
                $.each(data, function(i, item) {
                    powiatSelect.append($('<option>').attr('value', item.id).text(item.name));
                });
            });
        } else {
            powiatSelect.empty().append('<option value="">Wybierz powiat</option>');
        }
    });

    // Handle company row click to show details - przeniesiono z index.html
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