$(document).ready(function() {

    // --- USUNIĘTO KOD DOTYCZĄCY TABEL PODSUMOWUJĄCYCH ---
    // Usunięto: createTableIfNotExists, addRowToTable, addMobileCard, editRow
    // Usunięto: handleResponsiveTables
    // Usunięto: collectFormData, collectTableData
    // Usunięto: logikę w .click() dla #dodaj-adres, #dodaj-telefon itd., która używała tabel
    // Usunięto: logikę w $('form').on('submit', ...) która zbierała dane z tabel

    // Inicjalizacja Select2 dla pól wielokrotnego wyboru
    // Upewnij się, że klasa .select2-multiple jest dodana do odpowiednich pól w forms.py
     if ($.fn.select2) {
        $('.select2-multiple').select2({
            theme: 'bootstrap-5',
            width: $(this).data('width') ? $(this).data('width') : $(this).hasClass('w-100') ? '100%' : 'style',
            placeholder: $(this).data('placeholder'),
            closeOnSelect: false,
        });
    }

    // Obsługa kliknięcia ogólnego przycisku 'add-entry' do dodawania nowych zestawów pól
    $('body').on('click', '.add-entry', function() { // Używamy delegacji zdarzeń
        const containerId = $(this).data('container');
        const templateId = $(this).data('template-id');
        const container = $('#' + containerId);
        // Pobierz HTML z szablonu (zakładamy, że szablon zawiera JEDEN element .entry-form)
        const templateHtml = $('#' + templateId).html();

        // Znajdź aktualną liczbę wpisów, aby ustalić nowy indeks
        const entryClass = '.' + templateId.replace('-template', '-form'); // np. '.adres-form'
        const currentIndex = container.children(entryClass).length;

        // Zamień placeholder __prefix__ na nowy indeks w szablonie
        const newHtml = templateHtml.replace(/__prefix__/g, currentIndex);
        const newElement = $(newHtml); // Utwórz element jQuery

        // Get the CSRF token from the main form
        const csrfToken = $('input[name="csrf_token"]').val();

        // Determine the field list name from the container ID
        const fieldListName = containerId.replace('-container', ''); // e.g., 'adresy-container' -> 'adresy'

        // Find the placeholder CSRF input within the new element
        const csrfInput = newElement.find('.js-csrf-token');

        // Set the name and value for the CSRF input
        if (csrfInput.length > 0) {
            csrfInput.attr('name', `${fieldListName}-${currentIndex}-csrf_token`);
            csrfInput.val(csrfToken);
        }

        // Dodaj nowy zestaw pól do kontenera
        container.append(newElement);

        // Ponownie podłącz obsługę przycisków usuwania dla nowego elementu
        setupRemoveButtons();
        // Ponownie podłącz obsługę przycisków "Dodaj nowy typ" dla nowego elementu
        setupAddNewOptionButtons(newElement);
    });

    // Funkcja do obsługi przycisków usuwania
    function setupRemoveButtons() {
        // Używamy delegacji zdarzeń, aby działało dla dynamicznie dodanych elementów
        $('body').off('click', '.remove-entry').on('click', '.remove-entry', function() {
            // Znajdź najbliższego rodzica z klasą .entry-form i usuń go
            $(this).closest('.entry-form').remove();
            // Opcjonalnie: można dodać logikę przeindeksowania, ale zazwyczaj nie jest konieczna
        });
    }

    // --- LOGIKA DLA WOJEWÓDZTW/POWIATÓW I OBSZARU DZIAŁANIA ---

    // Funkcja do ładowania powiatów na podstawie wybranych województw
    function loadPowiaty() {
        const selectedWojewodztwa = $('#wojewodztwa').val(); // ID pola select województw
        const powiatySelect = $('#powiaty'); // ID pola select powiatów
        const currentPowiatySelection = powiatySelect.val() || []; // Zachowaj obecne zaznaczenie powiatów

        powiatySelect.empty(); // Wyczyść obecne opcje powiatów

        if (selectedWojewodztwa && selectedWojewodztwa.length > 0) {
             // Użyj Promise.all, aby poczekać na wszystkie zapytania AJAX
             const requests = selectedWojewodztwa.map(wojewodztwo_id => {
                // Zwróć obietnicę z zapytania AJAX
                return $.getJSON(`/api/powiaty/${wojewodztwo_id}`);
            });

            Promise.all(requests).then(results => {
                 const allPowiaty = [];
                 // Zbierz powiaty ze wszystkich odpowiedzi
                 results.forEach(data => {
                     if (data) {
                         allPowiaty.push(...data);
                     }
                 });

                 // Posortuj powiaty alfabetycznie
                 allPowiaty.sort((a, b) => a.name.localeCompare(b.name));

                 // Dodaj posortowane opcje do selecta powiatów
                 allPowiaty.forEach(item => {
                    powiatySelect.append($('<option>', {
                        value: item.id,
                        text: item.name
                    }));
                 });

                 // Przywróć poprzednie zaznaczenie powiatów (jeśli nadal istnieją)
                 powiatySelect.val(currentPowiatySelection);
                 // Odśwież Select2 dla powiatów, jeśli jest używany
                 if (powiatySelect.hasClass('select2-hidden-accessible')) {
                    powiatySelect.trigger('change');
                 }

            }).catch(error => {
                console.error("Błąd podczas ładowania powiatów:", error);
                 // Można dodać powiadomienie dla użytkownika
            });

        } else {
            // Jeśli żadne województwo nie jest wybrane, wyczyść i odśwież Select2 powiatów
            powiatySelect.empty();
             if (powiatySelect.hasClass('select2-hidden-accessible')) {
                powiatySelect.trigger('change');
            }
        }
    }

     // Funkcja kontrolująca widoczność wyboru województw/powiatów
    function toggleAreaSelection() {
        const krajValue = $('#kraj').val(); // ID pola select kraju
        if (krajValue === 'POL') {
            $('#area-selection').hide(); // Ukryj wybór województw/powiatów
             // Opcjonalnie wyczyść zaznaczenia województw/powiatów
            $('#wojewodztwa').val(null).trigger('change');
            $('#powiaty').val(null).trigger('change');
        } else {
            $('#area-selection').show(); // Pokaż wybór województw/powiatów
        }
    }

    // Nasłuchiwanie na zmianę województw
    $('#wojewodztwa').on('change', function() {
        loadPowiaty();
    });

     // Nasłuchiwanie na zmianę kraju
    $('#kraj').on('change', function() {
        toggleAreaSelection();
         // Jeśli wybrano inny kraj niż POL, załaduj powiaty dla wybranych województw
        if ($(this).val() !== 'POL') {
            loadPowiaty();
        }
    });

    // --- LOGIKA DLA OVERLAY "Dodaj nowy typ" ---

    // Funkcja do podłączania obsługi przycisków "Dodaj nowy typ"
    function setupAddNewOptionButtons(parentElement = document) {
         $(parentElement).find('.add-new-option').off('click').on('click', function() {
             const type = $(this).data('type');
             // Znajdź *najbliższy* element select w tym samym input-group lub kontenerze
             const selectElement = $(this).closest('.input-group').find('select');
             const selectId = selectElement.attr('id');

             if (!selectId) {
                console.error("Nie można znaleźć ID dla docelowego selecta dla przycisku 'Dodaj nowy typ'.");
                alert("Wystąpił błąd: Nie można zidentyfikować pola docelowego.");
                return;
             }

            // Ustawianie tytułu i etykiety w overlay
             let title = 'Dodaj nowy typ';
             let label = 'Nazwa';
             switch(type) {
                case 'adres_typ': title = 'Dodaj nowy typ adresu'; label = 'Nazwa typu adresu'; break;
                case 'email_typ': title = 'Dodaj nowy typ emaila'; label = 'Nazwa typu emaila'; break;
                case 'telefon_typ': title = 'Dodaj nowy typ telefonu'; label = 'Nazwa typu telefonu'; break;
                case 'firma_typ': title = 'Dodaj nowy typ firmy'; label = 'Nazwa typu firmy'; break;
                case 'specjalnosc': title = 'Dodaj nową specjalność'; label = 'Nazwa specjalności'; break;
             }
             $('#overlay-title').text(title);
             $('#overlay-label').text(label);

             // Zapisanie typu i ID docelowego selecta
             $('#overlay-type').val(type);
             $('#overlay-target-select-id').val(selectId); // Używamy nowego id pola ukrytego

             // Czyszczenie inputu w overlay i pokazanie go
             $('#overlay-input').val('');
             $('#overlay-form-container').removeClass('d-none');
             $('#overlay-input').focus(); // Ustaw fokus na polu input
         });
    }

    // Obsługa zamykania formularza overlay
    $('#close-overlay').click(function() {
        $('#overlay-form-container').addClass('d-none');
    });
    $(document).on('keydown', function(e) {
        if (e.key === 'Escape' && !$('#overlay-form-container').hasClass('d-none')) {
            $('#overlay-form-container').addClass('d-none');
        }
    });


    // Obsługa wysyłania formularza overlay
    $('#overlay-form').submit(function(e) {
        e.preventDefault();

        const type = $('#overlay-type').val();
        const value = $('#overlay-input').val().trim();
        const targetSelectId = $('#overlay-target-select-id').val(); // Pobierz ID docelowego selecta

        if (!value) {
            alert('Proszę wprowadzić wartość');
            return;
        }
        if (!targetSelectId) {
             console.error("Brak ID docelowego selecta w ukrytym polu overlay.");
             alert("Wystąpił błąd: Brak informacji o polu docelowym.");
             return;
        }

        // Określenie endpoint API
        let apiEndpoint;
        switch(type) {
            case 'adres_typ': apiEndpoint = '/api/adres_typ'; break;
            case 'email_typ': apiEndpoint = '/api/email_typ'; break;
            case 'telefon_typ': apiEndpoint = '/api/telefon_typ'; break;
            case 'firma_typ': apiEndpoint = '/api/firma_typ'; break;
            case 'specjalnosc': apiEndpoint = '/api/specjalnosc'; break;
            default:
                console.error("Nieznany typ dla overlay:", type);
                alert("Wystąpił błąd: Nieznany typ danych.");
                return;
        }

        // Wysłanie nowej wartości do API
        $.ajax({
            url: apiEndpoint,
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ name: value }),
            success: function(response) {
                $('#overlay-form-container').addClass('d-none');

                // Znajdź docelowy element select na podstawie zapisanego ID
                 const $targetSelect = $('#' + targetSelectId);

                 if (!$targetSelect.length) {
                     console.error("Nie znaleziono docelowego elementu select o ID:", targetSelectId);
                     alert("Wystąpił błąd: Nie znaleziono pola do zaktualizowania.");
                     return;
                 }

                const newOptionValue = response.id.toString();
                const newOptionText = value; // Używamy wartości wprowadzonej przez użytkownika

                // Sprawdź, czy opcja już nie istnieje (na wszelki wypadek)
                if ($targetSelect.find("option[value='" + newOptionValue + "']").length === 0) {
                    // Utwórz nową opcję HTML
                    var newOption = new Option(newOptionText, newOptionValue, false, false); // Ostatnie 'false' - nie zaznaczaj domyślnie
                    // Dodaj ją do selecta
                    $targetSelect.append(newOption);
                }

                 // Zaznacz nowo dodaną opcję
                 // Dla standardowego selecta:
                 if (!$targetSelect.prop('multiple')) {
                     $targetSelect.val(newOptionValue);
                 }
                 // Dla selecta wielokrotnego wyboru (jak specjalności):
                 else {
                     let currentSelections = $targetSelect.val() || [];
                     if (!Array.isArray(currentSelections)) {
                         currentSelections = [currentSelections];
                     }
                     if (!currentSelections.includes(newOptionValue)) {
                         currentSelections.push(newOptionValue);
                     }
                     $targetSelect.val(currentSelections);
                 }

                 // Odśwież Select2, jeśli jest używany na tym konkretnym polu
                 if ($targetSelect.hasClass('select2-hidden-accessible')) {
                     $targetSelect.trigger('change.select2'); // Trigger dla Select2
                 } else {
                      $targetSelect.trigger('change'); // Standardowy trigger
                 }

                alert('Dodano pomyślnie!');
            },
            error: function(xhr) {
                let errorMessage = 'Wystąpił błąd.';
                try {
                    const responseJson = JSON.parse(xhr.responseText);
                    if (responseJson && responseJson.error) {
                        errorMessage = 'Wystąpił błąd: ' + responseJson.error;
                    }
                } catch (e) { /* Ignoruj błąd parsowania */ }
                alert(errorMessage);
            }
        });
    });

    // Obsługa przycisku potwierdzającego usunięcie firmy
    $('#confirmDeleteCompany').on('click', function() {
        const companyId = $(this).data('company-id');
        $.ajax({
            url: `/company/${companyId}/delete`,
            type: 'POST',
            success: function(response) {
                if (response.success) {
                    $('#deleteCompanyModal').modal('hide');
                    alert('Firma została usunięta pomyślnie!');
                    window.location.href = response.redirect;
                } else {
                    $('#deleteCompanyModal').modal('hide');
                    alert('Wystąpił błąd: ' + response.error);
                }
            },
            error: function(xhr) {
                $('#deleteCompanyModal').modal('hide');
                let errorMessage = 'Wystąpił błąd podczas usuwania firmy.';
                try {
                    const responseJson = JSON.parse(xhr.responseText);
                    if (responseJson && responseJson.error) {
                        errorMessage = 'Wystąpił błąd: ' + responseJson.error;
                    }
                } catch (e) { /* Ignoruj błąd parsowania */ }
                alert(errorMessage);
            }
        });
    });

    // Removed the problematic form submit handler

    // --- INICJALIZACJA PO ZAŁADOWANIU STRONY ---
    setupRemoveButtons(); // Dla już istniejących wpisów
    setupAddNewOptionButtons(); // Dla już istniejących przycisków "Dodaj typ"
    toggleAreaSelection(); // Ustaw widoczność województw/powiatów na starcie
    // Załaduj powiaty dla początkowo wybranych województw (jeśli są)
    if ($('#kraj').val() !== 'POL' && $('#wojewodztwa').val() && $('#wojewodztwa').val().length > 0) {
         loadPowiaty();
    }

}); // Koniec $(document).ready