$(document).ready(function() {
    // Inicjalizacja Select2 dla odpowiednich pól
    initializeSelect2();

    $('#dodaj-adres').click(function() {
        var adresyContainer = $('#adresy-container');
        var index = adresyContainer.children('.adres-form').length;
        adresyContainer.append(`
            <div class="adres-form">
                <div class="mb-2">
                    <label class="form-label">Typ adresu</label>
                    <select class="form-select" name="adresy-${index}-typ_adresu"></select>
                </div>
                <div class="mb-2">
                    <label class="form-label">Kod</label>
                    <input type="text" class="form-control" name="adresy-${index}-kod">
                </div>
                <div class="mb-2">
                    <label class="form-label">Miejscowość</label>
                    <input type="text" class="form-control" name="adresy-${index}-miejscowosc">
                </div>
                <div class="mb-2">
                    <label class="form-label">Ulica/Miejscowość</label>
                    <input type="text" class="form-control" name="adresy-${index}-ulica_miejscowosc">
                </div>
            </div>
        `);
    });

    $('#dodaj-email').click(function() {
        var emaileContainer = $('#emaile-container');
        var index = emaileContainer.children('.email-form').length;
        emaileContainer.append(`
            <div class="email-form">
                <div class="mb-2">
                    <label class="form-label">Typ e-maila</label>
                    <select class="form-select" name="emaile-${index}-typ_emaila"></select>
                </div>
                <div class="mb-2">
                    <label class="form-label">E-mail</label>
                    <input type="email" class="form-control" name="emaile-${index}-email">
                </div>
            </div>
        `);
    });

    // Modyfikacja obsługi województw - użycie Select2 zamiast zwykłego selecta
    // Ponieważ Select2 ma inne zachowanie niż standardowe pola, modyfikujemy funkcje

    // Obsługa zmian w Select2 województwa
    $('#wojewodztwa').on('change', function() {
        loadPowiaty();
    });

    // Obsługa zmian w Select2 powiatów - jeśli potrzebna
    $('#powiaty').on('change', function() {
        // Ewentualny kod obsługi zmiany powiatów
    });

    // Funkcja do ładowania powiatów na podstawie wybranych województw
    function loadPowiaty() {
        const selectedWojewodztwa = $('#wojewodztwa').val();

        if (selectedWojewodztwa && selectedWojewodztwa.length > 0) {
            // Pobieramy powiaty dla wszystkich wybranych województw
            // Możesz dostosować to do swojego API, jeśli obsługuje wiele województw naraz
            const firstWojewodztwo = selectedWojewodztwa[0];

            $.getJSON(`/api/powiaty/${firstWojewodztwo}`, function(data) {
                const powiatySelect = $('#powiaty');

                // Zachowujemy aktualnie wybrane powiaty
                const currentSelection = powiatySelect.val() || [];

                // Resetujemy opcje
                powiatySelect.empty();

                // Dodajemy nowe opcje
                $.each(data, function(i, item) {
                    powiatySelect.append($('<option>').attr('value', item.id).text(item.name));
                });

                // Aktualizujemy Select2
                powiatySelect.val(currentSelection).trigger('change');
            });
        }
    }

    // Funkcja inicjalizująca Select2 dla wszystkich odpowiednich pól
    function initializeSelect2() {
        // Inicjalizacja dla głównych pól wyboru
        $('#specjalnosci').select2({
            width: '100%',
            theme: 'classic',
            placeholder: "Wybierz specjalności...",
            allowClear: true
        });

        $('#wojewodztwa').select2({
            width: '100%',
            theme: 'classic',
            placeholder: "Wybierz województwa...",
            allowClear: true
        });

        $('#powiaty').select2({
            width: '100%',
            theme: 'classic',
            placeholder: "Wybierz powiaty...",
            allowClear: true
        });

        // Inicjalizacja dla innych pól SelectField, które mogą wymagać Select2
        $('.select2-field').select2({
            width: '100%',
            theme: 'classic'
        });

        // Zapisujemy referencje do oryginalnych funkcji Select2
        const originalSelect2 = $.fn.select2;

        // Rozszerzamy metodę .append() jQuery, aby automatycznie inicjalizować Select2 dla nowo dodanych pól
        const originalAppend = $.fn.append;
        $.fn.append = function() {
            const result = originalAppend.apply(this, arguments);
            if (this.find('select').length > 0) {
                this.find('select').each(function() {
                    if (!$(this).data('select2')) {
                        $(this).select2({
                            width: '100%',
                            theme: 'classic'
                        });
                    }
                });
            }
            return result;
        };
    }
});