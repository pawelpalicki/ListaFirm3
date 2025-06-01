$(document).ready(function() {

    // Sprawdzenie dostępności bibliotek jQuery i Select2
    if (typeof $ === 'undefined' || typeof $.fn.select2 === 'undefined') {
        console.error("jQuery or Select2 plugin not found. Skipping Select2 initialization for form fields.");
    } else {
        // Inicjalizacja Select2 dla pól formularza
        $('.select2-multiple').select2({
            theme: 'bootstrap-5',
            width: $(this).data('width') ? $(this).data('width') : ($(this).hasClass('w-100') ? '100%' : 'style'),
            placeholder: $(this).data('placeholder') || "Wybierz opcje...",
            closeOnSelect: false,
        });
    }

    // Obsługa dynamicznych formularzy (FieldList) - dodawanie wpisów
    $('body').off('click', '.add-entry').on('click', '.add-entry', function() {
        const containerId = $(this).data('container');
        const templateId = $(this).data('template-id');
        const container = $('#' + containerId);
        const templateHtml = $('#' + templateId).html();

        const entryClass = '.' + templateId.replace('-template', '-form');
        const currentIndex = container.children(entryClass).length;

        const newHtml = templateHtml.replace(/__prefix__/g, currentIndex);
        const newElement = $(newHtml);

        const csrfToken = $('input[name="csrf_token"]').val();
        const fieldListName = containerId.replace('-container', '');
        const csrfInput = newElement.find('.js-csrf-token');

        if (csrfInput.length > 0) {
            csrfInput.attr('name', `${fieldListName}-${currentIndex}-csrf_token`);
            csrfInput.val(csrfToken);
        }

        container.append(newElement);

        // Ponowne podłączenie handlerów dla przycisków w nowo dodanym elemencie
        setupRemoveButtons();
        setupAddNewOptionButtons(newElement);

        // Reinicjalizacja Select2 na nowo dodanych polach
        newElement.find('select.select2-multiple').select2({
             theme: 'bootstrap-5',
             width: 'style',
             placeholder: $(this).data('placeholder') || "Wybierz opcje...",
             closeOnSelect: false,
        });
    });

    // Funkcja do obsługi przycisków usuwania
    function setupRemoveButtons() {
        $('body').off('click', '.remove-entry').on('click', '.remove-entry', function() {
            $(this).closest('.entry-form').remove();
        });
    }

    // Funkcja do ładowania powiatów na podstawie wybranych województw
    function loadPowiaty() {
        const selectedWojewodztwa = $('#wojewodztwa').val();
        const powiatySelect = $('#powiaty');

        // Zapisz aktualnie zaznaczone powiaty PRZED wyczyszczeniem opcji
        const currentPowiatySelection = powiatySelect.val() || [];

        powiatySelect.empty();

        if (selectedWojewodztwa && selectedWojewodztwa.length > 0) {
            const requests = selectedWojewodztwa.map(wojewodztwo_id => {
                return $.getJSON(`/api/powiaty/${wojewodztwo_id}`);
            });

            Promise.all(requests).then(results => {
                let allPowiaty = [];
                results.forEach(data => {
                    if (data && Array.isArray(data)) {
                        allPowiaty.push(...data);
                    }
                });

                // Usunięcie duplikatów po ID powiatu i sortowanie po nazwie
                const powiatyMap = new Map();
                allPowiaty.forEach(p => powiatyMap.set(p.id, p));
                allPowiaty = Array.from(powiatyMap.values()).sort((a, b) => a.name.localeCompare(b.name));

                // Dodaj nowo pobrane opcje do elementu select
                allPowiaty.forEach(item => {
                    powiatySelect.append($('<option>', {
                        value: String(item.id), // Wartość 'value' w HTML musi być stringiem
                        text: item.name
                    }));
                });

                // Przywróć poprzednio zaznaczone powiaty na NOWYCH opcjach
                const selectionStrings = currentPowiatySelection.map(String);
                powiatySelect.val(selectionStrings);

                // Poinformuj Select2, że opcje i/lub wartość uległy zmianie
                if (powiatySelect.hasClass('select2-hidden-accessible')) {
                    powiatySelect.trigger('change.select2');
                } else {
                    powiatySelect.trigger('change');
                }

            }).catch(error => {
                console.error("Błąd podczas ładowania powiatów:", error);
                powiatySelect.empty().trigger('change.select2');
            });
        } else {
            // Jeśli brak wybranych województw, wyczyść pole powiatów.
            powiatySelect.empty().trigger('change.select2');
        }
    }

    // Funkcja kontrolująca widoczność sekcji obszaru działania
    function toggleAreaSelection() {
        const selectedOption = $('input[name="obszar_dzialania"]:checked').val();

        // Zarządzanie wartością ukrytego pola kraju
        $('#kraj').val(selectedOption === 'kraj' ? 'POL' : '');

        // Zarządzanie widocznością sekcji województw i powiatów
        $('#wojewodztwa-selection').hide();
        $('#powiaty-selection').hide();

        if (selectedOption === 'wojewodztwa') {
            $('#wojewodztwa-selection').show();
            // Wyczyść pole powiatów
            if ($('#powiaty').hasClass('select2-hidden-accessible')) {
                $('#powiaty').val(null).trigger('change.select2');
            } else {
                $('#powiaty').val(null).trigger('change');
            }
        } else if (selectedOption === 'powiaty') {
            $('#wojewodztwa-selection').show();
            $('#powiaty-selection').show();
            // Odświeżenie wizualne Select2, jeśli było ukryte
            if ($('#powiaty').hasClass('select2-hidden-accessible')) {
                $('#powiaty').select2('open').select2('close');
            }
        } else { // selectedOption === 'kraj'
            // Wyczyść pola województw i powiatów
            if ($('#wojewodztwa').hasClass('select2-hidden-accessible')) {
                $('#wojewodztwa').val(null).trigger('change.select2');
            } else {
                $('#wojewodztwa').val(null).trigger('change');
            }
            if ($('#powiaty').hasClass('select2-hidden-accessible')) {
                $('#powiaty').val(null).trigger('change.select2');
            } else {
                $('#powiaty').val(null).trigger('change');
            }
        }
    }

    // Funkcja do podłączania obsługi przycisków "Dodaj nowy typ"
    function setupAddNewOptionButtons(parentElement = document) {
        $(parentElement).find('.add-new-option').off('click').on('click', function() {
            const type = $(this).data('type');
            const selectElement = $(this).closest('.input-group').find('select');
            const selectId = selectElement.attr('id');

            if (!selectId) {
                console.error("Cannot find ID for the target select element for the 'Add New Type' button.");
                alert("Wystąpił błąd: Nie można zidentyfikować pola docelowego.");
                return;
            }

            // Ustawianie tytułu i etykiety w formularzu overlay
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

            // Zapisanie typu encji i ID docelowego selecta w ukrytych polach overlay
            $('#overlay-type').val(type);
            $('#overlay-target-select-id').val(selectId);

            // Czyszczenie inputu w overlay i pokazanie kontenera
            $('#overlay-input').val('');
            $('#overlay-form-container').removeClass('d-none');
            $('#overlay-input').focus();
        });
    }

    // Obsługa zamykania formularza overlay kliknięciem na przycisk X
    $('#close-overlay').click(function() {
        $('#overlay-form-container').addClass('d-none');
    });

    // Obsługa zamykania formularza overlay klawiszem ESC
    $(document).on('keydown', function(e) {
        if ((e.key === 'Escape' || e.keyCode === 27) && !$('#overlay-form-container').hasClass('d-none')) {
            $('#overlay-form-container').addClass('d-none');
        }
    });

    // Obsługa wysyłania formularza overlay (dodawanie nowej opcji przez API)
    $('#overlay-form').submit(function(e) {
        e.preventDefault();

        const type = $('#overlay-type').val();
        const value = $('#overlay-input').val().trim();
        const targetSelectId = $('#overlay-target-select-id').val();

        if (!value) {
            alert('Proszę wprowadzić wartość');
            return;
        }
        if (!targetSelectId) {
            console.error("Missing target select ID in hidden overlay field.");
            alert("Wystąpił błąd wewnętrzny: Brak informacji o polu docelowym.");
            return;
        }

        let apiEndpoint;
        switch(type) {
            case 'adres_typ': apiEndpoint = '/api/adres_typ'; break;
            case 'email_typ': apiEndpoint = '/api/email_typ'; break;
            case 'telefon_typ': apiEndpoint = '/api/telefon_typ'; break;
            case 'firma_typ': apiEndpoint = '/api/firma_typ'; break;
            case 'specjalnosc': apiEndpoint = '/api/specjalnosc'; break;
            default:
                console.error("Unknown type for overlay form submission:", type);
                alert("Wystąpił błąd: Nieznany typ danych do dodania.");
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

                const $targetSelect = $('#' + targetSelectId);

                if (!$targetSelect.length) {
                    console.error("Target select element not found after API success. ID:", targetSelectId);
                    alert("Wystąpił błąd wewnętrzny: Nie znaleziono pola do zaktualizowania po dodaniu.");
                    return;
                }

                // Pobierz nowe ID i nazwę z odpowiedzi API, konwertując ID na string
                const newOptionValue = String(response.id);
                const newOptionText = response.name || value;

                // Sprawdź, czy opcja z tą wartością już istnieje; jeśli nie, dodaj ją
                if ($targetSelect.find("option[value='" + newOptionValue + "']").length === 0) {
                    const newOption = new Option(newOptionText, newOptionValue, false, false);
                    $targetSelect.append(newOption);
                }

                // *** Nowa logika: Upewnij się, że nowo dodana opcja jest zaznaczona ***
                let currentSelections = $targetSelect.val() || [];
                // Jeśli pole jest single-select, po prostu ustaw nową wartość
                if (!$targetSelect.prop('multiple')) {
                    $targetSelect.val(newOptionValue);
                } else { // Jeśli to multiple-select, dodaj nową wartość do istniejących
                    if (!Array.isArray(currentSelections)) {
                        currentSelections = currentSelections ? [String(currentSelections)] : [];
                    }
                    if (!currentSelections.includes(newOptionValue)) {
                        currentSelections.push(newOptionValue);
                    }
                    $targetSelect.val(currentSelections);
                }

                // Poinformuj Select2, że opcje lub wartość uległy zmianie, aby odświeżył wyświetlanie
                if ($targetSelect.hasClass('select2-hidden-accessible')) {
                    $targetSelect.trigger('change.select2');
                } else {
                    $targetSelect.trigger('change');
                }

                // --- BEGIN NEW LOGIC TO UPDATE TEMPLATES ---
                let templateIdToUpdate;
                let selectInTemplateSelector;

                switch(type) {
                    case 'adres_typ':
                        templateIdToUpdate = '#adres-template';
                        selectInTemplateSelector = 'select[name="adresy-__prefix__-typ_adresu"]';
                        break;
                    case 'email_typ':
                        templateIdToUpdate = '#email-template';
                        selectInTemplateSelector = 'select[name="emaile-__prefix__-typ_emaila"]';
                        break;
                    case 'telefon_typ':
                        templateIdToUpdate = '#telefon-template';
                        selectInTemplateSelector = 'select[name="telefony-__prefix__-typ_telefonu"]';
                        break;
                    case 'firma_typ':
                        // This case handles the main company type select if it was the target.
                        // No specific template update for FieldList, as 'typ_firmy' is usually singular.
                        if (targetSelectId === 'typ_firmy') {
                             const $typFirmySelect = $('#typ_firmy');
                             if ($typFirmySelect.find("option[value='" + newOptionValue + "']").length === 0) {
                                const newTypFirmyOption = new Option(newOptionText, newOptionValue, false, false);
                                $typFirmySelect.append(newTypFirmyOption); // .trigger('change') is handled by commonSelectClass logic later or by $targetSelect
                             }
                        }
                        break;
                    case 'specjalnosc':
                        // This case handles the main 'specjalnosci' multi-select if it was the target.
                        // No specific template update for FieldList, as 'specjalnosci' is usually singular.
                        if (targetSelectId === 'specjalnosci') {
                             const $specjalnosciSelect = $('#specjalnosci');
                             if ($specjalnosciSelect.find("option[value='" + newOptionValue + "']").length === 0) {
                                const newSpecOption = new Option(newOptionText, newOptionValue, false, false);
                                $specjalnosciSelect.append(newSpecOption); // .trigger('change') is handled by commonSelectClass logic or $targetSelect
                             }
                        }
                        break;
                }

                if (templateIdToUpdate && selectInTemplateSelector) {
                    const $template = $(templateIdToUpdate);
                    if ($template.length) {
                        const $selectInTemplate = $template.find(selectInTemplateSelector);
                        if ($selectInTemplate.length) {
                            if ($selectInTemplate.find("option[value='" + newOptionValue + "']").length === 0) {
                                const newOptionForTemplate = new Option(newOptionText, newOptionValue, false, false);
                                $selectInTemplate.append(newOptionForTemplate);
                            }
                        } else {
                            console.warn("Select element not found in template: " + selectInTemplateSelector + " within " + templateIdToUpdate);
                        }
                    } else {
                        console.warn("Template not found: " + templateIdToUpdate);
                    }
                }
                // --- END NEW LOGIC TO UPDATE TEMPLATES ---

                // Update ALL existing select fields of the same type on the page
                let commonSelectSelector;
                switch(type) {
                    case 'adres_typ': commonSelectSelector = 'select[id^="adresy-"][id$="-typ_adresu"]'; break;
                    case 'email_typ': commonSelectSelector = 'select[id^="emaile-"][id$="-typ_emaila"]'; break;
                    case 'telefon_typ': commonSelectSelector = 'select[id^="telefony-"][id$="-typ_telefonu"]'; break;
                    case 'firma_typ': commonSelectSelector = '#typ_firmy'; break; // Specific ID for main company type
                    case 'specjalnosc': commonSelectSelector = '#specjalnosci'; break; // Specific ID for main specialties
                }

                if (commonSelectSelector) {
                    $(commonSelectSelector).each(function() {
                        const $selectToUpdate = $(this);
                        // Avoid re-processing the $targetSelect if it's the same, as it's already updated.
                        if ($selectToUpdate.attr('id') === targetSelectId && $targetSelect.find("option[value='" + newOptionValue + "']").length > 0) {
                            // If it is the target select, it's already handled, ensure its Select2 is updated if applicable
                            if ($selectToUpdate.hasClass('select2-hidden-accessible')) {
                                $selectToUpdate.trigger('change.select2');
                            } else {
                                 $selectToUpdate.trigger('change');
                            }
                            return; // Skip to next iteration
                        }

                        if ($selectToUpdate.find("option[value='" + newOptionValue + "']").length === 0) {
                            const newOptionGlobal = new Option(newOptionText, newOptionValue, false, false);
                            $selectToUpdate.append(newOptionGlobal);
                        }
                        // If this select is a Select2 instance and was modified, trigger change
                        // Check if it was actually modified to avoid redundant triggers if the option already existed.
                         if ($selectToUpdate.hasClass('select2-hidden-accessible')) {
                            $selectToUpdate.trigger('change.select2');
                        } else {
                             $selectToUpdate.trigger('change');
                        }
                    });
                }
                // *** Komunikat o sukcesie ***
                alert(`Pomyślnie dodano: "${newOptionText}"`);
            },
            error: function(xhr) {
                let errorMessage = 'Wystąpił błąd podczas dodawania danych.';
                try {
                    const responseJson = JSON.parse(xhr.responseText);
                    if (responseJson && responseJson.error) {
                        errorMessage = 'Wystąpił błąd: ' + responseJson.error;
                    } else if (xhr.status === 400) {
                        errorMessage = 'Błąd danych: Wprowadzona wartość jest nieprawidłowa lub już istnieje.';
                    } else if (xhr.status === 404) {
                        errorMessage = 'Błąd: Endpoint API nie znaleziony.';
                    } else if (xhr.status === 500) {
                        errorMessage = 'Błąd serwera: Wystąpił problem po stronie serwera.';
                    }
                } catch (e) {
                    errorMessage += ` (Status: ${xhr.status})`;
                    console.error("Error parsing API response:", e);
                }
                alert(errorMessage);
            }
        });
    });

    // Nasłuchiwanie na zmiany użytkownika (po inicjalizacji startowej)
    // Nasłuchiwanie na zmianę wybranego radiobuttona obszaru działania
    $('input[name="obszar_dzialania"]').change(function() {
        const selectedOption = $(this).val();
        toggleAreaSelection();

        // Jeśli użytkownik przełączył obszar działania na 'powiaty', załaduj listę powiatów
        if (selectedOption === 'powiaty') {
            loadPowiaty();
        }
    });

    // Nasłuchiwanie na zmianę wybranych województw (Select2)
    $('#wojewodztwa').on('change.select2', function() {
        // Jeśli aktualnie wybrany obszar działania to 'powiaty', przeładuj listę powiatów
        if ($('input[name="obszar_dzialania"]:checked').val() === 'powiaty') {
            loadPowiaty();
        }
    });

    // Logika usuwania firmy
    // Obsługa kliknięcia na przycisk potwierdzający usunięcie firmy w modalu
    $('#confirmDeleteCompany').on('click', function() {
        const companyId = $(this).data('company-id');

        // Wysyłanie żądania POST do endpointu usuwania firmy
        $.ajax({
            url: `/company/${companyId}/delete`,
            type: 'POST',
            success: function(response) {
                if (response.success) {
                    $('#deleteCompanyModal').modal('hide');
                    // alert('Firma została usunięta pomyślnie!');
                    // Przekierowanie użytkownika na stronę główną po usunięciu
                    window.location.href = response.redirect;
                } else {
                    $('#deleteCompanyModal').modal('hide');
                    alert('Wystąpił błąd podczas usuwania: ' + (response.error || 'Nieznany błąd'));
                }
            },
            error: function(xhr) {
                $('#deleteCompanyModal').modal('hide');
                let errorMessage = 'Wystąpił błąd podczas komunikacji z serwerem podczas usuwania firmy.';
                try {
                    const responseJson = JSON.parse(xhr.responseText);
                    if (responseJson && responseJson.error) {
                        errorMessage = 'Wystąpił błąd: ' + responseJson.error;
                    } else {
                        errorMessage += ` (Status: ${xhr.status})`;
                    }
                } catch (e) {
                    errorMessage += ` (Status: ${xhr.status})`;
                    console.error("Error parsing delete error response:", e);
                }
                alert(errorMessage);
            }
        });
    });

    // Inicjalizacja stanu formularza po załadowaniu strony
    // Podłączenie handlerów do przycisków usuwania i dodawania nowych typów
    setupRemoveButtons();
    setupAddNewOptionButtons();

    // Ustawienie początkowej widoczności sekcji województw/powiatów
    toggleAreaSelection();

    // Dynamiczne ładowanie powiatów na starcie, jeśli obszar działania to 'powiaty'
    const initialSelectedArea = $('input[name="obszar_dzialania"]:checked').val();
    if (initialSelectedArea === 'powiaty') {
        loadPowiaty();
    }
});