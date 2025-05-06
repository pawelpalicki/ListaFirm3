// Ensure the document is ready before running script
$(document).ready(function() {

    // --- SPRAWDZENIE DOSTĘPNOŚCI BIBLIOTEK ---
    // Sprawdzamy, czy jQuery i Select2 są dostępne
    if (typeof $ === 'undefined' || typeof $.fn.select2 === 'undefined') {
        console.error("jQuery or Select2 plugin not found. Skipping Select2 initialization for form fields.");
        // Możesz tu dodać kod, który zresetuje pola select do domyślnego wyglądu,
        // jeśli Select2 jest opcjonalne.
        // $('.form-select').removeClass('select2-multiple').css('width', '');
    } else {
        // --- SEKCJA INICJALIZACJI SELECT2 DLA PÓL FORMULARZA FIRMY ---
        // Ta sekcja inicjalizuje Select2 na elementach z klasą .select2-multiple
        // Klasa ta jest dodawana automatycznie przez WTForms dla Select2MultipleField z forms.py
        $('.select2-multiple').select2({
            theme: 'bootstrap-5', // Użyj motywu bootstrap-5
            // Określenie szerokości: 100% jeśli element ma klasę w-100, inaczej auto (style) lub z data-width
            width: $(this).data('width') ? $(this).data('width') : ($(this).hasClass('w-100') ? '100%' : 'style'),
            placeholder: $(this).data('placeholder') || "Wybierz opcje...", // Użyj placeholder z data-placeholder lub domyślnego
            closeOnSelect: false, // Pozwala na wybór wielu opcji bez zamykania listy (dla multi-select)
            // Dodaj język polski, jeśli masz odpowiedni plik językowy Select2 załadowany (np. select2/dist/js/i18n/pl.js)
            // language: "pl", 
            // Jeśli potrzebujesz niestandardowego matchera (np. dla polskich znaków bez diakrytyków), możesz go tu dodać
            // matcher: function(params, data) { ... Twój kod matchera ... }
        });
        console.log("Select2 initialized on .select2-multiple elements."); // Debug
    }


    // --- SEKCJA DYNAMICZNYCH FORMULARZY (FieldList) ---

    // Obsługa kliknięcia ogólnego przycisku 'add-entry' do dodawania nowych zestawów pól (Delegacja zdarzeń)
    // Używamy delegacji zdarzeń na 'body' aby handlery działały dla elementów dodawanych dynamicznie.
    $('body').off('click', '.add-entry').on('click', '.add-entry', function() {
        const containerId = $(this).data('container');
        const templateId = $(this).data('template-id');
        const container = $('#' + containerId);
        // Pobierz HTML z szablonu (zakładamy, że szablon zawiera JEDEN element .entry-form)
        const templateHtml = $('#' + templateId).html();

        // Znajdź aktualną liczbę wpisów, aby ustalić nowy indeks (prefix dla nazw pól)
        const entryClass = '.' + templateId.replace('-template', '-form'); // np. '.adres-form'
        const currentIndex = container.children(entryClass).length;

        // Zamień placeholder __prefix__ na nowy indeks w szablonie HTML
        const newHtml = templateHtml.replace(/__prefix__/g, currentIndex);
        const newElement = $(newHtml); // Utwórz element jQuery z nowego HTML

        // Get the CSRF token from the main form and set it in the new entry's hidden field
        // To jest potrzebne dla walidacji CSRF w sub-formularzach w FieldList
        const csrfToken = $('input[name="csrf_token"]').val();
        const fieldListName = containerId.replace('-container', ''); // np. 'adresy-container' -> 'adresy'
        const csrfInput = newElement.find('.js-csrf-token');

        if (csrfInput.length > 0) {
            // Ustawiamy name i value dla tokenu CSRF w nowo dodanej sekcji formularza
            csrfInput.attr('name', `${fieldListName}-${currentIndex}-csrf_token`);
            csrfInput.val(csrfToken);
        }

        // Dodaj nowy zestaw pól (FieldList entry) do kontenera na stronie
        container.append(newElement);
        console.log("Added new entry to", containerId, "with index", currentIndex); // Debug

        // Ponownie podłącz handlery zdarzeń dla przycisków usuwania w nowym elemencie
        setupRemoveButtons();
        // Ponownie podłącz handlery zdarzeń dla przycisków "Dodaj nowy typ" w nowym elemencie
        setupAddNewOptionButtons(newElement);

        // *** WAŻNE: Zainicjalizuj Select2 na nowo dodanych polach select wewnątrz FieldList ***
        // Jeśli którekolwiek pola select w szablonach FieldList powinny być Select2,
        // musisz je tu zainicjalizować. Na podstawie company_form.html, pola typ_adresu,
        // typ_telefonu, typ_emaila nie mają klasy select2-multiple, więc zakładamy,
        // że mają to być standardowe selecty. Jeśli mają być Select2, dodaj tu:
        // newElement.find('select.form-select-for-fieldlist').select2({...}); // Użyj odpowiedniego selektora

        // Jeśli pola w FieldList mają być Select2MultipleField, dodaj tę klasę w szablonie i inicjalizuj tu:
        newElement.find('select.select2-multiple').select2({
             theme: 'bootstrap-5',
             width: 'style', // lub '100%'
             placeholder: $(this).data('placeholder') || "Wybierz opcje...",
             closeOnSelect: false,
             // ... inne opcje ...
        });
         console.log("Re-initialized Select2 on new elements if applicable."); // Debug
    });

    // Funkcja do obsługi przycisków usuwania (Delegacja zdarzeń)
    // Off().on() zapobiega wielokrotnemu podłączeniu tego samego handlera do body.
    function setupRemoveButtons() {
        $('body').off('click', '.remove-entry').on('click', '.remove-entry', function() {
            // Znajdź najbliższego rodzica z klasą .entry-form i usuń go z DOM
            $(this).closest('.entry-form').remove();
            // Opcjonalnie: można dodać logikę przeindeksowania pól po usunięciu,
            // ale WTForms zwykle radzi sobie bez tego dla prostego usuwania.
            console.log("Removed entry."); // Debug
        });
    }


    // --- LOGIKA DLA OBSZARU DZIAŁANIA ---

    // Funkcja do ładowania powiatów (poprawiona o konwersję ID i odświeżenie Select2)
    // Ta funkcja czyści istniejące opcje i dodaje nowe z API na podstawie wybranych województw.
    // Jest wywoływana, gdy użytkownik zmienia wybór województw lub przełącza obszar działania na 'powiaty'.
    function loadPowiaty() {
        // Select2 dla województw zwraca tablicę stringów dzięki coerce=str w forms.py
        const selectedWojewodztwa = $('#wojewodztwa').val();
        const powiatySelect = $('#powiaty');

        // *** WAŻNE: Zapisz aktualnie zaznaczone powiaty PRZED wyczyszczeniem opcji ***
        // To zadziała zarówno dla danych załadowanych przez Flask, jak i dla zaznaczeń użytkownika.
        // Zwróci listę Integerów dzięki coerce=int w forms.py dla pola powiaty.
        const currentPowiatySelection = powiatySelect.val() || [];
        console.log("loadPowiaty: Current selection before empty:", currentPowiatySelection); // Debug

        // *** Wyczyść istniejące opcje w Select2 ***
        powiatySelect.empty();
         console.log("loadPowiaty: Emptied #powiaty."); // Debug


        if (selectedWojewodztwa && selectedWojewodztwa.length > 0) {
            const requests = selectedWojewodztwa.map(wojewodztwo_id => {
                // wojewodztwo_id jest stringiem (z coerce=str)
                return $.getJSON(`/api/powiaty/${wojewodztwo_id}`);
            });

            Promise.all(requests).then(results => {
                let allPowiaty = [];
                results.forEach(data => {
                    if (data && Array.isArray(data)) {
                         // data to tablica obiektów [{id: 123, name: "Powiat X"}, ...], gdzie id jest intem z API
                        allPowiaty.push(...data);
                    } else if (data) {
                         console.warn("API did not return an array for one wojewodztwo:", data); // Debug
                    }
                });

                // Usunięcie duplikatów po ID powiatu na wypadek, gdy ten sam powiat jest przypisany do wielu województw w bazie (co jest mało prawdopodobne, ale dla bezpieczeństwa)
                const powiatyMap = new Map();
                allPowiaty.forEach(p => powiatyMap.set(p.id, p));
                allPowiaty = Array.from(powiatyMap.values());

                // Sortowanie po nazwie powiatu
                allPowiaty.sort((a, b) => a.name.localeCompare(b.name));

                // Dodaj nowo pobrane opcje do elementu select
                allPowiaty.forEach(item => {
                    // Dodaj opcję. value MUSI być stringiem, aby poprawnie działać z atrybutem value w HTML i jQuery .val()
                    // Mimo że coerce=int konwertuje wartość PRZY WYSŁANIU FORMULARZA,
                    // wartości w samym HTML SELECT tagu są stringami.
                    powiatySelect.append($('<option>', {
                        value: String(item.id), // Konwertujemy ID (Int z API) na string
                        text: item.name
                    }));
                });
                 console.log("loadPowiaty: Added", allPowiaty.length, "options to #powiaty."); // Debug


                // *** Przywróć zapisane/poprzednio zaznaczone powiaty na NOWYCH opcjach ***
                // currentPowiatySelection zawiera ID (Integer) z form.powiaty.data lub poprzedniego wyboru użytkownika
                // jQuery .val() na Select2 MultipleField przyjmuje tablicę wartości.
                // Konwersja na stringi jest zalecana dla spójności z value atrybutów <option>
                const selectionStrings = currentPowiatySelection.map(String);
                powiatySelect.val(selectionStrings);
                console.log("loadPowiaty: Attempting to set value:", selectionStrings); // Debug


                // *** Kluczowe: Poinformuj Select2, że opcje i/lub wartość uległy zmianie ***
                // Triggering 'change.select2' po dynamicznej zmianie opcji i wartości jest niezbędne,
                // aby Select2 odświeżyło swoje wyświetlanie (dodało/usunęło tagi dla multi-selecta).
                 if (powiatySelect.hasClass('select2-hidden-accessible')) {
                     powiatySelect.trigger('change.select2'); // Standardowy trigger Select2
                      console.log("loadPowiaty finished, triggered change.select2"); // Debug
                 } else {
                      powiatySelect.trigger('change'); // Standardowy trigger jQuery (mniej prawdopodobne, że się wykona na Select2)
                      console.log("loadPowiaty finished, triggered standard change"); // Debug
                 }

            }).catch(error => {
                console.error("Błąd podczas ładowania powiatów:", error);
                 // Wyczyść pole i odśwież Select2 w przypadku błędu ładowania API
                 powiatySelect.empty().trigger('change.select2');
            });
        } else {
            // Jeśli brak wybranych województw (lub odznaczono wszystkie), wyczyść pole powiatów.
             console.log("loadPowiaty: No wojewodztwa selected, emptying #powiaty."); // Debug
             powiatySelect.empty().trigger('change.select2');
        }
    }

    // Funkcja kontrolująca widoczność sekcji obszaru działania
    // Ta funkcja odpowiada TYLKO za pokazywanie/ukrywanie divów na podstawie radio buttona.
    // NIE wywołuje loadPowiaty bezpośrednio w reakcji na samą zmianę widoczności,
    // bo ładowanie powiatów jest powiązane ze zmianą wyboru województw lub przełączeniem na 'powiaty'.
    function toggleAreaSelection() {
        // Pobierz wartość zaznaczonego radio buttona obszaru działania
        const selectedOption = $('input[name="obszar_dzialania"]:checked').val();
        console.log("toggleAreaSelection called, selected radio:", selectedOption); // Debug

        // Zarządzanie wartością ukrytego pola kraju
        // Ustawiamy wartość, ale bez trigger('change'), żeby nie wpływać na inne listenery niepotrzebnie
        if (selectedOption === 'kraj') {
            $('#kraj').val('POL');
        } else {
            $('#kraj').val('');
        }

        // Zarządzanie widocznością sekcji województw i powiatów
        // show() i hide() zmieniają styl CSS display
        $('#wojewodztwa-selection').hide();
        $('#powiaty-selection').hide();

        if (selectedOption === 'wojewodztwa') {
            $('#wojewodztwa-selection').show();
            // Jeśli przełączamy NA województwa, upewniamy się, że pole powiatów jest puste
            // i Select2 jest odświeżone, aby to pokazać wizualnie.
             if ($('#powiaty').hasClass('select2-hidden-accessible')) {
                 $('#powiaty').val(null).trigger('change.select2');
             } else { // Fallback dla zwykłego selecta, choć #powiaty powinno być Select2
                 $('#powiaty').val(null).trigger('change');
             }
             console.log("Toggle: Selected 'wojewodztwa', showing #wojewodztwa-selection, hiding/clearing #powiaty."); // Debug

        } else if (selectedOption === 'powiaty') {
            $('#wojewodztwa-selection').show(); // Twoja logika w szablonie pokazuje województwa również dla powiatów
            $('#powiaty-selection').show();
            // Kiedy przełączamy NA powiaty, sekcje stają się widoczne.
            // Select2 na polu powiaty (jeśli było ukryte) może wymagać odśświeżenia wizualnego
            // po zmianie display na 'block', aby poprawnie się wyrenderować.
             if ($('#powiaty').hasClass('select2-hidden-accessible')) {
                // Ten trik z open/close często pomaga, jeśli Select2 nie renderuje się dobrze na starcie na ukrytym elemencie
                // or after its container becomes visible.
                $('#powiaty').select2('open').select2('close');
                 console.log("Toggle: Selected 'powiaty', showing both sections, forcing #powiaty Select2 visual refresh."); // Debug
            } else {
                 console.log("Toggle: Selected 'powiaty', showing both sections."); // Debug
            }

        } else { // selectedOption === 'kraj'
             // Kiedy przełączamy NA kraj, upewniamy się, że pola województw i powiatów są puste
             // i Select2 jest odświeżone, aby pokazać brak zaznaczenia.
             if ($('#wojewodztwa').hasClass('select2-hidden-accessible')) {
                $('#wojewodztwa').val(null).trigger('change.select2');
            } else { // Fallback dla zwykłego selecta, choć #wojewodztwa powinno być Select2
                $('#wojewodztwa').val(null).trigger('change');
            }
             if ($('#powiaty').hasClass('select2-hidden-accessible')) {
                 $('#powiaty').val(null).trigger('change.select2');
             } else { // Fallback dla zwykłego selecta
                 $('#powiaty').val(null).trigger('change');
             }
             console.log("Toggle: Selected 'kraj', hiding/clearing both sections."); // Debug
        }
    }


    // --- LOGIKA DLA OVERLAY "Dodaj nowy typ" (Przeniesiona tutaj) ---

    // Funkcja do podłączania obsługi przycisków "Dodaj nowy typ" (Delegacja zdarzeń)
    // Używamy delegacji zdarzeń na 'body'
    // off().on() zapobiega wielokrotnemu podłączeniu handlera na body.
    function setupAddNewOptionButtons(parentElement = document) {
        $(parentElement).find('.add-new-option').off('click').on('click', function() {
             const type = $(this).data('type'); // Pobierz typ encji do dodania (adres_typ, email_typ itp.)
             // Znajdź *najbliższy* element select powiązany z tym przyciskiem.
             const selectElement = $(this).closest('.input-group').find('select');
             const selectId = selectElement.attr('id'); // Pobierz ID tego selecta

             if (!selectId) {
                 console.error("Cannot find ID for the target select element for the 'Add New Type' button.");
                 alert("Wystąpił błąd: Nie można zidentyfikować pola docelowego.");
                 return;
             }
              console.log("Add new option button clicked. Type:", type, "Target Select ID:", selectId); // Debug


            // Ustawianie tytułu i etykiety w formularzu overlay w zależności od typu
             let title = 'Dodaj nowy typ';
             let label = 'Nazwa';
             switch(type) {
                case 'adres_typ': title = 'Dodaj nowy typ adresu'; label = 'Nazwa typu adresu'; break;
                case 'email_typ': title = 'Dodaj nowy typ emaila'; label = 'Nazwa typu emaila'; break;
                case 'telefon_typ': title = 'Dodaj nowy typ telefonu'; label = 'Nazwa typu telefonu'; break;
                case 'firma_typ': title = 'Dodaj nowy typ firmy'; label = 'Nazwa typu firmy'; break;
                case 'specjalnosc': title = 'Dodaj nową specjalność'; label = 'Nazwa specjalności'; break;
                default: console.warn("Unknown overlay type:", type);
             }
             $('#overlay-title').text(title);
             $('#overlay-label').text(label);

             // Zapisanie typu dodawanej encji i ID docelowego selecta w ukrytych polach overlay
             $('#overlay-type').val(type);
             $('#overlay-target-select-id').val(selectId);

             // Czyszczenie inputu w overlay i pokazanie kontenera overlay
             $('#overlay-input').val('');
             $('#overlay-form-container').removeClass('d-none');
             $('#overlay-input').focus(); // Ustaw fokus na polu input dla wygody użytkownika
         });
    }

    // Obsługa zamykania formularza overlay kliknięciem na przycisk X
    $('#close-overlay').click(function() {
        $('#overlay-form-container').addClass('d-none');
         console.log("Overlay form closed via close button."); // Debug
    });

    // Obsługa zamykania formularza overlay klawiszem ESC
    $(document).on('keydown', function(e) {
        // Sprawdź, czy klawisz to ESC (kod 27 lub 'Escape') i czy overlay jest widoczny
        if ((e.key === 'Escape' || e.keyCode === 27) && !$('#overlay-form-container').hasClass('d-none')) {
            $('#overlay-form-container').addClass('d-none');
             console.log("Overlay form closed via ESC key."); // Debug
        }
    });

    // Obsługa wysyłania formularza overlay (dodawanie nowej opcji przez API)
    $('#overlay-form').submit(function(e) {
        e.preventDefault(); // Zapobiegaj domyślnej wysyłce formularza

        const type = $('#overlay-type').val(); // Pobierz typ z ukrytego pola
        const value = $('#overlay-input').val().trim(); // Pobierz wartość z pola tekstowego
        const targetSelectId = $('#overlay-target-select-id').val(); // Pobierz ID docelowego selecta

        if (!value) {
            alert('Proszę wprowadzić wartość');
            return;
        }
        if (!targetSelectId) {
             console.error("Missing target select ID in hidden overlay field.");
             alert("Wystąpił błąd wewnętrzny: Brak informacji o polu docelowym.");
             return;
        }

        // Określenie endpoint API na podstawie typu
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
         console.log("Overlay form submitting. Type:", type, "Value:", value, "Endpoint:", apiEndpoint); // Debug


        // Wysłanie nowej wartości do API
        $.ajax({
            url: apiEndpoint,
            type: 'POST',
            contentType: 'application/json', // Wysyłamy JSON
            data: JSON.stringify({ name: value }), // Wysyłamy nazwę w formacie JSON
            success: function(response) {
                // Zamknij overlay po sukcesie
                $('#overlay-form-container').addClass('d-none');
                console.log("API call successful:", response); // Debug


                // Znajdź docelowy element select na stronie na podstawie zapisanego ID
                 const $targetSelect = $('#' + targetSelectId);

                 if (!$targetSelect.length) {
                     console.error("Target select element not found after API success. ID:", targetSelectId);
                     alert("Wystąpił błąd wewnętrzny: Nie znaleziono pola do zaktualizowania po dodaniu.");
                     return;
                 }

                // Pobierz nowe ID i nazwę z odpowiedzi API
                // WAŻNE: ID zwracane przez API dla powiatów i specjalnosci to Integery
                // Przy dodawaniu opcji do HTML SELECT tagu, value jest ZAWSZE stringiem.
                const newOptionValue = String(response.id); // Konwertujemy ID (Int/Text z API) na string dla atrybutu value
                const newOptionText = response.name || value; // Użyj nazwy z API lub wartości wprowadzonej przez użytkownika (jeśli API nie zwróciło nazwy)

                // Sprawdź, czy opcja z tym value (string) już nie istnieje w select
                if ($targetSelect.find("option[value='" + newOptionValue + "']").length === 0) {
                    // Utwórz nowy element <option>
                    // Ostatnie 'false' = opcja nie jest zaznaczona domyślnie przy dodaniu do selecta
                    var newOption = new Option(newOptionText, newOptionValue, false, false);
                    // Dodaj nową opcję do selecta
                    $targetSelect.append(newOption);
                    console.log("Added new option:", newOptionText, "with value:", newOptionValue, "to", targetSelectId); // Debug

                    // *** Zaznacz nowo dodaną opcję po dodaniu do selecta ***
                    // To jest ważne, aby nowo dodany typ był automatycznie wybrany w Select2.
                    let currentSelections = $targetSelect.val() || []; // Pobierz aktualne zaznaczenia (Select2 zwraca tablicę stringów dla multi)
                    // .val() może zwrócić null, string lub tablicę. Upewnij się, że mamy tablicę do pracy
                    if (!Array.isArray(currentSelections)) {
                         currentSelections = currentSelections ? [String(currentSelections)] : []; // Upewnij się, że elementy są stringami
                    }

                    // Dodaj wartość nowej opcji (jako string) do listy zaznaczeń, jeśli jej tam jeszcze nie ma
                    if (!currentSelections.includes(newOptionValue)) {
                         currentSelections.push(newOptionValue);
                    }

                    // Ustaw nową listę zaznaczeń na polu select. Select2 to podchwyci.
                    $targetSelect.val(currentSelections);
                     console.log("Attempting to set new selection:", currentSelections, "on", targetSelectId); // Debug

                } else {
                     console.log("Option with value", newOptionValue, "already exists in", targetSelectId + ". Not adding again."); // Debug
                    // Opcjonalnie: jeśli opcja istniała, ale nie była zaznaczona, możesz ją zaznaczyć
                    let currentSelections = $targetSelect.val() || [];
                     if (!Array.isArray(currentSelections)) {
                         currentSelections = currentSelections ? [String(currentSelections)] : [];
                    }
                    if (!currentSelections.includes(newOptionValue)) {
                         currentSelections.push(newOptionValue);
                         $targetSelect.val(currentSelections);
                         console.log("Option existed but not selected, set new selection:", currentSelections, "on", targetSelectId); // Debug
                    }
                }


                 // *** Kluczowe: Poinformuj Select2, że opcje lub wartość uległy zmianie ***
                 // To jest niezbędne, aby Select2 odświeżyło swoje wyświetlanie (dodało/usunęło tagi dla multi-selecta)
                 if ($targetSelect.hasClass('select2-hidden-accessible')) {
                     $targetSelect.trigger('change.select2'); // Trigger specyficzny dla Select2
                     console.log("Triggered change.select2 on", targetSelectId); // Debug
                 } else {
                      $targetSelect.trigger('change'); // Standardowy trigger jQuery dla zwykłych selectów
                      console.log("Triggered standard change on", targetSelectId); // Debug
                 }

                // flash message z Flaska pojawi się po przeładowaniu strony lub po sukcesie wysłania głównego formularza
                // alert('Dodano pomyślnie!'); // Unikaj alertów, które blokują JS
            },
            error: function(xhr) {
                // Obsługa błędów API
                let errorMessage = 'Wystąpił błąd podczas dodawania danych.';
                try {
                    const responseJson = JSON.parse(xhr.responseText);
                    // Jeśli API zwróciło błąd i jego treść
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
                    // Jeśli odpowiedź API nie jest JSON lub nie ma klucza error
                    errorMessage += ' (Status: ' + xhr.status + ')';
                    console.error("Error parsing API response:", e); // Debug
                }
                alert(errorMessage); // Pokaż alert z błędem
                 console.error("Overlay form submit AJAX error:", xhr.status, xhr.responseText); // Debug
            }
        });
    });


    // --- LOGIKA USUWANIA FIRMY ---
    // Obsługa kliknięcia na przycisk potwierdzający usunięcie firmy w modalu
    // Handler podłączony do przycisku #confirmDeleteCompany
    $('#confirmDeleteCompany').on('click', function() {
        const companyId = $(this).data('company-id'); // Pobierz ID firmy z atrybutu data
        console.log("Delete company confirmed for ID:", companyId); // Debug

        // Wysyłanie żądania POST do endpointu usuwania firmy
        $.ajax({
            url: `/company/${companyId}/delete`, // Endpoint usuwania
            type: 'POST', // Metoda POST (zalecane dla akcji usuwania)
            success: function(response) {
                // Obsługa odpowiedzi sukcesu z backendu
                if (response.success) {
                    $('#deleteCompanyModal').modal('hide'); // Ukryj modal
                    alert('Firma została usunięta pomyślnie!'); // Pokaż komunikat sukcesu
                    // Przekieruj użytkownika na stronę główną lub inną po usunięciu
                    window.location.href = response.redirect;
                } else {
                    // Obsługa odpowiedzi błędu z backendu
                    $('#deleteCompanyModal').modal('hide'); // Ukryj modal
                    alert('Wystąpił błąd podczas usuwania: ' + (response.error || 'Nieznany błąd')); // Pokaż komunikat błędu
                     console.error("Delete company backend error:", response.error); // Debug
                }
            },
            error: function(xhr) {
                // Obsługa błędów komunikacji AJAX (np. 404, 500)
                $('#deleteCompanyModal').modal('hide'); // Ukryj modal
                let errorMessage = 'Wystąpił błąd podczas komunikacji z serwerem podczas usuwania firmy.';
                 try {
                     const responseJson = JSON.parse(xhr.responseText);
                     if (responseJson && responseJson.error) {
                         errorMessage = 'Wystąpił błąd: ' + responseJson.error;
                     } else {
                          errorMessage += ' (Status: ' + xhr.status + ')';
                     }
                 } catch (e) {
                      errorMessage += ' (Status: ' + xhr.status + ')';
                      console.error("Error parsing delete error response:", e); // Debug
                 }
                alert(errorMessage); // Pokaż komunikat błędu
                 console.error("Delete company AJAX error:", xhr.status, xhr.responseText); // Debug
            }
        });
    });

    // Removed the problematic form submit handler - Walidacja i wysyłka formularza głównego jest teraz obsługiwana przez Flask/WTForms

    // --- INICJALIZACJA STANu FORMULARZA PO ZAŁADOWANIU STRONY ---
    // Ten blok kodu wykonuje się raz po całkowitym załadowaniu DOM

    // Podłącz handlery do przycisków usuwania i dodawania nowych typów
    // dla elementów, które zostały wyrenderowane przez Flask w szablonie HTML.
    setupRemoveButtons();
    setupAddNewOptionButtons();
    console.log("Initial setupRemoveButtons and setupAddNewOptionButtons completed."); // Debug


    // Ustaw początkową widoczność sekcji województw/powiatów
    // na podstawie wartości radio buttona 'obszar_dzialania', która została
    // ustawiona przez Flask na podstawie danych firmy (w przypadku edycji)
    // lub na wartość domyślną (w przypadku dodawania).
    // Ta funkcja tylko pokazuje/ukrywa divy i czyści pola ukryte.
    toggleAreaSelection();
    console.log("Initial toggleAreaSelection executed based on Flask form data."); // Debug


    // *** KLUCZOWA LOGIKA DLA STRONY EDYCJI FIRMY: Dynamiczne ładowanie powiatów na starcie, jeśli obszar = 'powiaty' ***
    // Sprawdzamy, jaka opcja obszaru działania była zaznaczona przez Flask przy pierwszym renderowaniu strony.
    const initialSelectedArea = $('input[name="obszar_dzialania"]:checked').val();
    console.log("Initial selected area radio value:", initialSelectedArea); // Debug


    if (initialSelectedArea === 'powiaty') {
        // Jeśli firma działa na poziomie powiatów (strona edycji),
        // musimy dynamicznie załadować listę OPCJI powiatów dostępnych dla JUŻ wybranych województw firmy.
        // Pole #wojewodztwa.val() zwróci ID województw, które Flask wstępnie zaznaczył.
        // Funkcja loadPowiaty() pobierze listę powiatów dla TYCH województw,
        // doda je do #powiaty Select2 i spróbuje przywrócić zapisane zaznaczenia powiatów
        // (które Flask wstępnie ustawił w form.powiaty.data i które zostały odczytane
        // przez loadPowiaty przed czyszczeniem opcji).
        console.log("Initial load (Edit page): Area is 'powiaty'. Calling loadPowiaty to filter options and restore selection from Flask data."); // Debug
        loadPowiaty(); // Ta funkcja pobierze opcje wg wybranych woj. i odświeży Select2/przywróci selekcję
    } else {
         console.log("Initial load: Area is not 'powiaty'. No initial loadPowiaty needed."); // Debug
    }
    // KONIEC KLUCZOWEJ LOGIKI DLA EDYCJI


    // --- NASŁUCHIWANIE NA ZMIANY UŻYTKOWNIKA (Po inicjalizacji startowej) ---

    // Nasłuchiwanie na zmianę wybranego radiobuttona obszaru działania
    // Ten handler uruchamia się, gdy użytkownik KLIKNIE na inny radio button obszaru działania.
    $('input[name="obszar_dzialania"]').change(function() {
        const selectedOption = $(this).val();
        console.log("User changed Area radio TO:", selectedOption); // Debug

        toggleAreaSelection(); // Zmień widoczność sekcji i wyczyść UKRYTE pola

        // Jeśli użytkownik przełączył obszar działania NA 'powiaty',
        // musimy załadować listę powiatów na podstawie AKUTALNIE wybranych województw.
        // Jeśli użytkownik przełączył Z 'powiaty' na coś innego, pole powiatów zostało już
        // wyczyszczone przez toggleAreaSelection(), loadPowiaty nie jest potrzebne.
        if (selectedOption === 'powiaty') {
             console.log("User changed area TO 'powiaty': Calling loadPowiaty for current wojewodztwa."); // Debug
             loadPowiaty();
        }
        // Jeśli zmieniono Z 'powiaty' na 'wojewodztwa', pole powiatów jest czyszczone w toggleAreaSelection
        // Jeśli zmieniono Z 'powiaty' na 'kraj', pola wojewodztwa i powiaty są czyszczone w toggleAreaSelection
    });

    // Nasłuchiwanie na zmianę wybranych województw
    // Ten handler uruchamia się, gdy użytkownik zmieni zaznaczenie w polu Select2 województw.
    // Używamy zdarzenia 'change.select2', które jest specyficzne dla Select2
    // i jest wywoływane po zmianie wartości przez interakcję użytkownika lub `.val().trigger('change.select2')`.
    $('#wojewodztwa').on('change.select2', function() {
        console.log("User changed Wojewodztwa selection."); // Debug
        // Jeśli aktualnie wybrany obszar działania to 'powiaty',
        // zmiana województw powinna spowodować przeładowanie listy dostępnych powiatów.
        // Pole powiatów zostanie wyczyszczone i zapełnione nowymi opcjami.
        // Zaznaczenie zostanie utracone (co jest oczekiwane przy zmianie filtrów województw).
        if ($('input[name="obszar_dzialania"]:checked').val() === 'powiaty') {
             console.log("Area is 'powiaty' and Wojewodztwa changed: Calling loadPowiaty to refresh available options."); // Debug
            loadPowiaty();
        } else {
             console.log("Area is not 'powiaty'. Wojewodztwa change ignored for Powiaty loading."); // Debug
        }
    });


    // --- LOGIKA USUWANIA FIRMY (Przeniesiona tutaj) ---
    // Obsługa kliknięcia na przycisk potwierdzający usunięcie firmy w modalu
    // Handler podłączony do przycisku #confirmDeleteCompany
    $('#confirmDeleteCompany').on('click', function() {
        const companyId = $(this).data('company-id'); // Pobierz ID firmy z atrybutu data
        console.log("Delete company confirmed for ID:", companyId); // Debug

        // Wysyłanie żądania POST do endpointu usuwania firmy
        $.ajax({
            url: `/company/${companyId}/delete`, // Endpoint usuwania
            type: 'POST', // Metoda POST (zalecane dla akcji usuwania)
            success: function(response) {
                // Obsługa odpowiedzi sukcesu z backendu
                if (response.success) {
                    $('#deleteCompanyModal').modal('hide'); // Ukryj modal
                    alert('Firma została usunięta pomyślnie!'); // Pokaż komunikat sukcesu
                    // Przekieruj użytkownika na stronę główną lub inną po usunięciu
                    window.location.href = response.redirect;
                } else {
                    // Obsługa odpowiedzi błędu z backendu
                    $('#deleteCompanyModal').modal('hide'); // Ukryj modal
                    alert('Wystąpił błąd podczas usuwania: ' + (response.error || 'Nieznany błąd')); // Pokaż komunikat błędu
                     console.error("Delete company backend error:", response.error); // Debug
                }
            },
            error: function(xhr) {
                // Obsługa błędów komunikacji AJAX (np. 404, 500)
                $('#deleteCompanyModal').modal('hide'); // Ukryj modal
                let errorMessage = 'Wystąpił błąd podczas komunikacji z serwerem podczas usuwania firmy.';
                 try {
                     const responseJson = JSON.parse(xhr.responseText);
                     if (responseJson && responseJson.error) {
                         errorMessage = 'Wystąpił błąd: ' + responseJson.error;
                     } else {
                          errorMessage += ' (Status: ' + xhr.status + ')';
                     }
                 } catch (e) {
                      errorMessage += ' (Status: ' + xhr.status + ')';
                      console.error("Error parsing delete error response:", e); // Debug
                 }
                alert(errorMessage); // Pokaż komunikat błędu
                 console.error("Delete company AJAX error:", xhr.status, xhr.responseText); // Debug
            }
        });
    });

    // Removed the problematic form submit handler - Walidacja i wysyłka formularza głównego jest teraz obsługiwana przez Flask/WTForms


    // --- Inny kod JS specyficzny dla tego formularza, który nie pasuje do powyższych sekcji... ---
    // Jeśli miałeś inny kod JS na końcu oryginalnego company_form.js, umieść go tutaj,
    // wewnątrz tego głównego bloku $(document).ready.


}); // Koniec JEDYNEGO i głównego $(document).ready