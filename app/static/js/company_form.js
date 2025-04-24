$(document).ready(function() {
    // Obsługa dynamicznie dodawanych elementów formularza

    $('#dodaj-adres').click(function() {
        var adresyContainer = $('#adresy-container');
        var index = adresyContainer.children('.adres-form').length;
        var newElement = $(`
            <div class="adres-form mb-3 p-3 border rounded">
                <div class="row">
                    <div class="col-md-4 mb-2">
                        <label class="form-label">Typ adresu</label>
                        <select class="form-select" name="adresy-${index}-typ_adresu"></select>
                    </div>
                </div>
                <div class="row">
                    <div class="col-md-2 mb-2">
                        <label class="form-label">Kod</label>
                        <input type="text" class="form-control" name="adresy-${index}-kod">
                    </div>
                    <div class="col-md-4 mb-2">
                        <label class="form-label">Miejscowość</label>
                        <input type="text" class="form-control" name="adresy-${index}-miejscowosc">
                    </div>
                    <div class="col-md-6 mb-2">
                        <label class="form-label">Ulica/Miejscowość</label>
                        <input type="text" class="form-control" name="adresy-${index}-ulica_miejscowosc">
                    </div>
                </div>
            </div>
        `);

        adresyContainer.append(newElement);

        // Inicjalizuj Select2 dla nowego adresu
        Select2Config.initializeDynamicElement(newElement);
    });

    $('#dodaj-telefon').click(function() {
        var telefonyContainer = $('#telefony-container');
        var index = telefonyContainer.children('.telefon-form').length;
        var newElement = $(`
            <div class="telefon-form mb-3 p-3 border rounded">
                <div class="row">
                    <div class="col-md-12 mb-2">
                        <label class="form-label">Typ telefonu</label>
                        <select class="form-select" name="telefony-${index}-typ_telefonu"></select>
                    </div>
                    <div class="col-md-12 mb-2">
                        <label class="form-label">Telefon</label>
                        <input type="text" class="form-control" name="telefony-${index}-telefon">
                    </div>
                </div>
            </div>
        `);

        telefonyContainer.append(newElement);

        // Inicjalizuj Select2 dla nowego telefonu
        Select2Config.initializeDynamicElement(newElement);
    });

    $('#dodaj-email').click(function() {
        var emaileContainer = $('#emaile-container');
        var index = emaileContainer.children('.email-form').length;
        var newElement = $(`
            <div class="email-form mb-3 p-3 border rounded">
                <div class="row">
                    <div class="col-md-12 mb-2">
                        <label class="form-label">Typ e-maila</label>
                        <select class="form-select" name="emaile-${index}-typ_emaila"></select>
                    </div>
                    <div class="col-md-12 mb-2">
                        <label class="form-label">E-mail</label>
                        <input type="email" class="form-control" name="emaile-${index}-email">
                    </div>
                </div>
            </div>
        `);

        emaileContainer.append(newElement);

        // Inicjalizuj Select2 dla nowego emaila
        Select2Config.initializeDynamicElement(newElement);
    });

    $('#dodaj-osobe').click(function() {
        var osobyContainer = $('#osoby-container');
        var index = osobyContainer.children('.osoba-form').length;
        var newElement = $(`
            <div class="osoba-form mb-4 p-3 border rounded">
                <div class="row">
                    <div class="col-md-6 mb-2">
                        <label class="form-label">Imię</label>
                        <input type="text" class="form-control" name="osoby-${index}-imie">
                    </div>
                    <div class="col-md-6 mb-2">
                        <label class="form-label">Nazwisko</label>
                        <input type="text" class="form-control" name="osoby-${index}-nazwisko">
                    </div>
                </div>
                <div class="row">
                    <div class="col-md-6 mb-2">
                        <label class="form-label">Stanowisko</label>
                        <input type="text" class="form-control" name="osoby-${index}-stanowisko">
                    </div>
                </div>
                <div class="row">
                    <div class="col-md-6 mb-2">
                        <label class="form-label">Email</label>
                        <input type="email" class="form-control" name="osoby-${index}-email">
                    </div>
                    <div class="col-md-6 mb-2">
                        <label class="form-label">Telefon</label>
                        <input type="text" class="form-control" name="osoby-${index}-telefon">
                    </div>
                </div>
            </div>
        `);

        osobyContainer.append(newElement);
    });

    $('#dodaj-ocene').click(function() {
        var ocenyContainer = $('#oceny-container');
        var index = ocenyContainer.children('.ocena-form').length;
        var newElement = $(`
            <div class="ocena-form mb-4 p-3 border rounded">
                <div class="row">
                    <div class="col-md-6 mb-2">
                        <label class="form-label">Osoba oceniająca</label>
                        <input type="text" class="form-control" name="oceny-${index}-osoba_oceniajaca">
                    </div>
                    <div class="col-md-6 mb-2">
                        <label class="form-label">Budowa/Dział</label>
                        <input type="text" class="form-control" name="oceny-${index}-budowa_dzial">
                    </div>
                </div>
                <div class="row">
                    <div class="col-md-6 mb-2">
                        <label class="form-label">Rok współpracy</label>
                        <input type="text" class="form-control" name="oceny-${index}-rok_wspolpracy">
                    </div>
                    <div class="col-md-6 mb-2">
                        <label class="form-label">Ocena</label>
                        <input type="text" class="form-control" name="oceny-${index}-ocena">
                    </div>
                </div>
                <div class="mb-2">
                    <label class="form-label">Komentarz</label>
                    <textarea class="form-control" name="oceny-${index}-komentarz" rows="2"></textarea>
                </div>
            </div>
        `);

        ocenyContainer.append(newElement);
    });


    // Obsługa zmiany województw dla formularza firmy
    $('#wojewodztwa').on('change', function() {
        loadPowiaty();
    });

    // Funkcja do ładowania powiatów na podstawie wybranych województw
    function loadPowiaty() {
        const selectedWojewodztwa = $('#wojewodztwa').val();

        if (selectedWojewodztwa && selectedWojewodztwa.length > 0) {
            // Zachowujemy aktualny wybór powiatów przed aktualizacją
            const currentSelection = $('#powiaty').val() || [];

            // Reset opcji
            const powiatySelect = $('#powiaty');
            powiatySelect.empty();

            // Iterujemy przez wszystkie wybrane województwa
            selectedWojewodztwa.forEach(function(wojewodztwo) {
                $.getJSON(`/api/powiaty/${wojewodztwo}`, function(data) {
                    // Dodajemy nowe opcje
                    $.each(data, function(i, item) {
                        powiatySelect.append($('<option>').attr('value', item.id).text(item.name));
                    });

                    // Przywracamy poprzedni wybór (jeśli powiaty nadal istnieją w nowym województwie)
                    powiatySelect.val(currentSelection).trigger('change');
                });
            });
        }
    }


    // Zapisz dane województw i powiatów do ukrytych pól podczas submitu
    $('form').on('submit', function() {
        $('#wojewodztwa-input').val(JSON.stringify($('#wojewodztwa').val() || []));
        $('#powiaty-input').val(JSON.stringify($('#powiaty').val() || []));
    });
});