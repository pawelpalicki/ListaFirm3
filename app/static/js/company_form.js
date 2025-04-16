$(document).ready(function() {
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
    //Analogicznie dla telefonów, osób i ocen
    // Aktualizacja listy powiatów po zmianie województwa
    $('#wojewodztwa-select').change(function() {
        const wojewodztwoId = $(this).val();
        if (wojewodztwoId) {
            $.getJSON(`/api/powiaty/${wojewodztwoId}`, function(data) {
                const powiatSelect = $('#powiaty-select');
                powiatSelect.empty();
                powiatSelect.append('<option value="">Wybierz powiat</option>');
                $.each(data, function(i, item) {
                    powiatSelect.append($('<option>').attr('value', item.id).text(item.name));
                });
            });
        } else {
            $('#powiaty-select').empty().append('<option value="">Wybierz powiat</option>');
        }
    });

    // Dodawanie województwa do kontenera
    $('#dodaj-wojewodztwo').click(function() {
        $('#wojewodztwa-select option:selected').each(function() {
            const wojewodztwoId = $(this).val();
            const wojewodztwoName = $(this).text();
            $('#wybrane-obszary').append(`<span class="badge bg-primary m-1" data-id="${wojewodztwoId}">${wojewodztwoName} <button type="button" class="btn-close" aria-label="Usuń"></button></span>`);
        });
        aktualizujUkrytePola();
    });

    // Dodawanie powiatu do kontenera
    $('#dodaj-powiat').click(function() {
        $('#powiaty-select option:selected').each(function() {
            const powiatId = $(this).val();
            const powiatName = $(this).text();
            $('#wybrane-obszary').append(`<span class="badge bg-success m-1" data-id="${powiatId}">${powiatName} <button type="button" class="btn-close" aria-label="Usuń"></button></span>`);
        });
        aktualizujUkrytePola();
    });

    // Usuwanie wybranego obszaru
    $(document).on('click', '.btn-close', function() {
        $(this).parent().remove();
        aktualizujUkrytePola();
    });

    // Aktualizacja ukrytych pól z wybranymi ID
    function aktualizujUkrytePola() {
        const wojewodztwaIds = [];
        const powiatyIds = [];
        $('#wybrane-obszary span').each(function() {
            const id = $(this).data('id');
            if ($(this).hasClass('bg-primary')) {
                wojewodztwaIds.push(id);
            } else if ($(this).hasClass('bg-success')) {
                powiatyIds.push(id);
            }
        });
        $('#wojewodztwa-input').val(wojewodztwaIds.join(','));
        $('#powiaty-input').val(powiatyIds.join(','));
    }
});
