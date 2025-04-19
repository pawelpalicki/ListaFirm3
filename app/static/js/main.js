function setupCustomMultiSelect() {
    const normalizeText = (text) => {
        return text
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '')
            .toLowerCase();
    };

    // Funkcja do przekształcania select multiple w listę checkboxów
    function transformMultiSelect(selectElement) {
        // Zachowaj referencję do oryginalnego elementu i jego rodzica
        const originalSelect = selectElement;
        const parentElement = originalSelect.parentNode;

        // Stwórz kontener dla nowego elementu
        const container = document.createElement('div');
        container.className = 'custom-multi-select';

        // Stwórz pole wyszukiwania
        const searchInput = document.createElement('input');
        searchInput.type = 'text';
        searchInput.className = 'form-control mb-2';
        searchInput.placeholder = 'Szukaj...';
        container.appendChild(searchInput);

        // Pobierz wymiary oryginalnego selecta przed manipulacją
        const originalHeight = originalSelect.offsetHeight || 200;

        // Stwórz kontener na checkboxy z możliwością przewijania
        const checkboxContainer = document.createElement('div');
        checkboxContainer.className = 'checkbox-container';
        checkboxContainer.style.height = (originalHeight > 0) ? originalHeight + 'px' : '200px';
        checkboxContainer.style.overflowY = 'auto';
        checkboxContainer.style.border = '1px solid #ced4da';
        checkboxContainer.style.borderRadius = '0.5rem';
        checkboxContainer.style.padding = '0.5rem';
        checkboxContainer.style.marginBottom = '1rem';
        container.appendChild(checkboxContainer);

        // Dodaj ukryty select do przechowywania wartości
        const hiddenSelect = document.createElement('select');
        hiddenSelect.name = originalSelect.name;
        hiddenSelect.id = originalSelect.id;
        hiddenSelect.multiple = true;
        hiddenSelect.style.display = 'none';
        container.appendChild(hiddenSelect);

        // Dodaj wszystkie opcje z oryginalnego selecta
        const originalOptions = Array.from(originalSelect.options);
        originalOptions.forEach(option => {
            // Dodaj opcję do ukrytego selecta
            const hiddenOption = document.createElement('option');
            hiddenOption.value = option.value;
            hiddenOption.selected = option.selected;
            hiddenSelect.appendChild(hiddenOption);

            // Utwórz element div dla checkboxa
            const checkboxDiv = document.createElement('div');
            checkboxDiv.className = 'form-check';

            // Utwórz checkbox
            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.className = 'form-check-input';
            checkbox.value = option.value;
            checkbox.id = `checkbox-${originalSelect.id}-${option.value}`;
            checkbox.checked = option.selected;

            // Utwórz etykietę
            const label = document.createElement('label');
            label.className = 'form-check-label';
            label.htmlFor = checkbox.id;
            label.textContent = option.textContent;

            // Dodaj checkbox i etykietę do checkboxDiv
            checkboxDiv.appendChild(checkbox);
            checkboxDiv.appendChild(label);

            // Dodaj checkboxDiv do checkboxContainer
            checkboxContainer.appendChild(checkboxDiv);

            // Dodaj event listener do checkboxa
            checkbox.addEventListener('change', function() {
                hiddenOption.selected = this.checked;
            });
        });

        // Dodaj filtrowanie
        searchInput.addEventListener('input', function() {
            const searchValue = normalizeText(this.value);

            Array.from(checkboxContainer.querySelectorAll('.form-check')).forEach(checkboxDiv => {
                const label = checkboxDiv.querySelector('label');
                const labelText = normalizeText(label.textContent);
                checkboxDiv.style.display = labelText.includes(searchValue) ? '' : 'none';
            });
        });

        // Wstaw nowy kontener na miejsce oryginalnego selecta
        parentElement.insertBefore(container, originalSelect);
        parentElement.removeChild(originalSelect);
    }

    // Przekształć wszystkie wielokrotne selecty
    const multiSelects = document.querySelectorAll('select[multiple]');
    multiSelects.forEach(transformMultiSelect);
}

// Wszystkie inicjalizacje w jednym bloku DOMContentLoaded
document.addEventListener('DOMContentLoaded', function() {
    // Wywołaj najpierw setupCustomMultiSelect, aby zamienić wszystkie selecty multiple
    setupCustomMultiSelect();

    // Obsługa nawigacji mobilnej
    const navbar = document.querySelector('.navbar');

    // Obsługa otwierania menu
    const navbarToggler = document.querySelector('.navbar-toggler');
    if (navbarToggler) {
        navbarToggler.addEventListener('click', function() {
            navbar.classList.toggle('mobile-menu-open');
        });
    }

    // Zamknij menu przy kliknięciu na link
    const navbarCollapse = document.querySelector('.navbar-collapse');
    if (navbarCollapse) {
        navbarCollapse.addEventListener('click', function(e) {
            if(e.target.classList.contains('nav-link')) {
                navbar.classList.remove('mobile-menu-open');
            }
        });
    }

    // Obsługa filtra mobilnego
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

// Funkcja do obsługi filtra mobilnego
function toggleMobileFilter(show) {
    const overlay = document.getElementById('mobile-filter-overlay');
    if (!overlay) return;

    if(show) {
        overlay.style.display = 'block';
        document.body.style.overflow = 'hidden';
        const navbar = document.querySelector('.navbar');
        if (navbar) navbar.style.zIndex = '1500'; // Obniżamy navbar
    } else {
        overlay.style.display = 'none';
        document.body.style.overflow = '';
        const navbar = document.querySelector('.navbar');
        if (navbar) navbar.style.zIndex = '';
    }
}