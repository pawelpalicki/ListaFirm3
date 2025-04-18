// Enable search filtering in multi-selects
function setupSearchableDropdowns() {
    // Helper do normalizacji tekstu
    const normalizeText = (text) => {
        return text
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '')
            .toLowerCase();
    };

    const multiSelects = document.querySelectorAll('select[multiple]');

    multiSelects.forEach(select => {
        // Create a search input
        const searchInput = document.createElement('input');
        searchInput.type = 'text';
        searchInput.className = 'form-control mb-2';
        searchInput.placeholder = 'Szukaj...';

        // Insert the search input before the select
        select.parentNode.insertBefore(searchInput, select);

        // Add event listener for searching
        searchInput.addEventListener('input', function() {
            const searchValue = normalizeText(this.value);

            Array.from(select.options).forEach(option => {
                const optionText = normalizeText(option.textContent);
                option.style.display = optionText.includes(searchValue) ? '' : 'none';
            });
        });
    });
}

// Initialize functionalities when document is ready
document.addEventListener('DOMContentLoaded', function() {
    setupSearchableDropdowns();
});

document.addEventListener('DOMContentLoaded', function() {
  const navbar = document.querySelector('.navbar');

  // Obsługa otwierania menu
  document.querySelector('.navbar-toggler').addEventListener('click', function() {
    navbar.classList.toggle('mobile-menu-open');
  });

  // Zamknij menu przy kliknięciu na overlay
  document.querySelector('.navbar-collapse').addEventListener('click', function(e) {
    if(e.target.classList.contains('nav-link')) {
      navbar.classList.remove('mobile-menu-open');
    }
  });
});

function toggleMobileFilter(show) {
  const overlay = document.getElementById('mobile-filter-overlay');
  if(show) {
    overlay.style.display = 'block';
    document.body.style.overflow = 'hidden';
    document.querySelector('.navbar').style.zIndex = '1500'; // Obniżamy navbar
  } else {
    overlay.style.display = 'none';
    document.body.style.overflow = '';
    document.querySelector('.navbar').style.zIndex = '';
  }
}

// W event listenerze dla przycisku otwierającego filtr
document.querySelector('.filter-toggle-btn').addEventListener('click', () => {
  toggleMobileFilter(true);
});

// W event listenerze dla zamykania overlay
document.querySelector('#mobile-filter-overlay').addEventListener('click', (e) => {
  if(e.target === document.querySelector('#mobile-filter-overlay')) {
    toggleMobileFilter(false);
  }
});