$(document).ready(function() {
    // Funkcja do tworzenia tabeli, jeśli jeszcze nie istnieje
    function createTableIfNotExists(containerId, headersArray) {
        const tableId = containerId + '-table';
        if ($('#' + tableId).length === 0) {
            // Tworzymy kontener dla tabeli z klasą "responsive-table-container"
            const tableContainer = $('<div class="table-responsive mt-3 mb-3 responsive-table-container"></div>');

            // Tworzymy tabelę z dodatkową klasą "responsive-table"
            const table = $('<table class="table table-sm table-hover table-borderless responsive-table"></table>').attr('id', tableId);

            // Tworzymy nagłówek tabeli
            const thead = $('<thead class="table-light"></thead>');
            const headerRow = $('<tr></tr>');

            // Dodajemy nagłówki z dodatkowymi atrybutami data-label
            headersArray.forEach(header => {
                headerRow.append($('<th></th>').text(header).attr('data-column', header));
            });

            // Dodajemy kolumnę na akcje
            headerRow.append($('<th>Akcje</th>').attr('data-column', 'Akcje'));

            thead.append(headerRow);
            table.append(thead);

            // Dodajemy tbody
            table.append($('<tbody></tbody>'));

            // Dodajemy tabelę do kontenera, a kontener umieszczamy bezpośrednio po formularzu
            tableContainer.append(table);
            $('#' + containerId).after(tableContainer);

            // Dodajemy mobilną wersję tabeli (ukryta domyślnie)
            const mobileContainer = $('<div class="mobile-cards-container d-none"></div>').attr('id', tableId + '-mobile');
            $('#' + containerId).after(mobileContainer);
        }
    }

    // Funkcja do dodawania wiersza do tabeli
    function addRowToTable(tableId, dataArray, rawDataObj) {
        const tbody = $('#' + tableId + ' tbody');
        const row = $('<tr></tr>');
        const headersArray = [];

        // Zbieramy nagłówki
        $('#' + tableId + ' thead th').each(function() {
            headersArray.push($(this).attr('data-column'));
        });

        // Dodajemy dane z atrybutami data-label
        dataArray.forEach((data, index) => {
            if (index < headersArray.length - 1) { // Pomijamy ostatnią kolumnę (Akcje)
                row.append($('<td></td>').text(data).attr('data-label', headersArray[index]));
            }
        });

        // Dodajemy przyciski akcji
        const actionCell = $('<td></td>').attr('data-label', 'Akcje');
        const editButton = $('<button class="btn btn-sm btn-outline-primary action-btn edit-btn me-1"><i class="bi bi-pencil"></i> <span class="btn-text">Modyfikuj</span></button>');
        const deleteButton = $('<button class="btn btn-sm btn-outline-danger action-btn delete-btn"><i class="bi bi-trash"></i> <span class="btn-text">Usuń</span></button>');

        // Dodajemy surowe dane jako atrybut row
        if (rawDataObj) {
            row.data('raw-data', rawDataObj);
        }

        // Obsługa przycisku edycji
        editButton.click(function() {
            const rawData = $(this).closest('tr').data('raw-data');
            editRow(tableId, rawData, $(this).closest('tr'));
        });

        // Obsługa przycisku usuwania
        deleteButton.click(function() {
            const rowElement = $(this).closest('tr');
            const cardElement = $('#' + tableId + '-mobile .mobile-card[data-row-id="' + rowElement.attr('data-row-id') + '"]');

            // Usuwamy wiersz z tabeli i odpowiadającą kartę z widoku mobilnego
            rowElement.remove();
            cardElement.remove();
        });

        actionCell.append(editButton).append(deleteButton);
        row.append(actionCell);

        // Dodajemy unikalny identyfikator wiersza
        const rowId = 'row-' + Date.now() + '-' + Math.floor(Math.random() * 1000);
        row.attr('data-row-id', rowId);

        tbody.append(row);

        // Dodajemy odpowiadającą kartę dla widoku mobilnego
        addMobileCard(tableId, dataArray, headersArray, rawDataObj, rowId);
    }

    // Funkcja do tworzenia karty mobilnej
    function addMobileCard(tableId, dataArray, headersArray, rawDataObj, rowId) {
        const mobileContainer = $('#' + tableId + '-mobile');
        const card = $('<div class="card mb-3 mobile-card"></div>').attr('data-row-id', rowId);
        const cardBody = $('<div class="card-body p-3"></div>');

        // Dodajemy zawartość karty
        for (let i = 0; i < dataArray.length && i < headersArray.length - 1; i++) {
            const headerLabel = $('<strong></strong>').text(headersArray[i] + ': ');
            const dataSpan = $('<span></span>').text(dataArray[i]);
            const dataLine = $('<div class="mb-1"></div>').append(headerLabel).append(dataSpan);
            cardBody.append(dataLine);
        }

        // Dodajemy przyciski akcji
        const actionDiv = $('<div class="d-flex justify-content-end mt-2"></div>');
        const editButton = $('<button class="btn btn-sm btn-outline-primary me-1"><i class="bi bi-pencil"></i> Modyfikuj</button>');
        const deleteButton = $('<button class="btn btn-sm btn-outline-danger"><i class="bi bi-trash"></i> Usuń</button>');

        // Dodajemy surowe dane jako atrybut karty
        if (rawDataObj) {
            card.data('raw-data', rawDataObj);
        }

        // Obsługa przycisku edycji
        editButton.click(function() {
            const rawData = $(this).closest('.mobile-card').data('raw-data');
            const rowElement = $('#' + tableId + ' tr[data-row-id="' + rowId + '"]');
            editRow(tableId, rawData, rowElement);
            $(this).closest('.mobile-card').remove();
        });

        // Obsługa przycisku usuwania
        deleteButton.click(function() {
            const cardElement = $(this).closest('.mobile-card');
            const rowElement = $('#' + tableId + ' tr[data-row-id="' + cardElement.attr('data-row-id') + '"]');

            // Usuwamy wiersz z tabeli i kartę z widoku mobilnego
            cardElement.remove();
            rowElement.remove();
        });

        actionDiv.append(editButton).append(deleteButton);
        cardBody.append(actionDiv);
        card.append(cardBody);
        mobileContainer.append(card);
    }

    // Funkcja do edycji wiersza
    function editRow(tableId, rawData, rowElement) {
        // Identyfikujemy, który formularz edytujemy na podstawie ID tabeli
        let formPrefix = '';
        let containerSelector = '';

        if (tableId === 'adresy-container-table') {
            formPrefix = 'adresy';
            containerSelector = '#adresy-container';
        } else if (tableId === 'telefony-container-table') {
            formPrefix = 'telefony';
            containerSelector = '#telefony-container';
        } else if (tableId === 'emaile-container-table') {
            formPrefix = 'emaile';
            containerSelector = '#emaile-container';
        } else if (tableId === 'osoby-container-table') {
            formPrefix = 'osoby';
            containerSelector = '#osoby-container';
        } else if (tableId === 'oceny-container-table') {
            formPrefix = 'oceny';
            containerSelector = '#oceny-container';
        }

        // Wypełniamy formularz danymi z raw-data
        if (rawData) {
            // Iterujemy przez wszystkie pola w formularzu
            $(containerSelector + ' .form-control, ' + containerSelector + ' .form-select').each(function() {
                const inputName = $(this).attr('name');
                if (inputName && rawData[inputName]) {
                    if ($(this).is('select')) {
                        $(this).val(rawData[inputName]).trigger('change');
                    } else {
                        $(this).val(rawData[inputName]);
                    }
                }
            });
        }

        // Usuwamy wiersz z tabeli i odpowiadającą kartę z widoku mobilnego
        const rowId = rowElement.attr('data-row-id');
        rowElement.remove();
        $('#' + tableId + '-mobile .mobile-card[data-row-id="' + rowId + '"]').remove();
    }

    // Funkcja do czyszczenia formularza
    function clearForm(containerSelector) {
        $(containerSelector + ' .form-control, ' + containerSelector + ' .form-select').each(function() {
            if ($(this).is('select')) {
                $(this).val('').trigger('change');
            } else {
                $(this).val('');
            }
        });
    }

    // Funkcja do zbierania danych z formularza
    function collectFormData(containerSelector, formPrefix) {
        const data = {};
        const displayData = [];

        // Iterujemy przez wszystkie pola w formularzu
        $(containerSelector + ' .form-control, ' + containerSelector + ' .form-select').each(function() {
            const inputName = $(this).attr('name');
            const value = $(this).val();

            // Zapisujemy wartość do obiektu
            if (inputName) {
                data[inputName] = value;

                // Dla select, pobieramy tekst wybranej opcji
                if ($(this).is('select') && value) {
                    displayData.push($(this).find('option:selected').text());
                } else {
                    displayData.push(value);
                }
            }
        });

        return {
            rawData: data,
            displayData: displayData
        };
    }

    // Obsługa dodawania adresu
    $('#dodaj-adres').click(function() {
        var adresyContainer = $('#adresy-container');

        // Pobieramy dane z formularza
        const formData = collectFormData('#adresy-container', 'adresy');
        const typAdresu = adresyContainer.find('select[name^="adresy"][name$="typ_adresu"]').val();
        const kod = adresyContainer.find('input[name^="adresy"][name$="kod"]').val();
        const miejscowosc = adresyContainer.find('input[name^="adresy"][name$="miejscowosc"]').val();
        const ulicaMiejscowosc = adresyContainer.find('input[name^="adresy"][name$="ulica_miejscowosc"]').val();

        // Pobieramy tekst wybranej opcji dla typu adresu
        const typAdresuText = typAdresu ? adresyContainer.find('select[name^="adresy"][name$="typ_adresu"] option:selected').text() : '';

        if (!typAdresu || !miejscowosc) {
            alert('Wypełnij przynajmniej pole "Typ adresu" i "Miejscowość"');
            return;
        }

        // Tworzymy tabelę, jeśli nie istnieje
        createTableIfNotExists('adresy-container', ['Typ adresu', 'Kod', 'Miejscowość', 'Ulica/Miejscowość']);

        // Dodajemy dane do tabeli
        addRowToTable('adresy-container-table', [typAdresuText, kod, miejscowosc, ulicaMiejscowosc], formData.rawData);

        // Czyścimy formularz
        clearForm('#adresy-container');
    });

    // Obsługa dodawania telefonu
    $('#dodaj-telefon').click(function() {
        var telefonyContainer = $('#telefony-container');

        // Pobieramy dane z formularza
        const formData = collectFormData('#telefony-container', 'telefony');
        const typTelefonu = telefonyContainer.find('select[name^="telefony"][name$="typ_telefonu"]').val();
        const telefon = telefonyContainer.find('input[name^="telefony"][name$="telefon"]').val();

        // Pobieramy tekst wybranej opcji dla typu telefonu
        const typTelefonuText = typTelefonu ? telefonyContainer.find('select[name^="telefony"][name$="typ_telefonu"] option:selected').text() : '';

        if (!typTelefonu || !telefon) {
            alert('Wypełnij pola "Typ telefonu" i "Telefon"');
            return;
        }

        // Tworzymy tabelę, jeśli nie istnieje
        createTableIfNotExists('telefony-container', ['Typ telefonu', 'Telefon']);

        // Dodajemy dane do tabeli
        addRowToTable('telefony-container-table', [typTelefonuText, telefon], formData.rawData);

        // Czyścimy formularz
        clearForm('#telefony-container');
    });

    // Obsługa dodawania emaila
    $('#dodaj-email').click(function() {
        var emaileContainer = $('#emaile-container');

        // Pobieramy dane z formularza
        const formData = collectFormData('#emaile-container', 'emaile');
        const typEmaila = emaileContainer.find('select[name^="emaile"][name$="typ_emaila"]').val();
        const email = emaileContainer.find('input[name^="emaile"][name$="email"]').val();

        // Pobieramy tekst wybranej opcji dla typu emaila
        const typEmailaText = typEmaila ? emaileContainer.find('select[name^="emaile"][name$="typ_emaila"] option:selected').text() : '';

        if (!typEmaila || !email) {
            alert('Wypełnij pola "Typ e-maila" i "E-mail"');
            return;
        }

        // Tworzymy tabelę, jeśli nie istnieje
        createTableIfNotExists('emaile-container', ['Typ e-maila', 'E-mail']);

        // Dodajemy dane do tabeli
        addRowToTable('emaile-container-table', [typEmailaText, email], formData.rawData);

        // Czyścimy formularz
        clearForm('#emaile-container');
    });

    // Obsługa dodawania osoby
    $('#dodaj-osobe').click(function() {
        var osobyContainer = $('#osoby-container');

        // Pobieramy dane z formularza
        const formData = collectFormData('#osoby-container', 'osoby');
        const imie = osobyContainer.find('input[name^="osoby"][name$="imie"]').val();
        const nazwisko = osobyContainer.find('input[name^="osoby"][name$="nazwisko"]').val();
        const stanowisko = osobyContainer.find('input[name^="osoby"][name$="stanowisko"]').val();
        const email = osobyContainer.find('input[name^="osoby"][name$="email"]').val();
        const telefon = osobyContainer.find('input[name^="osoby"][name$="telefon"]').val();

        if (!imie || !nazwisko) {
            alert('Wypełnij przynajmniej pola "Imię" i "Nazwisko"');
            return;
        }

        // Tworzymy tabelę, jeśli nie istnieje
        createTableIfNotExists('osoby-container', ['Imię', 'Nazwisko', 'Stanowisko', 'Email', 'Telefon']);

        // Dodajemy dane do tabeli
        addRowToTable('osoby-container-table', [imie, nazwisko, stanowisko, email, telefon], formData.rawData);

        // Czyścimy formularz
        clearForm('#osoby-container');
    });

    // Obsługa dodawania oceny
    $('#dodaj-ocene').click(function() {
        var ocenyContainer = $('#oceny-container');

        // Pobieramy dane z formularza
        const formData = collectFormData('#oceny-container', 'oceny');
        const osobaOceniajaca = ocenyContainer.find('input[name^="oceny"][name$="osoba_oceniajaca"]').val();
        const budowaDzial = ocenyContainer.find('input[name^="oceny"][name$="budowa_dzial"]').val();
        const rokWspolpracy = ocenyContainer.find('input[name^="oceny"][name$="rok_wspolpracy"]').val();
        const ocena = ocenyContainer.find('input[name^="oceny"][name$="ocena"]').val();
        const komentarz = ocenyContainer.find('textarea[name^="oceny"][name$="komentarz"]').val();

        if (!osobaOceniajaca || !ocena) {
            alert('Wypełnij przynajmniej pola "Osoba oceniająca" i "Ocena"');
            return;
        }

        // Tworzymy tabelę, jeśli nie istnieje
        createTableIfNotExists('oceny-container', ['Osoba oceniająca', 'Budowa/Dział', 'Rok współpracy', 'Ocena', 'Komentarz']);

        // Dodajemy dane do tabeli
        addRowToTable('oceny-container-table', [osobaOceniajaca, budowaDzial, rokWspolpracy, ocena, komentarz], formData.rawData);

        // Czyścimy formularz
        clearForm('#oceny-container');
    });

    // Dodajemy funkcję do przełączania widoku na podstawie szerokości ekranu
    function handleResponsiveTables() {
        const windowWidth = $(window).width();

        if (windowWidth < 768) { // Breakpoint dla urządzeń mobilnych
            $('.responsive-table-container').addClass('d-none');
            $('.mobile-cards-container').removeClass('d-none');
        } else {
            $('.responsive-table-container').removeClass('d-none');
            $('.mobile-cards-container').addClass('d-none');
        }
    }

    // Wywołujemy przy załadowaniu strony
    handleResponsiveTables();

    // Nasłuchujemy na zmianę rozmiaru okna
    $(window).resize(function() {
        handleResponsiveTables();
    });

    // Pozostała część kodu (obsługa województw i powiatów) pozostaje bez zmian
    $('#wojewodztwa').on('change', function() {
        loadPowiaty();
    });

    function loadPowiaty() {
        const selectedWojewodztwa = $('#wojewodztwa').val();

        if (selectedWojewodztwa && selectedWojewodztwa.length > 0) {
            const currentSelection = $('#powiaty').val() || [];
            const powiatySelect = $('#powiaty');
            powiatySelect.empty();

            selectedWojewodztwa.forEach(function(wojewodztwo) {
                $.getJSON(`/api/powiaty/${wojewodztwo}`, function(data) {
                    $.each(data, function(i, item) {
                        powiatySelect.append($('<option>').attr('value', item.id).text(item.name));
                    });
                    powiatySelect.val(currentSelection).trigger('change');
                });
            });
        }
    }

    $('form').on('submit', function() {
        $('#wojewodztwa-input').val(JSON.stringify($('#wojewodztwa').val() || []));
        $('#powiaty-input').val(JSON.stringify($('#powiaty').val() || []));

        // Dodajemy obsługę zbierania danych z tabel do formularza przed wysłaniem
        function collectTableData(tableId, containerName) {
            const data = [];
            $('#' + tableId + ' tbody tr').each(function() {
                const rowData = $(this).data('raw-data');
                if (rowData) {
                    data.push(rowData);
                }
            });

            // Dodajemy ukryte pole z danymi z tabeli
            if (data.length > 0) {
                const hiddenInput = $('<input>').attr({
                    type: 'hidden',
                    name: containerName + '_data',
                    value: JSON.stringify(data)
                });
                $(this).append(hiddenInput);
            }
        }

        // Zbieramy dane z wszystkich tabel
        collectTableData('adresy-container-table', 'adresy');
        collectTableData('telefony-container-table', 'telefony');
        collectTableData('emaile-container-table', 'emaile');
        collectTableData('osoby-container-table', 'osoby');
        collectTableData('oceny-container-table', 'oceny');
    });

    // Obsługa wyświetlania formularza overlay
    $('.add-new-option').click(function() {
        const type = $(this).data('type');
        const selectElement = $(this).closest('.input-group').find('select');

        const selectId = selectElement.attr('id');

        // --- Dodane logowanie i sprawdzenie ---
        console.log("Kliknięto 'Dodaj' dla typu:", type);
        console.log("Przycisk:", this);
        console.log("Znaleziony element select:", selectElement);
        console.log("Pobrane ID selecta:", selectId);

        if (!selectId) {
            console.error("Nie udało się znaleźć ID dla elementu select powiązanego z tym przyciskiem 'Dodaj'. Sprawdź selektor jQuery i strukturę HTML.");
            alert("Wystąpił błąd: Nie można zidentyfikować pola docelowego. Sprawdź konsolę deweloperską (F12).");
            return; // Przerwij działanie, jeśli ID nie zostało znalezione
        }
        // --- Koniec dodanego logowania i sprawdzenia ---
        
        // Ustawianie właściwości formularza w zależności od typu
        switch(type) {
            case 'adres_typ':
                $('#overlay-title').text('Dodaj nowy typ adresu');
                $('#overlay-label').text('Nazwa typu adresu');
                break;
            case 'email_typ':
                $('#overlay-title').text('Dodaj nowy typ emaila');
                $('#overlay-label').text('Nazwa typu emaila');
                break;
            case 'telefon_typ':
                $('#overlay-title').text('Dodaj nowy typ telefonu');
                $('#overlay-label').text('Nazwa typu telefonu');
                break;
            case 'firma_typ':
                $('#overlay-title').text('Dodaj nowy typ firmy');
                $('#overlay-label').text('Nazwa typu firmy');
                break;
            case 'specjalnosc':
                $('#overlay-title').text('Dodaj nową specjalność');
                $('#overlay-label').text('Nazwa specjalności');
                break;
        }

        // Zapisanie typu i ID selecta dla późniejszego użycia
        $('#overlay-type').val(type);
        $('#overlay-id').val(selectId); // Ustaw ID tylko jeśli zostało znalezione

        // Czyszczenie formularza i pokazanie overlay
        $('#overlay-input').val('');
        $('#overlay-form-container').removeClass('d-none');
    });

    // Obsługa zamykania formularza overlay
    $('#close-overlay').click(function() {
        $('#overlay-form-container').addClass('d-none');
    });

    // Obsługa wysyłania formularza overlay
    $('#overlay-form').submit(function(e) {
        e.preventDefault();

        const type = $('#overlay-type').val();
        const value = $('#overlay-input').val();
        const selectId = $('#overlay-id').val();

        if (!value.trim()) {
            alert('Proszę wprowadzić wartość');
            return;
        }

        // Określenie endpoint API na podstawie typu
        let apiEndpoint;
        switch(type) {
            case 'adres_typ':
                apiEndpoint = '/api/adres_typ';
                break;
            case 'email_typ':
                apiEndpoint = '/api/email_typ';
                break;
            case 'telefon_typ':
                apiEndpoint = '/api/telefon_typ';
                break;
            case 'firma_typ':
                apiEndpoint = '/api/firma_typ';
                break;
            case 'specjalnosc':
                apiEndpoint = '/api/specjalnosc';
                break;
        }

        // Wysłanie nowej wartości do API
        $.ajax({
            url: apiEndpoint,
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ name: value }),
            success: function(response) {
                // Zamknięcie formularza overlay
                $('#overlay-form-container').addClass('d-none');

                if (type === 'specjalnosc') {
                    const $select = $('#' + selectId); // np. $('#specjalnosci')
                    const newOptionValue = response.id.toString(); // ID nowej opcji jako string
                    const newOptionText = value; // Tekst nowej opcji

                    // --- Krok 1: Dodaj nową opcję do bazowego elementu <select> ---
                    // Sprawdź, czy opcja o tej wartości już nie istnieje
                    if ($select.find("option[value='" + newOptionValue + "']").length === 0) {
                        // Utwórz nową opcję (bez ustawiania selected tutaj)
                        var newOption = new Option(newOptionText, newOptionValue, false, false);
                        // Dodaj ją do <select>
                        $select.append(newOption);
                        console.log("HTML <option> dodany do <select>:", newOptionValue, newOptionText);
                    } else {
                        console.log("Opcja o wartości", newOptionValue, "już istnieje w <select>.");
                    }

                    // --- Krok 2: Pobierz aktualną listę zaznaczonych ID ---
                    // Używamy .val(), które dla Select2 multi-select powinno zwrócić tablicę stringów
                    let currentSelections = $select.val() || [];
                     // Upewnijmy się, że na pewno pracujemy na tablicy
                     if (!Array.isArray(currentSelections)) {
                         currentSelections = currentSelections ? [currentSelections] : [];
                     }
                    console.log("Obecne zaznaczenia (przed dodaniem nowej):", currentSelections);

                    // --- Krok 3: Dodaj ID nowej opcji do listy zaznaczeń ---
                    // Dodaj tylko, jeśli jeszcze nie ma (na wypadek wielokrotnego kliknięcia itp.)
                    if (!currentSelections.includes(newOptionValue)) {
                        currentSelections.push(newOptionValue);
                        console.log("ID nowej opcji dodane do listy zaznaczeń.");
                    } else {
                         console.log("ID nowej opcji już było na liście zaznaczeń.");
                    }

                    // --- Krok 4: Ustaw nową listę zaznaczeń w Select2 i poinformuj o zmianie ---
                    console.log("Ustawianie zaznaczeń w Select2 na:", currentSelections);
                    // Ustawiamy wartość i wywołujemy zdarzenie, aby Select2 odświeżył UI
                    $select.val(currentSelections).trigger('change.select2');
                    console.log("Wywołano trigger 'change.select2'.");

                    // --- Opcjonalny Krok 5: Weryfikacja po chwili ---
                    // Sprawdźmy po krótkim opóźnieniu, czy wartość została poprawnie ustawiona
                    setTimeout(() => {
                         const finalSelections = $select.val();
                         console.log("Zaznaczenia w Select2 po 100ms:", finalSelections);
                         // Porównajmy, czy zawiera nową opcję
                         if (finalSelections && finalSelections.includes(newOptionValue)) {
                            console.log("Weryfikacja: Nowa opcja JEST zaznaczona.");
                         } else {
                            console.warn("Weryfikacja: Nowa opcja NIE JEST zaznaczona.");
                         }
                    }, 100);


                    // Powiadomienie użytkownika
                    alert('Dodano pomyślnie! Nowa specjalność została dodana do listy i zaznaczona.');

                } else {
                     // Standardowa obsługa dla innych typów (bez zmian)
                     const $select = $('#' + selectId);
                     $select.append(new Option(value, response.id, true, true));
                     if ($select.hasClass('select2-hidden-accessible')) {
                        $select.trigger('change');
                     }
                     alert('Dodano pomyślnie!');
                }
            },
            error: function(xhr) {
                // Wyświetl bardziej szczegółowy błąd, jeśli jest dostępny
                let errorMessage = 'Wystąpił błąd.';
                try {
                    // Spróbuj sparsować odpowiedź JSON z serwera
                    const responseJson = JSON.parse(xhr.responseText);
                    // Jeśli zawiera pole 'error', użyj go
                    if (responseJson && responseJson.error) {
                        errorMessage = 'Wystąpił błąd: ' + responseJson.error;
                    }
                } catch (e) {
                    // Ignoruj błąd parsowania, jeśli odpowiedź nie jest JSONem lub jest pusta
                    console.error("Error parsing error response:", e);
                    // Można dodać ogólny komunikat z kodem statusu, np.:
                    // errorMessage = `Wystąpił błąd serwera (status: ${xhr.status})`;
                }
                alert(errorMessage);
            }
        });
    });
    
    // Dodatkowo dodajemy obsługę klawisza Escape do zamykania overlay
    $(document).on('keydown', function(e) {
        if (e.key === 'Escape' && !$('#overlay-form-container').hasClass('d-none')) {
            $('#overlay-form-container').addClass('d-none');
        }
    });

    // Funkcja do dodawania przycisku "Dodaj" dla nowo utworzonego formularza
    function addAddButtonToNewForm(container) {
        // Sprawdzamy, jakiego typu jest kontener i dodajemy odpowiedni przycisk
        if (container.id === 'adresy-container') {
            // Znajdujemy ostatni select typu adresu
            const lastSelect = container.querySelector('select[name$="typ_adresu"]:last-of-type');
            if (lastSelect && !lastSelect.nextElementSibling?.classList.contains('add-new-option')) {
                const button = document.createElement('button');
                button.type = 'button';
                button.className = 'btn btn-outline-secondary add-new-option';
                button.dataset.type = 'adres_typ';
                button.innerHTML = '<i class="bi bi-plus-circle"></i> Dodaj';

                // Tworzymy div dla input-group, jeśli nie istnieje
                const parent = lastSelect.parentElement;
                if (!parent.classList.contains('input-group')) {
                    const inputGroup = document.createElement('div');
                    inputGroup.className = 'input-group';
                    parent.insertBefore(inputGroup, lastSelect);
                    inputGroup.appendChild(lastSelect);
                    inputGroup.appendChild(button);
                } else {
                    parent.appendChild(button);
                }

                // Dodajemy event listener
                button.addEventListener('click', function() {
                    const type = this.dataset.type;
                    const selectElement = this.previousElementSibling;

                    $('#overlay-title').text('Dodaj nowy typ adresu');
                    $('#overlay-label').text('Nazwa typu adresu');
                    $('#overlay-type').val(type);
                    $('#overlay-id').val(selectElement.id);
                    $('#overlay-input').val('');
                    $('#overlay-form-container').removeClass('d-none');
                });
            }
        } else if (container.id === 'emaile-container') {
            // Analogiczna logika dla emaili
            const lastSelect = container.querySelector('select[name$="typ_emaila"]:last-of-type');
            if (lastSelect && !lastSelect.nextElementSibling?.classList.contains('add-new-option')) {
                const button = document.createElement('button');
                button.type = 'button';
                button.className = 'btn btn-outline-secondary add-new-option';
                button.dataset.type = 'email_typ';
                button.innerHTML = '<i class="bi bi-plus-circle"></i> Dodaj';

                const parent = lastSelect.parentElement;
                if (!parent.classList.contains('input-group')) {
                    const inputGroup = document.createElement('div');
                    inputGroup.className = 'input-group';
                    parent.insertBefore(inputGroup, lastSelect);
                    inputGroup.appendChild(lastSelect);
                    inputGroup.appendChild(button);
                } else {
                    parent.appendChild(button);
                }

                button.addEventListener('click', function() {
                    const type = this.dataset.type;
                    const selectElement = this.previousElementSibling;

                    $('#overlay-title').text('Dodaj nowy typ emaila');
                    $('#overlay-label').text('Nazwa typu emaila');
                    $('#overlay-type').val(type);
                    $('#overlay-id').val(selectElement.id);
                    $('#overlay-input').val('');
                    $('#overlay-form-container').removeClass('d-none');
                });
            }
        } else if (container.id === 'telefony-container') {
            // Analogiczna logika dla telefonów
            const lastSelect = container.querySelector('select[name$="typ_telefonu"]:last-of-type');
            if (lastSelect && !lastSelect.nextElementSibling?.classList.contains('add-new-option')) {
                const button = document.createElement('button');
                button.type = 'button';
                button.className = 'btn btn-outline-secondary add-new-option';
                button.dataset.type = 'telefon_typ';
                button.innerHTML = '<i class="bi bi-plus-circle"></i> Dodaj';

                const parent = lastSelect.parentElement;
                if (!parent.classList.contains('input-group')) {
                    const inputGroup = document.createElement('div');
                    inputGroup.className = 'input-group';
                    parent.insertBefore(inputGroup, lastSelect);
                    inputGroup.appendChild(lastSelect);
                    inputGroup.appendChild(button);
                } else {
                    parent.appendChild(button);
                }

                button.addEventListener('click', function() {
                    const type = this.dataset.type;
                    const selectElement = this.previousElementSibling;

                    $('#overlay-title').text('Dodaj nowy typ telefonu');
                    $('#overlay-label').text('Nazwa typu telefonu');
                    $('#overlay-type').val(type);
                    $('#overlay-id').val(selectElement.id);
                    $('#overlay-input').val('');
                    $('#overlay-form-container').removeClass('d-none');
                });
            }
        }
    }

    // Funkcja do wywoływania po dodaniu nowego formularza
    function setupDynamicFormWithAddButton() {
        addAddButtonToNewForm(document.getElementById('adresy-container'));
        addAddButtonToNewForm(document.getElementById('emaile-container'));
        addAddButtonToNewForm(document.getElementById('telefony-container'));
    }

    // Wywoływane po załadowaniu strony i przy każdym dodaniu nowego formularza
    $(document).ready(function() {
        setupDynamicFormWithAddButton();

        // Interceptujemy domyślne funkcje dodawania formularzy
        const originalAddFormFunctions = {
            'dodaj-adres': window.dodajAdres || null,
            'dodaj-email': window.dodajEmail || null,
            'dodaj-telefon': window.dodajTelefon || null
        };

        // Jeśli funkcje istnieją, nadpisujemy je
        if (originalAddFormFunctions['dodaj-adres']) {
            window.dodajAdres = function() {
                originalAddFormFunctions['dodaj-adres']();
                addAddButtonToNewForm(document.getElementById('adresy-container'));
            };
        }

        if (originalAddFormFunctions['dodaj-email']) {
            window.dodajEmail = function() {
                originalAddFormFunctions['dodaj-email']();
                addAddButtonToNewForm(document.getElementById('emaile-container'));
            };
        }

        if (originalAddFormFunctions['dodaj-telefon']) {
            window.dodajTelefon = function() {
                originalAddFormFunctions['dodaj-telefon']();
                addAddButtonToNewForm(document.getElementById('telefony-container'));
            };
        }

        // Alternatywnie, nasłuchujemy na kliknięcia przycisków dodawania formularzy
        $('#dodaj-adres').click(function() {
            // Dajemy trochę czasu na utworzenie formularza
            setTimeout(() => {
                addAddButtonToNewForm(document.getElementById('adresy-container'));
            }, 100);
        });

        $('#dodaj-email').click(function() {
            setTimeout(() => {
                addAddButtonToNewForm(document.getElementById('emaile-container'));
            }, 100);
        });

        $('#dodaj-telefon').click(function() {
            setTimeout(() => {
                addAddButtonToNewForm(document.getElementById('telefony-container'));
            }, 100);
        });
    });
    
});