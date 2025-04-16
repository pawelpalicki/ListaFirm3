// Enable search filtering in multi-selects
function setupSearchableDropdowns() {
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
            const searchValue = this.value.toLowerCase();
            
            Array.from(select.options).forEach(option => {
                const text = option.textContent.toLowerCase();
                option.style.display = text.includes(searchValue) ? '' : 'none';
            });
        });
    });
}

// Initialize functionalities when document is ready
document.addEventListener('DOMContentLoaded', function() {
    setupSearchableDropdowns();
});