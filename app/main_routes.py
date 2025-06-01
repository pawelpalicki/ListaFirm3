from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, Response
from flask_login import current_user # Importujemy tylko 'current_user' (do użycia w szablonach/logice)

# WAŻNA UWAGA: Pozostałe Twoje importy są tutaj prawidłowe i powinny pozostać!
# Nie przenoś ich do __init__.py ani nie usuwaj.
from sqlalchemy import or_, and_, func
from app.models import Firmy, FirmyTyp, Adresy, AdresyTyp, Email, EmailTyp, Telefon, TelefonTyp, Specjalnosci, FirmySpecjalnosci, Kraj, Wojewodztwa, Powiaty, FirmyObszarDzialania, Osoby, Oceny
from app import db # Importujesz 'db' z zainicjalizowanej aplikacji
from unidecode import unidecode
from app.forms import CompanyForm, SimplePersonForm, SimpleRatingForm, SpecialtyForm, AddressTypeForm, EmailTypeForm, PhoneTypeForm, CompanyTypeForm
from sqlalchemy.exc import SQLAlchemyError

main = Blueprint('main', __name__)

# --- GLOBALNA AUTORYZACJA DLA BLUEPRINTU 'main' ---
@main.before_request
def require_login_for_main_blueprint():
    # Sprawdź, czy użytkownik nie jest zalogowany.
    if not current_user.is_authenticated:
        # Sprawdź, czy aktualny endpoint należy do blueprintu 'auth'
        # (czyli jest to strona logowania/wylogowania)
        # lub jest to plik statyczny (np. CSS, JS, obrazki).
        # Te strony muszą być dostępne publicznie.
        if request.endpoint and (
            request.endpoint == 'auth.login' or
            request.endpoint == 'auth.logout' or
            request.endpoint == 'static'
        ):
            return # Pozwól na dostęp do tych endpointów bez logowania.

        # Dla wszystkich innych endpointów w tym blueprincie,
        # jeśli użytkownik nie jest zalogowany, przekieruj go na stronę logowania.
        # Flask-Login automatycznie doda parametr 'next' do URL-a.
        flash("Musisz się zalogować, aby uzyskać dostęp do tej strony.", "warning")
        return redirect(url_for('auth.login', next=request.url))

@main.route('/')
def index():
    query = Firmy.query

    # Handle search filter
    search = request.args.get('search', '')
    if search:
        # Normalizacja tekstu wyszukiwania - usuwanie znaków specjalnych
        normalized_search = ''.join(c for c in search if c.isalnum() or c.isspace())

        # Lista do przechowywania ID firm, które pasują do kryteriów wyszukiwania
        matching_company_ids = set()

        # Funkcja normalizująca tekst
        def normalize_text(text):
            if text is None:
                return ""
            # Usuwanie znaków specjalnych i normalizacja do ASCII
            text = str(text)
            normalized = unidecode(text).lower()  # konwersja do ASCII i małych liter
            return ''.join(c for c in normalized if c.isalnum() or c.isspace())

        # Wyszukiwanie w tabeli FIRMY
        firmy_results = Firmy.query.all()
        for firma in firmy_results:
            if (normalized_search in normalize_text(firma.nazwa_firmy).lower() or
                normalized_search in normalize_text(firma.strona_www).lower() or
                normalized_search in normalize_text(firma.uwagi).lower()):
                matching_company_ids.add(firma.id_firmy)

        # Wyszukiwanie w tabeli ADRESY
        adres_results = Adresy.query.all()
        for adres in adres_results:
            if (normalized_search in normalize_text(adres.kod).lower() or
                normalized_search in normalize_text(adres.miejscowosc).lower() or
                normalized_search in normalize_text(adres.ulica_miejscowosc).lower()):
                if adres.id_firmy:
                    matching_company_ids.add(adres.id_firmy)

        # Wyszukiwanie w tabeli EMAIL
        email_results = Email.query.all()
        for email in email_results:
            if normalized_search in normalize_text(email.e_mail).lower():
                if email.id_firmy:
                    matching_company_ids.add(email.id_firmy)

        # Wyszukiwanie w tabeli TELEFON
        telefon_results = Telefon.query.all()
        for telefon in telefon_results:
            if normalized_search in normalize_text(telefon.telefon).lower():
                if telefon.id_firmy:
                    matching_company_ids.add(telefon.id_firmy)

        # Wyszukiwanie w tabeli OSOBY
        osoby_results = Osoby.query.all()
        for osoba in osoby_results:
            if (normalized_search in normalize_text(osoba.imie).lower() or
                normalized_search in normalize_text(osoba.nazwisko).lower() or
                normalized_search in normalize_text(osoba.stanowisko).lower() or
                normalized_search in normalize_text(osoba.e_mail).lower() or
                normalized_search in normalize_text(osoba.telefon).lower()):
                if osoba.id_firmy:
                    matching_company_ids.add(osoba.id_firmy)

        # Wyszukiwanie w tabeli OCENY
        oceny_results = Oceny.query.all()
        for ocena in oceny_results:
            if (normalized_search in normalize_text(ocena.osoba_oceniajaca).lower() or
                normalized_search in normalize_text(ocena.budowa_dzial).lower() or
                normalized_search in normalize_text(ocena.komentarz).lower()):
                if ocena.id_firmy:
                    matching_company_ids.add(ocena.id_firmy)

        # Wyszukiwanie w tabeli SPECJALNOSCI (przez relację)
        specjalnosci_results = Specjalnosci.query.all()
        for spec in specjalnosci_results:
            if normalized_search in normalize_text(spec.specjalnosc).lower():
                firmy_spec = FirmySpecjalnosci.query.filter_by(id_specjalnosci=spec.id_specjalnosci).all()
                for fs in firmy_spec:
                    matching_company_ids.add(fs.id_firmy)

        # Wyszukiwanie po typie firmy
        firmy_typ_results = FirmyTyp.query.all()
        for typ in firmy_typ_results:
            if normalized_search in normalize_text(typ.typ_firmy).lower():
                firmy_by_typ = Firmy.query.filter_by(id_firmy_typ=typ.id_firmy_typ).all()
                for firma in firmy_by_typ:
                    matching_company_ids.add(firma.id_firmy)

        # Wyszukiwanie po obszarze działania (województwa, powiaty, kraj)
        wojewodztwa_results = Wojewodztwa.query.all()
        for woj in wojewodztwa_results:
            if normalized_search in normalize_text(woj.wojewodztwo).lower():
                firmy_woj = FirmyObszarDzialania.query.filter_by(id_wojewodztwa=woj.id_wojewodztwa).all()
                for fw in firmy_woj:
                    matching_company_ids.add(fw.id_firmy)

        powiaty_results = Powiaty.query.all()
        for pow in powiaty_results:
            if normalized_search in normalize_text(pow.powiat).lower():
                firmy_pow = FirmyObszarDzialania.query.filter_by(id_powiaty=pow.id_powiaty).all()
                for fp in firmy_pow:
                    matching_company_ids.add(fp.id_firmy)

        kraje_results = Kraj.query.all()
        for kraj in kraje_results:
            if normalized_search in normalize_text(kraj.kraj).lower():
                firmy_kraj = FirmyObszarDzialania.query.filter_by(id_kraj=kraj.id_kraj).all()
                for fk in firmy_kraj:
                    matching_company_ids.add(fk.id_firmy)

        # Filtrowanie głównego zapytania, aby zawierało tylko firmy pasujące do wyszukiwania
        if matching_company_ids:
            query = query.filter(Firmy.id_firmy.in_(matching_company_ids))
        else:
            # Jeśli nie znaleziono dopasowań, zwróć pustą listę
            query = query.filter(False)

    # Handle specialty filter
    specialties = request.args.getlist('specialties')
    if specialties:
        query = query.join(FirmySpecjalnosci)\
                    .filter(FirmySpecjalnosci.id_specjalnosci.in_(specialties))

    # Handle area filter
    wojewodztwo = request.args.get('wojewodztwo')
    powiat = request.args.get('powiat')

    if powiat:
        # Include companies with nationwide service
        nationwide_companies = db.session.query(Firmy.id_firmy)\
                                .join(FirmyObszarDzialania)\
                                .filter(FirmyObszarDzialania.id_kraj == 'POL')

        # Get powiat data to find its wojewodztwo
        powiat_data = Powiaty.query.filter_by(id_powiaty=powiat).first()

        if powiat_data:
            wojewodztwo_id = powiat_data.id_wojewodztwa

            # Companies serving the specific powiat
            powiat_companies = db.session.query(Firmy.id_firmy)\
                                .join(FirmyObszarDzialania)\
                                .filter(FirmyObszarDzialania.id_powiaty == powiat)

            # Companies serving the whole wojewodztwo (with empty powiat fields)
            wojewodztwo_empty_powiat_companies = db.session.query(Firmy.id_firmy)\
                                    .join(FirmyObszarDzialania)\
                                    .filter(
                                        and_(
                                            FirmyObszarDzialania.id_wojewodztwa == wojewodztwo_id,
                                            FirmyObszarDzialania.id_powiaty == 0
                                        )
                                    )

            # Combine all relevant companies
            combined_companies = nationwide_companies.union(
                powiat_companies, 
                wojewodztwo_empty_powiat_companies
            ).subquery()
        else:
            # If powiat not found, only include nationwide companies
            combined_companies = nationwide_companies.subquery()

        # Apply filter to the main query
        query = query.filter(Firmy.id_firmy.in_(combined_companies))

    elif wojewodztwo and not powiat:
        # Firmy o zasięgu ogólnokrajowym
        nationwide_companies = db.session.query(Firmy.id_firmy)\
                                .join(FirmyObszarDzialania)\
                                .filter(FirmyObszarDzialania.id_kraj == 'POL')

        # Firmy działające tylko na poziomie województwa (bez przypisanych powiatów)
        wojewodztwo_companies = db.session.query(Firmy.id_firmy)\
                                .join(FirmyObszarDzialania)\
                                .filter(FirmyObszarDzialania.id_wojewodztwa == wojewodztwo)\
                                .filter(FirmyObszarDzialania.id_powiaty == 0)\
                                .except_(
                                    # Wykluczenie firm, które mają jakikolwiek wpis z przypisanym powiatem
                                    db.session.query(Firmy.id_firmy)\
                                    .join(FirmyObszarDzialania)\
                                    .filter(FirmyObszarDzialania.id_wojewodztwa == wojewodztwo)\
                                    .filter(FirmyObszarDzialania.id_powiaty != 0))

        # Połączenie zbiorów
        combined_companies = nationwide_companies.union(wojewodztwo_companies).subquery()

        # Filtrowanie głównego zapytania
        query = query.filter(Firmy.id_firmy.in_(combined_companies))


    # Handle company type filter
    company_types = [ct for ct in request.args.getlist('company_types') if ct.strip()]
    if company_types:
        query = query.filter(Firmy.id_firmy_typ.in_(company_types))


    companies = query.all()

    # Get all data needed for filters
    all_specialties = Specjalnosci.query.all()
    all_wojewodztwa = Wojewodztwa.query.all()
    all_powiaty = Powiaty.query.all()
    all_company_types = FirmyTyp.query.all()

    return render_template('index.html', 
                           companies=companies,
                           all_specialties=all_specialties,
                           all_wojewodztwa=all_wojewodztwa,
                           all_powiaty=all_powiaty,
                           all_company_types=all_company_types)

@main.route('/instrukcja')
def instrukcja():
    return render_template('instrukcja.html')

@main.route('/company/<int:company_id>')
def company_details(company_id):
    company = Firmy.query.get_or_404(company_id)

    # Calculate average rating
    avg_rating = db.session.query(func.avg(Oceny.ocena))\
                            .filter(Oceny.id_firmy == company_id)\
                            .scalar() or 0
    avg_rating = round(avg_rating, 1)

    # Get area of operation
    nationwide = db.session.query(FirmyObszarDzialania)\
                            .filter(FirmyObszarDzialania.id_firmy == company_id,
                                    FirmyObszarDzialania.id_kraj == 'POL')\
                            .first() is not None

    wojewodztwa = db.session.query(Wojewodztwa)\
                           .join(FirmyObszarDzialania)\
                           .filter(FirmyObszarDzialania.id_firmy == company_id,
                                   Wojewodztwa.wojewodztwo != 'Nie dotyczy / Brak danych')\
                           .all()

    powiaty = db.session.query(Powiaty, Wojewodztwa.id_wojewodztwa)\
                       .join(FirmyObszarDzialania, Powiaty.id_powiaty == FirmyObszarDzialania.id_powiaty)\
                       .join(Wojewodztwa, Powiaty.id_wojewodztwa == Wojewodztwa.id_wojewodztwa)\
                       .filter(FirmyObszarDzialania.id_firmy == company_id)\
                       .all()

    # Get company specialties
    specialties = db.session.query(Specjalnosci)\
                            .join(FirmySpecjalnosci)\
                            .filter(FirmySpecjalnosci.id_firmy == company_id)\
                            .all()

    # Determine if it's an AJAX request
    is_ajax = request.args.get('ajax', False) # Check for 'ajax=true' in query parameters

    return render_template('company_details.html',
                            company=company,
                            avg_rating=avg_rating,
                            nationwide=nationwide,
                            wojewodztwa=wojewodztwa,
                            powiaty=powiaty,
                            specialties=specialties,
                            standalone=not is_ajax) # Set standalone to False if it's an AJAX request

@main.route('/api/powiaty/<wojewodztwo_id>')
def get_powiaty(wojewodztwo_id):
    powiaty = Powiaty.query.filter_by(id_wojewodztwa=wojewodztwo_id).all()
    return jsonify([{'id': p.id_powiaty, 'name': p.powiat} for p in powiaty])

@main.route('/api/adres_typ', methods=['POST'])
def add_adres_typ():
    data = request.json
    if not data or 'name' not in data:
        return jsonify({'error': 'Brak wymaganych danych'}), 400

    try:
        # Sprawdzamy, czy typ już istnieje
        existing = AdresyTyp.query.filter_by(typ_adresu=data['name']).first()
        if existing:
            return jsonify({'error': 'Ten typ adresu już istnieje', 'id': existing.id_adresy_typ}), 400

        # Dodajemy nowy typ adresu
        new_typ = AdresyTyp(typ_adresu=data['name'])
        db.session.add(new_typ)
        db.session.commit()

        return jsonify({'id': new_typ.id_adresy_typ, 'name': new_typ.typ_adresu}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@main.route('/api/email_typ', methods=['POST'])
def add_email_typ():
    data = request.json
    if not data or 'name' not in data:
        return jsonify({'error': 'Brak wymaganych danych'}), 400

    try:
        # Sprawdzamy, czy typ już istnieje
        existing = EmailTyp.query.filter_by(typ_emaila=data['name']).first()
        if existing:
            return jsonify({'error': 'Ten typ emaila już istnieje', 'id': existing.id_email_typ}), 400

        # Dodajemy nowy typ emaila
        new_typ = EmailTyp(typ_emaila=data['name'])
        db.session.add(new_typ)
        db.session.commit()

        return jsonify({'id': new_typ.id_email_typ, 'name': new_typ.typ_emaila}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@main.route('/api/telefon_typ', methods=['POST'])
def add_telefon_typ():
    data = request.json
    if not data or 'name' not in data:
        return jsonify({'error': 'Brak wymaganych danych'}), 400

    try:
        # Sprawdzamy, czy typ już istnieje
        existing = TelefonTyp.query.filter_by(typ_telefonu=data['name']).first()
        if existing:
            return jsonify({'error': 'Ten typ telefonu już istnieje', 'id': existing.id_telefon_typ}), 400

        # Dodajemy nowy typ telefonu
        new_typ = TelefonTyp(typ_telefonu=data['name'])
        db.session.add(new_typ)
        db.session.commit()

        return jsonify({'id': new_typ.id_telefon_typ, 'name': new_typ.typ_telefonu}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@main.route('/api/firma_typ', methods=['POST'])
def add_firma_typ():
    data = request.json
    if not data or 'name' not in data:
        return jsonify({'error': 'Brak wymaganych danych'}), 400

    try:
        # Sprawdzamy, czy typ już istnieje
        existing = FirmyTyp.query.filter_by(typ_firmy=data['name']).first()
        if existing:
            return jsonify({'error': 'Ten typ firmy już istnieje', 'id': existing.id_firmy_typ}), 400

        # Dodajemy nowy typ firmy
        new_typ = FirmyTyp(typ_firmy=data['name'])
        db.session.add(new_typ)
        db.session.commit()

        return jsonify({'id': new_typ.id_firmy_typ, 'name': new_typ.typ_firmy}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@main.route('/api/specjalnosc', methods=['POST'])
def add_specjalnosc():
    data = request.json
    if not data or 'name' not in data:
        return jsonify({'error': 'Brak wymaganych danych'}), 400

    try:
        # Sprawdzamy, czy specjalność już istnieje
        existing = Specjalnosci.query.filter_by(specjalnosc=data['name']).first()
        if existing:
            return jsonify({'error': 'Ta specjalność już istnieje', 'id': existing.id_specjalnosci}), 400

        # Dodajemy nową specjalność
        new_spec = Specjalnosci(specjalnosc=data['name'])
        db.session.add(new_spec)
        db.session.commit()

        return jsonify({'id': new_spec.id_specjalnosci, 'name': new_spec.specjalnosc}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@main.route('/company/new', methods=['GET', 'POST'])
def new_company():
    from app.forms import CompanyForm
    form = CompanyForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            print("Formularz przeszedł walidację")
            # Create new company
            company = Firmy(
                nazwa_firmy=form.nazwa_firmy.data,
                id_firmy_typ=form.typ_firmy.data,
                strona_www=form.strona_www.data,
                uwagi=form.uwagi.data
            )
            db.session.add(company)
            db.session.flush()  # Get the ID of the new company

            # Add addresses
            for address_form in form.adresy:
                if address_form.miejscowosc.data:  # Only add if miejscowosc is provided
                    address = Adresy(
                        kod=address_form.kod.data,
                        miejscowosc=address_form.miejscowosc.data,
                        ulica_miejscowosc=address_form.ulica_miejscowosc.data,
                        id_adresy_typ=address_form.typ_adresu.data,
                        id_firmy=company.id_firmy
                    )
                    db.session.add(address)

            # Add emails
            for email_form in form.emaile:
                if email_form.email.data:  # Only add if email is provided
                    email = Email(
                        e_mail=email_form.email.data,
                        id_email_typ=email_form.typ_emaila.data,
                        id_firmy=company.id_firmy
                    )
                    db.session.add(email)

            # Pobierz emaile
            emaile = Email.query.filter_by(id_firmy=company.id_firmy).all()
            while len(form.emaile) < len(emaile):
                form.emaile.append_entry()
            for i, email in enumerate(emaile):
                form.emaile[i].typ_emaila.data = email.id_email_typ
                form.emaile[i].email.data = email.e_mail
            # Add phones
            for phone_form in form.telefony:
                if phone_form.telefon.data:  # Only add if phone is provided
                    phone = Telefon(
                        telefon=phone_form.telefon.data,
                        id_telefon_typ=phone_form.typ_telefonu.data,
                        id_firmy=company.id_firmy
                    )
                    db.session.add(phone)

            # Add people
            for person_form in form.osoby:
                if person_form.imie.data and person_form.nazwisko.data:  # Only add if name is provided
                    person = Osoby(
                        imie=person_form.imie.data,
                        nazwisko=person_form.nazwisko.data,
                        stanowisko=person_form.stanowisko.data,
                        e_mail=person_form.email.data,
                        telefon=person_form.telefon.data,
                        id_firmy=company.id_firmy
                    )
                    db.session.add(person)

            # Add ratings
            for rating_form in form.oceny:
                if rating_form.osoba_oceniajaca.data:  # Only add if osoba_oceniajaca is provided
                    rating = Oceny(
                        osoba_oceniajaca=rating_form.osoba_oceniajaca.data,
                        budowa_dzial=rating_form.budowa_dzial.data,
                        rok_wspolpracy=rating_form.rok_wspolpracy.data,
                        ocena=rating_form.ocena.data,
                        komentarz=rating_form.komentarz.data,
                        id_firmy=company.id_firmy
                    )
                    db.session.add(rating)

            # Obszar działania - nowa logika
            obszar_type = form.obszar_dzialania.data

            if obszar_type == 'kraj':
                    # Cały kraj - upewnij się, że kraj to POL
                    if form.kraj.data == 'POL':
                        obszar = FirmyObszarDzialania(
                            id_firmy=company.id_firmy,
                            id_kraj='POL',
                            id_wojewodztwa='N/A',
                            id_powiaty=0
                        )
                        db.session.add(obszar)
            elif obszar_type == 'wojewodztwa':
                # Tylko województwa - kraj powinien być N/A
                for woj_id in form.wojewodztwa.data:
                    obszar = FirmyObszarDzialania(
                        id_firmy=company.id_firmy,
                        id_kraj='N/A',
                        id_wojewodztwa=woj_id,
                        id_powiaty=0
                    )
                    db.session.add(obszar)
            elif obszar_type == 'powiaty':
                # # Powiaty (województwa są również zapisywane) - kraj pusty
                # for woj_id in form.wojewodztwa.data:
                #     obszar = FirmyObszarDzialania(
                #         id_firmy=company.id_firmy,
                #         id_kraj='',
                #         id_wojewodztwa=woj_id,
                #         id_powiaty=''
                #     )
                #     db.session.add(obszar)

                for pow_id in form.powiaty.data:
                    powiat = Powiaty.query.get(pow_id)
                    obszar = FirmyObszarDzialania(
                        id_firmy=company.id_firmy,
                        id_kraj='N/A',
                        id_wojewodztwa=powiat.id_wojewodztwa,
                        id_powiaty=pow_id
                    )
                    db.session.add(obszar)

            # Add specialties
            for spec_id in form.specjalnosci.data:
                spec = FirmySpecjalnosci(
                    id_firmy=company.id_firmy,
                    id_specjalnosci=spec_id
                )
                db.session.add(spec)

            db.session.commit()
            flash('Firma została dodana pomyślnie!', 'success')
            return redirect(url_for('main.company_details', company_id=company.id_firmy))
        else:
            if form.errors:
                print("Błędy walidacji:", form.errors)
                flash(f'Błędy w formularzu: {form.errors}', 'danger')
                return render_template('company_form.html', form=form, title='Nowa firma')

    # Dla GET lub ponownego wyświetlenia formularza z błędami
    return render_template('company_form.html', form=form, title='Nowa firma')

@main.route('/company/<int:company_id>/edit', methods=['GET', 'POST'])
def edit_company(company_id):
    from app.forms import CompanyForm

    # Pobierz firmę z bazy danych lub zwróć 404 jeśli nie istnieje
    company = Firmy.query.get_or_404(company_id)

    # Utwórz formularz i wypełnij go danymi
    form = CompanyForm(obj=company)

    # Jeśli to GET request, zapełnij pola formularza danymi z bazy
    if request.method == 'GET':
        # Zapełnij podstawowe informacje
        form.nazwa_firmy.data = company.nazwa_firmy
        form.typ_firmy.data = company.id_firmy_typ
        form.strona_www.data = company.strona_www
        form.uwagi.data = company.uwagi

        # Pobierz adresy
        adresy = Adresy.query.filter_by(id_firmy=company_id).all()
        while len(form.adresy) < len(adresy):
            form.adresy.append_entry()
        for i, adres in enumerate(adresy):
            form.adresy[i].typ_adresu.data = adres.id_adresy_typ
            form.adresy[i].kod.data = adres.kod
            form.adresy[i].miejscowosc.data = adres.miejscowosc
            form.adresy[i].ulica_miejscowosc.data = adres.ulica_miejscowosc

        # Pobierz emaile
        emaile = Email.query.filter_by(id_firmy=company_id).all()
        while len(form.emaile) < len(emaile):
            form.emaile.append_entry()
            form.emaile[-1].typ_emaila.choices = form.email_type_choices
        for i, email in enumerate(emaile):
            form.emaile[i].typ_emaila.data = email.id_email_typ
            form.emaile[i].email.data = email.e_mail

        # Pobierz telefony
        telefony = Telefon.query.filter_by(id_firmy=company_id).all()
        while len(form.telefony) < len(telefony):
            form.telefony.append_entry()
        for i, telefon in enumerate(telefony):
            form.telefony[i].typ_telefonu.data = telefon.id_telefon_typ
            form.telefony[i].telefon.data = telefon.telefon

        # Pobierz osoby kontaktowe
        osoby = Osoby.query.filter_by(id_firmy=company_id).all()
        while len(form.osoby) < len(osoby):
            form.osoby.append_entry()
        for i, osoba in enumerate(osoby):
            form.osoby[i].imie.data = osoba.imie
            form.osoby[i].nazwisko.data = osoba.nazwisko
            form.osoby[i].stanowisko.data = osoba.stanowisko
            form.osoby[i].email.data = osoba.e_mail
            form.osoby[i].telefon.data = osoba.telefon

        # Pobierz oceny
        oceny = Oceny.query.filter_by(id_firmy=company_id).all()
        while len(form.oceny) < len(oceny):
            form.oceny.append_entry()
        for i, ocena in enumerate(oceny):
            form.oceny[i].osoba_oceniajaca.data = ocena.osoba_oceniajaca
            form.oceny[i].budowa_dzial.data = ocena.budowa_dzial
            form.oceny[i].rok_wspolpracy.data = ocena.rok_wspolpracy
            form.oceny[i].ocena.data = ocena.ocena
            form.oceny[i].komentarz.data = ocena.komentarz

        # Obszar działania
        obszary = FirmyObszarDzialania.query.filter_by(id_firmy=company_id).all()

        # Sprawdź czy firma działa w całym kraju
        obszar_krajowy = next((o for o in obszary if o.id_kraj == 'POL'), None)
        if obszar_krajowy:
            form.obszar_dzialania.data = 'kraj'
            form.kraj.data = 'POL'
        else:
            # Sprawdź czy są powiaty
            has_powiaty = any(o.id_powiaty > 0 for o in obszary)
            if has_powiaty:
                form.obszar_dzialania.data = 'powiaty'
            else:
                # Sprawdź czy są województwa
                has_wojewodztwa = any(o.id_wojewodztwa for o in obszary)
                if has_wojewodztwa:
                    form.obszar_dzialania.data = 'wojewodztwa'
                else:
                    form.obszar_dzialania.data = 'kraj'  # Domyślna wartość

            form.kraj.data = ''

            # Zbierz ID województw (unikalne)
            wojewodztwa_ids = list(set([o.id_wojewodztwa for o in obszary if o.id_wojewodztwa]))
            form.wojewodztwa.data = [w for w in wojewodztwa_ids if w]  # Pomiń puste wartości

            # Zbierz ID powiatów
            powiaty_ids = [o.id_powiaty for o in obszary if o.id_powiaty and o.id_powiaty > 0]
            form.powiaty.data = powiaty_ids

        # Pobierz specjalności
        specjalnosci = FirmySpecjalnosci.query.filter_by(id_firmy=company_id).all()
        form.specjalnosci.data = [s.id_specjalnosci for s in specjalnosci]

    elif request.method == 'POST':
        if form.validate_on_submit():
            print("Formularz przeszedł walidację")
            # Aktualizuj podstawowe dane firmy
            company.nazwa_firmy = form.nazwa_firmy.data
            company.id_firmy_typ = form.typ_firmy.data
            company.strona_www = form.strona_www.data
            company.uwagi = form.uwagi.data

            with db.session.no_autoflush:
                # Usuń istniejące adresy, emaile, telefony, osoby, oceny, obszary, specjalności
                Adresy.query.filter_by(id_firmy=company_id).delete()
                Email.query.filter_by(id_firmy=company_id).delete()
                Telefon.query.filter_by(id_firmy=company_id).delete()
                Osoby.query.filter_by(id_firmy=company_id).delete()
                Oceny.query.filter_by(id_firmy=company_id).delete()
                FirmyObszarDzialania.query.filter_by(id_firmy=company_id).delete()
                FirmySpecjalnosci.query.filter_by(id_firmy=company_id).delete()

                db.session.flush()

                # Dodaj nowe adresy
                for address_form in form.adresy:
                    if address_form.miejscowosc.data:  # Dodaj tylko jeśli miejscowość jest podana
                        address = Adresy(
                            kod=address_form.kod.data,
                            miejscowosc=address_form.miejscowosc.data,
                            ulica_miejscowosc=address_form.ulica_miejscowosc.data,
                            id_adresy_typ=address_form.typ_adresu.data,
                            id_firmy=company_id
                        )
                        db.session.add(address)

            # Dodaj nowe emaile
            for email_form in form.emaile:
                if email_form.email.data:  # Dodaj tylko jeśli email jest podany
                    email = Email(
                        e_mail=email_form.email.data,
                        id_email_typ=email_form.typ_emaila.data,
                        id_firmy=company_id
                    )
                    db.session.add(email)

            # Dodaj nowe telefony
            for phone_form in form.telefony:
                if phone_form.telefon.data:  # Dodaj tylko jeśli telefon jest podany
                    phone = Telefon(
                        telefon=phone_form.telefon.data,
                        id_telefon_typ=phone_form.typ_telefonu.data,
                        id_firmy=company_id
                    )
                    db.session.add(phone)

            # Dodaj nowe osoby
            for person_form in form.osoby:
                if person_form.imie.data and person_form.nazwisko.data:  # Dodaj tylko jeśli imię i nazwisko są podane
                    person = Osoby(
                        imie=person_form.imie.data,
                        nazwisko=person_form.nazwisko.data,
                        stanowisko=person_form.stanowisko.data,
                        e_mail=person_form.email.data,
                        telefon=person_form.telefon.data,
                        id_firmy=company_id
                    )
                    db.session.add(person)

            # Dodaj nowe oceny
            for rating_form in form.oceny:
                if rating_form.osoba_oceniajaca.data:  # Dodaj tylko jeśli osoba oceniająca jest podana
                    rating = Oceny(
                        osoba_oceniajaca=rating_form.osoba_oceniajaca.data,
                        budowa_dzial=rating_form.budowa_dzial.data,
                        rok_wspolpracy=rating_form.rok_wspolpracy.data,
                        ocena=rating_form.ocena.data,
                        komentarz=rating_form.komentarz.data,
                        id_firmy=company_id
                    )
                    db.session.add(rating)

            # Obszar działania - nowa logika
            obszar_type = form.obszar_dzialania.data

            if obszar_type == 'kraj':
                    # Cały kraj - upewnij się, że kraj to POL
                    if form.kraj.data == 'POL':
                        obszar = FirmyObszarDzialania(
                            id_firmy=company.id_firmy,
                            id_kraj='POL',
                            id_wojewodztwa='N/A',
                            id_powiaty=0
                        )
                        db.session.add(obszar)
            elif obszar_type == 'wojewodztwa':
                # Tylko województwa - kraj powinien być N/A
                for woj_id in form.wojewodztwa.data:
                    obszar = FirmyObszarDzialania(
                        id_firmy=company.id_firmy,
                        id_kraj='N/A',
                        id_wojewodztwa=woj_id,
                        id_powiaty=0
                    )
                    db.session.add(obszar)
            elif obszar_type == 'powiaty':
                # # Powiaty (województwa są również zapisywane) - kraj pusty
                # for woj_id in form.wojewodztwa.data:
                #     obszar = FirmyObszarDzialania(
                #         id_firmy=company.id_firmy,
                #         id_kraj='',
                #         id_wojewodztwa=woj_id,
                #         id_powiaty=0
                #     )
                #     db.session.add(obszar)

                for pow_id in form.powiaty.data:
                    powiat = Powiaty.query.get(pow_id)
                    obszar = FirmyObszarDzialania(
                        id_firmy=company.id_firmy,
                        id_kraj='N/A',
                        id_wojewodztwa=powiat.id_wojewodztwa,
                        id_powiaty=pow_id
                    )
                    db.session.add(obszar)

            # Dodaj specjalności
            for spec_id in form.specjalnosci.data:
                spec = FirmySpecjalnosci(
                    id_firmy=company_id,
                    id_specjalnosci=spec_id
                )
                db.session.add(spec)

            db.session.commit()
            flash('Firma została zaktualizowana pomyślnie!', 'success')
            return redirect(url_for('main.company_details', company_id=company_id))

        else:
            print("Błędy walidacji:", form.errors)
            flash(f'Błędy w formularzu: {form.errors}', 'danger')

    return render_template('company_form.html', 
                         form=form, 
                         title='Edycja firmy',  # Zmienione z 'Nowa firma'
                         company_id=company_id)  # Dodane company_id

@main.route('/company/<int:company_id>/delete', methods=['POST'])
def delete_company(company_id):
    company = Firmy.query.get_or_404(company_id)
    try:
        # Usuwanie wszystkich powiązanych rekordów
        Adresy.query.filter_by(id_firmy=company_id).delete()
        Email.query.filter_by(id_firmy=company_id).delete()
        Telefon.query.filter_by(id_firmy=company_id).delete()
        Osoby.query.filter_by(id_firmy=company_id).delete()
        Oceny.query.filter_by(id_firmy=company_id).delete()
        FirmyObszarDzialania.query.filter_by(id_firmy=company_id).delete()
        FirmySpecjalnosci.query.filter_by(id_firmy=company_id).delete()
        # Usuwanie firmy
        db.session.delete(company)
        db.session.commit()
        flash('Firma została usunięta pomyślnie!', 'success')
        return jsonify({'success': True, 'redirect': url_for('main.index')})
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'Wystąpił błąd podczas usuwania firmy: {str(e)}', 'danger')
        return jsonify({'success': False, 'error': str(e)}), 500

@main.route('/specialties')
def list_specialties():
    specialties = Specjalnosci.query.all()
    return render_template('specialties.html', items=specialties, title='Specjalności')

@main.route('/specialties/new', methods=['GET', 'POST'])
def new_specialty():
    from app.forms import SpecialtyForm # Local import
    form = SpecialtyForm()
    if form.validate_on_submit():
        try:
            # Sprawdzamy, czy specjalność już istnieje (case-insensitive)
            existing_spec = Specjalnosci.query.filter(func.lower(Specjalnosci.specjalnosc) == func.lower(form.name.data)).first()
            if existing_spec:
                flash('Specjalność o tej nazwie już istnieje.', 'warning')
            else:
                new_spec = Specjalnosci(specjalnosc=form.name.data)
                db.session.add(new_spec)
                db.session.commit()
                flash('Specjalność została dodana pomyślnie!', 'success')
                return redirect(url_for('main.list_specialties'))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Wystąpił błąd podczas dodawania specjalności: {e}', 'danger')
    return render_template('simple_form.html', form=form, title='Dodaj Specjalność', back_url=url_for('main.list_specialties'))

@main.route('/specialties/<int:id>/edit', methods=['GET', 'POST'])
def edit_specialty(id):
    from app.forms import SpecialtyForm # Local import
    specialty = Specjalnosci.query.get_or_404(id)
    form = SpecialtyForm(obj=specialty)
    if request.method == 'GET':
        # Explicitly set the form data for the 'name' field from the model attribute 'Specjalnosc'
        form.name.data = specialty.specjalnosc
        return render_template('simple_form.html', form=form, title='Edytuj Specjalność', back_url=url_for('main.list_specialties'))
    else: # POST request
        if form.validate_on_submit():
            try:
                # Sprawdzamy, czy inna specjalność o tej nazwie już istnieje (case-insensitive)
                existing_spec = Specjalnosci.query.filter(func.lower(Specjalnosci.specjalnosc) == func.lower(form.name.data), Specjalnosci.id_specjalnosci != id).first()
                if existing_spec:
                    flash('Specjalność o tej nazwie już istnieje.', 'warning')
                else:
                    specialty.specjalnosc = form.name.data
                    db.session.commit()
                    flash('Specjalność została zaktualizowana pomyślnie!', 'success')
                    return redirect(url_for('main.list_specialties'))
            except SQLAlchemyError as e:
                db.session.rollback()
                flash(f'Wystąpił błąd podczas aktualizacji specjalności: {e}', 'danger')
        return render_template('simple_form.html', form=form, title='Edytuj Specjalność', back_url=url_for('main.list_specialties'))

@main.route('/specialties/<int:id>/delete', methods=['POST'])
def delete_specialty(id):
    specialty = Specjalnosci.query.get_or_404(id)
    try:
        db.session.delete(specialty)
        db.session.commit()
        flash('Specjalność została usunięta pomyślnie!', 'success')
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'Wystąpił błąd podczas usuwania specjalności: {e}', 'danger')
    return redirect(url_for('main.list_specialties'))


@main.route('/address_types')
def list_address_types():
    address_types = AdresyTyp.query.all()
    return render_template('address_types.html', items=address_types, title='Typy Adresów')

@main.route('/address_types/new', methods=['GET', 'POST'])
def new_address_type():
    from app.forms import AddressTypeForm # Local import
    form = AddressTypeForm()
    if form.validate_on_submit():
        try:
            # Sprawdzamy, czy typ adresu już istnieje (case-insensitive)
            existing_type = AdresyTyp.query.filter(func.lower(AdresyTyp.typ_adresu) == func.lower(form.name.data)).first()
            if existing_type:
                flash('Typ adresu o tej nazwie już istnieje.', 'warning')
            else:
                new_type = AdresyTyp(typ_adresu=form.name.data)
                db.session.add(new_type)
                db.session.commit()
                flash('Typ adresu został dodany pomyślnie!', 'success')
                return redirect(url_for('main.list_address_types'))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Wystąpił błąd podczas dodawania typu adresu: {e}', 'danger')
    return render_template('simple_form.html', form=form, title='Dodaj Typ Adresu', back_url=url_for('main.list_address_types'))


@main.route('/address_types/<int:id>/edit', methods=['GET', 'POST'])
def edit_address_type(id):
    from app.forms import AddressTypeForm # Local import
    address_type = AdresyTyp.query.get_or_404(id)
    form = AddressTypeForm(obj=address_type)
    if request.method == 'GET':
         # Explicitly set the form data for the 'name' field from the model attribute 'typ_adresu'
        form.name.data = address_type.typ_adresu
        return render_template('simple_form.html', form=form, title='Edytuj Typ Adresu', back_url=url_for('main.list_address_types'))
    else: # POST request
        if form.validate_on_submit():
            try:
                # Sprawdzamy, czy inny typ adresu o tej nazwie już istnieje (case-insensitive)
                existing_type = AdresyTyp.query.filter(func.lower(AdresyTyp.typ_adresu) == func.lower(form.name.data), AdresyTyp.id_adresy_typ != id).first()
                if existing_type:
                    flash('Typ adresu o tej nazwie już istnieje.', 'warning')
                else:
                    address_type.typ_adresu = form.name.data
                    db.session.commit()
                    flash('Typ adresu został zaktualizowany pomyślnie!', 'success')
                    return redirect(url_for('main.list_address_types'))
            except SQLAlchemyError as e:
                db.session.rollback()
                flash(f'Wystąpił błąd podczas aktualizacji typu adresu: {e}', 'danger')
        return render_template('simple_form.html', form=form, title='Edytuj Typ Adresu', back_url=url_for('main.list_address_types'))

@main.route('/address_types/<int:id>/delete', methods=['POST'])
def delete_address_type(id):
    address_type = AdresyTyp.query.get_or_404(id)
    try:
        db.session.delete(address_type)
        db.session.commit()
        flash('Typ adresu został usunięty pomyślnie!', 'success')
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'Wystąpił błąd podczas usuwania typu adresu: {e}', 'danger')
    return redirect(url_for('main.list_address_types'))


@main.route('/email_types')
def list_email_types():
    email_types = EmailTyp.query.all()
    return render_template('email_types.html', items=email_types, title='Typy E-maili')

@main.route('/email_types/new', methods=['GET', 'POST'])
def new_email_type():
    from app.forms import EmailTypeForm # Local import
    form = EmailTypeForm()
    if form.validate_on_submit():
        try:
            # Sprawdzamy, czy typ emaila już istnieje (case-insensitive)
            existing_type = EmailTyp.query.filter(func.lower(EmailTyp.typ_emaila) == func.lower(form.name.data)).first()
            if existing_type:
                flash('Typ emaila o tej nazwie już istnieje.', 'warning')
            else:
                new_type = EmailTyp(typ_emaila=form.name.data)
                db.session.add(new_type)
                db.session.commit()
                flash('Typ emaila został dodany pomyślnie!', 'success')
                return redirect(url_for('main.list_email_types'))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Wystąpił błąd podczas dodawania typu emaila: {e}', 'danger')
    return render_template('simple_form.html', form=form, title='Dodaj Typ E-maila', back_url=url_for('main.list_email_types'))

@main.route('/email_types/<int:id>/edit', methods=['GET', 'POST'])
def edit_email_type(id):
    from app.forms import EmailTypeForm # Local import
    email_type = EmailTyp.query.get_or_404(id)
    form = EmailTypeForm(obj=email_type)
    if request.method == 'GET':
        # Explicitly set the form data for the 'name' field from the model attribute 'Typ_emaila'
        form.name.data = email_type.typ_emaila
        return render_template('simple_form.html', form=form, title='Edytuj Typ E-maila', back_url=url_for('main.list_email_types'))
    else: # POST request
        if form.validate_on_submit():
            try:
                # Sprawdzamy, czy inny typ emaila o tej nazwie już istnieje (case-insensitive)
                existing_type = EmailTyp.query.filter(func.lower(EmailTyp.typ_emaila) == func.lower(form.name.data), EmailTyp.id_email_typ != id).first()
                if existing_type:
                    flash('Typ emaila o tej nazwie już istnieje.', 'warning')
                else:
                    email_type.typ_emaila = form.name.data
                    db.session.commit()
                    flash('Typ emaila został zaktualizowany pomyślnie!', 'success')
                    return redirect(url_for('main.list_email_types'))
            except SQLAlchemyError as e:
                db.session.rollback()
                flash(f'Wystąpił błąd podczas aktualizacji typu emaila: {e}', 'danger')
        return render_template('simple_form.html', form=form, title='Edytuj Typ E-maila', back_url=url_for('main.list_email_types'))

@main.route('/email_types/<int:id>/delete', methods=['POST'])
def delete_email_type(id):
    email_type = EmailTyp.query.get_or_404(id)
    try:
        db.session.delete(email_type)
        db.session.commit()
        flash('Typ emaila został usunięty pomyślnie!', 'success')
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'Wystąpił błąd podczas usuwania typu emaila: {e}', 'danger')
    return redirect(url_for('main.list_email_types'))


@main.route('/phone_types')
def list_phone_types():
    phone_types = TelefonTyp.query.all()
    return render_template('phone_types.html', items=phone_types, title='Typy Telefonów')

@main.route('/phone_types/new', methods=['GET', 'POST'])
def new_phone_type():
    from app.forms import PhoneTypeForm # Local import
    form = PhoneTypeForm()
    if form.validate_on_submit():
        try:
            # Sprawdzamy, czy typ telefonu już istnieje (case-insensitive)
            existing_type = TelefonTyp.query.filter(func.lower(TelefonTyp.typ_telefonu) == func.lower(form.name.data)).first()
            if existing_type:
                flash('Typ telefonu o tej nazwie już istnieje.', 'warning')
            else:
                new_type = TelefonTyp(typ_telefonu=form.name.data)
                db.session.add(new_type)
                db.session.commit()
                flash('Typ telefonu został dodany pomyślnie!', 'success')
                return redirect(url_for('main.list_phone_types'))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Wystąpił błąd podczas dodawania typu telefonu: {e}', 'danger')
    return render_template('simple_form.html', form=form, title='Dodaj Typ Telefonu', back_url=url_for('main.list_phone_types'))

@main.route('/phone_types/<int:id>/edit', methods=['GET', 'POST'])
def edit_phone_type(id):
    from app.forms import PhoneTypeForm # Local import
    phone_type = TelefonTyp.query.get_or_404(id)
    form = PhoneTypeForm(obj=phone_type)
    if request.method == 'GET':
        # Explicitly set the form data for the 'name' field from the model attribute 'Typ_telefonu'
        form.name.data = phone_type.typ_telefonu
        return render_template('simple_form.html', form=form, title='Edytuj Typ Telefonu', back_url=url_for('main.list_phone_types'))
    else: # POST request
        if form.validate_on_submit():
            try:
                # Sprawdzamy, czy inny typ telefonu o tej nazwie już istnieje (case-insensitive)
                existing_type = TelefonTyp.query.filter(func.lower(TelefonTyp.typ_telefonu) == func.lower(form.name.data), TelefonTyp.id_telefon_typ != id).first()
                if existing_type:
                    flash('Typ telefonu o tej nazwie już istnieje.', 'warning')
                else:
                    phone_type.typ_telefonu = form.name.data
                    db.session.commit()
                    flash('Typ telefonu został zaktualizowany pomyślnie!', 'success')
                    return redirect(url_for('main.list_phone_types'))
            except SQLAlchemyError as e:
                db.session.rollback()
                flash(f'Wystąpił błąd podczas aktualizacji typu telefonu: {e}', 'danger')
        return render_template('simple_form.html', form=form, title='Edytuj Typ Telefonu', back_url=url_for('main.list_phone_types'))

@main.route('/phone_types/<int:id>/delete', methods=['POST'])
def delete_phone_type(id):
    phone_type = TelefonTyp.query.get_or_404(id)
    try:
        db.session.delete(phone_type)
        db.session.commit()
        flash('Typ telefonu został usunięty pomyślnie!', 'success')
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'Wystąpił błąd podczas usuwania typu telefonu: {e}', 'danger')
    return redirect(url_for('main.list_phone_types'))

# Routes for Company Types
@main.route('/company_types')
def list_company_types():
    company_types = FirmyTyp.query.all()
    return render_template('company_types.html', items=company_types, title='Typy Firm')

@main.route('/company_types/new', methods=['GET', 'POST'])
def new_company_type():
    from app.forms import CompanyTypeForm # Local import
    form = CompanyTypeForm()
    if form.validate_on_submit():
        try:
            # Check if company type already exists (case-insensitive)
            existing_type = FirmyTyp.query.filter(func.lower(FirmyTyp.typ_firmy) == func.lower(form.name.data)).first()
            if existing_type:
                flash('Typ firmy o tej nazwie już istnieje.', 'warning')
            else:
                new_type = FirmyTyp(typ_firmy=form.name.data)
                db.session.add(new_type)
                db.session.commit()
                flash('Typ firmy został dodany pomyślnie!', 'success')
                return redirect(url_for('main.list_company_types'))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Wystąpił błąd podczas dodawania typu firmy: {e}', 'danger')
    return render_template('simple_form.html', form=form, title='Dodaj Typ Firmy', back_url=url_for('main.list_company_types'))

@main.route('/company_types/<int:id>/edit', methods=['GET', 'POST'])
def edit_company_type(id):
    from app.forms import CompanyTypeForm # Local import
    company_type = FirmyTyp.query.get_or_404(id)
    form = CompanyTypeForm(obj=company_type)
    if request.method == 'GET':
         # Explicitly set the form data for the 'name' field from the model attribute 'Typ_firmy'
        form.name.data = company_type.typ_firmy
        return render_template('simple_form.html', form=form, title='Edytuj Typ Firmy', back_url=url_for('main.list_company_types'))
    else: # POST request
        if form.validate_on_submit():
            try:
                # Check if another company type with this name already exists (case-insensitive)
                existing_type = FirmyTyp.query.filter(func.lower(FirmyTyp.typ_firmy) == func.lower(form.name.data), FirmyTyp.id_firmy_typ != id).first()
                if existing_type:
                     flash('Typ firmy o tej nazwie już istnieje.', 'warning')
                else:
                    company_type.typ_firmy = form.name.data
                    db.session.commit()
                    flash('Typ firmy został zaktualizowany pomyślnie!', 'success')
                    return redirect(url_for('main.list_company_types'))
            except SQLAlchemyError as e:
                db.session.rollback()
                flash(f'Wystąpił błąd podczas aktualizacji typu firmy: {e}', 'danger')
        return render_template('simple_form.html', form=form, title='Edytuj Typ Firmy', back_url=url_for('main.list_company_types'))

@main.route('/company_types/<int:id>/delete', methods=['POST'])
def delete_company_type(id):
    company_type = FirmyTyp.query.get_or_404(id)
    try:
        db.session.delete(company_type)
        db.session.commit()
        flash('Typ firmy został usunięty pomyślnie!', 'success')
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'Wystąpił błąd podczas usuwania typu firmy: {e}', 'danger')
    return redirect(url_for('main.list_company_types'))

# Routes for Persons
@main.route('/persons')
def list_persons():
    persons = Osoby.query.all()
    return render_template('persons.html', items=persons, title='Osoby Kontaktowe')

@main.route('/persons/new', methods=['GET', 'POST'])
def new_person():
    form = SimplePersonForm()
    if form.validate_on_submit():
        try:
            new_person = Osoby(
                imie=form.imie.data,
                nazwisko=form.nazwisko.data,
                stanowisko=form.stanowisko.data,
                e_mail=form.e_mail.data,
                telefon=form.telefon.data,
                id_firmy=form.id_firmy.data
            )
            db.session.add(new_person)
            db.session.commit()
            flash('Osoba kontaktowa została dodana pomyślnie!', 'success')
            return redirect(url_for('main.list_persons'))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Wystąpił błąd podczas dodawania osoby kontaktowej: {e}', 'danger')
    return render_template('person_form.html', form=form, title='Dodaj Osobę Kontaktową', back_url=url_for('main.list_persons'))

@main.route('/persons/<int:id>/edit', methods=['GET', 'POST'])
def edit_person(id):
    person = Osoby.query.get_or_404(id)
    # Użyj zaktualizowanej definicji formularza SimplePersonForm
    form = SimplePersonForm(obj=person) # Teraz obj=person powinno poprawnie wypełnić WSZYSTKIE pola

    if form.validate_on_submit():
        try:
            # Używaj zaktualizowanych nazw pól z formularza
            person.imie = form.imie.data
            person.nazwisko = form.nazwisko.data
            person.stanowisko = form.stanowisko.data
            person.e_mail = form.e_mail.data # Poprawna nazwa
            person.telefon = form.telefon.data # Poprawna nazwa
            person.id_firmy = form.id_firmy.data # Poprawna nazwa dla pola SelectField
            db.session.commit()
            flash('Osoba kontaktowa została zaktualizowana pomyślnie!', 'success')
            return redirect(url_for('main.list_persons'))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Wystąpił błąd podczas aktualizacji osoby kontaktowej: {e}', 'danger')

    # Przy GET lub błędzie walidacji, renderuj szablon.
    # Formularz przekazany do szablonu będzie już wypełniony danymi z 'person' dzięki obj=person
    return render_template('person_form.html', form=form, title='Edytuj Osobę Kontaktową', back_url=url_for('main.list_persons'))


@main.route('/persons/<int:id>/delete', methods=['POST'])
def delete_person(id):
    person = Osoby.query.get_or_404(id)
    try:
        db.session.delete(person)
        db.session.commit()
        flash('Osoba kontaktowa została usunięta pomyślnie!', 'success')
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'Wystąpił błąd podczas usuwania osoby kontaktowej: {e}', 'danger')
    return redirect(url_for('main.list_persons'))


# Routes for Ratings
@main.route('/ratings')
def list_ratings():
    ratings = Oceny.query.all()
    return render_template('ratings.html', items=ratings, title='Oceny Współpracy')

@main.route('/ratings/new', methods=['GET', 'POST'])
def new_rating():
    form = SimpleRatingForm()
    if form.validate_on_submit():
        try:
            new_rating = Oceny(
                osoba_oceniajaca=form.osoba_oceniajaca.data,
                budowa_dzial=form.budowa_dzial.data,
                rok_wspolpracy=form.rok_wspolpracy.data,
                ocena=form.ocena.data,
                komentarz=form.komentarz.data,
                id_firmy=form.id_firmy.data
            )
            db.session.add(new_rating)
            db.session.commit()
            flash('Ocena została dodana pomyślnie!', 'success')
            return redirect(url_for('main.list_ratings'))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Wystąpił błąd podczas dodawania oceny: {e}', 'danger')
    return render_template('rating_form.html', form=form, title='Dodaj Ocenę Współpracy', back_url=url_for('main.list_ratings'))

@main.route('/ratings/<int:id>/edit', methods=['GET', 'POST'])
def edit_rating(id):
    rating = Oceny.query.get_or_404(id)
    form = SimpleRatingForm(obj=rating)
    if form.validate_on_submit():
        try:
            rating.osoba_oceniajaca = form.osoba_oceniajaca.data
            rating.budowa_dzial = form.budowa_dzial.data
            rating.rok_wspolpracy = form.rok_wspolpracy.data
            rating.ocena = form.ocena.data
            rating.komentarz = form.komentarz.data
            rating.id_firmy = form.id_firmy.data
            db.session.commit()
            flash('Ocena została zaktualizowana pomyślnie!', 'success')
            return redirect(url_for('main.list_ratings'))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Wystąpił błąd podczas aktualizacji oceny: {e}', 'danger')
    # On GET request or validation failure, the form will be pre-populated by obj=
    return render_template('rating_form.html', form=form, title='Edytuj Ocenę Współpracy', back_url=url_for('main.list_ratings'))

@main.route('/ratings/<int:id>/delete', methods=['POST'])
def delete_rating(id):
    rating = Oceny.query.get_or_404(id)
    try:
        db.session.delete(rating)
        db.session.commit()
        flash('Ocena została usunięta pomyślnie!', 'success')
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'Wystąpił błąd podczas usuwania oceny: {e}', 'danger')
    return redirect(url_for('main.list_ratings'))

@main.route('/export_companies_html')
def export_companies_html():
    # Ta funkcja będzie generować stronę HTML do wydruku/zapisu
    query = Firmy.query

    # SKOPIUJ DOKŁADNIE LOGIKĘ FILTROWANIA ZE FUNKCJI index()
    # Potrzebujemy zastosować TE SAME FILTRY, co na stronie głównej

    # Handle search filter
    search = request.args.get('search', '')
    if search:
        normalized_search = ''.join(c for c in search if c.isalnum() or c.isspace())
        matching_company_ids = set()

        # Replicate search logic across all relevant tables
        # (This part is identical to your index function)
        # --- Start of duplicated search logic ---
        # UWAGA: Ta część jest nieefektywna dla dużych baz danych, ale skopiowana z oryginału
        firmy_results = Firmy.query.all()
        for firma in firmy_results:
            if (normalized_search in normalize_text(firma.nazwa_firmy).lower() or
                normalized_search in normalize_text(firma.strona_www).lower() or
                normalized_search in normalize_text(firma.uwagi).lower()):
                matching_company_ids.add(firma.id_firmy)

        adres_results = Adresy.query.all()
        for adres in adres_results:
            if (normalized_search in normalize_text(adres.kod).lower() or
                normalized_search in normalize_text(adres.miejscowosc).lower() or
                normalized_search in normalize_text(adres.ulica_miejscowosc).lower()):
                if adres.id_firmy:
                    matching_company_ids.add(adres.id_firmy)

        email_results = Email.query.all()
        for email in email_results:
            if normalized_search in normalize_text(email.e_mail).lower():
                if email.id_firmy:
                    matching_company_ids.add(email.id_firmy)

        telefon_results = Telefon.query.all()
        for telefon in telefon_results:
            if normalized_search in normalize_text(telefon.telefon).lower():
                if telefon.id_firmy:
                    matching_company_ids.add(telefon.id_firmy)

        osoby_results = Osoby.query.all()
        for osoba in osoby_results:
            if (normalized_search in normalize_text(osoba.imie).lower() or
                normalized_search in normalize_text(osoba.nazwisko).lower() or
                normalized_search in normalize_text(osoba.stanowisko).lower() or
                normalized_search in normalize_text(osoba.e_mail).lower() or
                normalized_search in normalize_text(osoba.telefon).lower()):
                if osoba.id_firmy:
                    matching_company_ids.add(osoba.id_firmy)

        oceny_results = Oceny.query.all()
        for ocena in oceny_results:
            if (normalized_search in normalize_text(ocena.osoba_oceniajaca).lower() or
                normalized_search in normalize_text(ocena.budowa_dzial).lower() or
                normalized_search in normalize_text(ocena.komentarz).lower()):
                if ocena.id_firmy:
                    matching_company_ids.add(ocena.id_firmy)

        specjalnosci_results = Specjalnosci.query.all()
        for spec in specjalnosci_results:
            if normalized_search in normalize_text(spec.specjalnosc).lower():
                firmy_spec = FirmySpecjalnosci.query.filter_by(id_specjalnosci=spec.id_specjalnosci).all()
                for fs in firmy_spec:
                    matching_company_ids.add(fs.id_firmy)

        firmy_typ_results = FirmyTyp.query.all()
        for typ in firmy_typ_results:
            if normalized_search in normalize_text(typ.typ_firmy).lower():
                firmy_by_typ = Firmy.query.filter_by(id_firmy_typ=typ.id_firmy_typ).all()
                for firma in firmy_by_typ:
                    matching_company_ids.add(firma.id_firmy)

        wojewodztwa_results = Wojewodztwa.query.all()
        for woj in wojewodztwa_results:
            if normalized_search in normalize_text(woj.wojewodztwo).lower():
                firmy_woj = FirmyObszarDzialania.query.filter_by(id_wojewodztwa=woj.id_wojewodztwa).all()
                for fw in firmy_woj:
                    matching_company_ids.add(fw.id_firmy)

        powiaty_results = Powiaty.query.all()
        for pow in powiaty_results:
            if normalized_search in normalize_text(pow.powiat).lower():
                firmy_pow = FirmyObszarDzialania.query.filter_by(id_powiaty=pow.id_powiaty).all()
                for fp in firmy_pow:
                    matching_company_ids.add(fp.id_firmy)

        kraje_results = Kraj.query.all() # Assuming Kraj model exists and has 'POL' ID
        for kraj in kraje_results:
             if normalized_search in normalize_text(kraj.kraj).lower():
                firmy_kraj = FirmyObszarDzialania.query.filter_by(id_kraj=kraj.id_kraj).all()
                for fk in firmy_kraj:
                    matching_company_ids.add(fk.id_firmy)

        if matching_company_ids:
            query = query.filter(Firmy.id_firmy.in_(matching_company_ids))
        else:
            query = query.filter(False) # No results match search criteria
        # --- End of duplicated search logic ---

    # Handle specialty filter
    specialties = request.args.getlist('specialties')
    if specialties:
        # Apply the filter to the current query state
        query = query.join(FirmySpecjalnosci)\
                     .filter(FirmySpecjalnosci.id_specjalnosci.in_(specialties))

    # Handle area filter
    wojewodztwo = request.args.get('wojewodztwo')
    powiat = request.args.get('powiat')

    if powiat:
        # Replicate powiat logic
        nationwide_companies = db.session.query(Firmy.id_firmy)\
                                 .join(FirmyObszarDzialania)\
                                 .filter(FirmyObszarDzialania.id_kraj == 'POL')

        powiat_data = Powiaty.query.filter_by(id_powiaty=powiat).first()

        if powiat_data:
            wojewodztwo_id = powiat_data.id_wojewodztwa

            powiat_companies = db.session.query(Firmy.id_firmy)\
                                 .join(FirmyObszarDzialania)\
                                 .filter(FirmyObszarDzialania.id_powiaty == powiat)

            wojewodztwo_empty_powiat_companies = db.session.query(Firmy.id_firmy)\
                                     .join(FirmyObszarDzialania)\
                                     .filter(
                                         and_(
                                             FirmyObszarDzialania.id_wojewodztwa == wojewodztwo_id,
                                             FirmyObszarDzialania.id_powiaty == 0
                                         )
                                     )

            combined_companies_ids_subquery = nationwide_companies.union(
                powiat_companies,
                wojewodztwo_empty_powiat_companies
            ).subquery()

        else:
             combined_companies_ids_subquery = nationwide_companies.subquery()

        query = query.filter(Firmy.id_firmy.in_(combined_companies_ids_subquery))

    elif wojewodztwo and not powiat:
        # Replicate wojewodztwo logic
        nationwide_companies = db.session.query(Firmy.id_firmy)\
                                 .join(FirmyObszarDzialania)\
                                 .filter(FirmyObszarDzialania.id_kraj == 'POL')

        wojewodztwo_companies = db.session.query(Firmy.id_firmy)\
                                 .join(FirmyObszarDzialania)\
                                 .filter(FirmyObszarDzialania.id_wojewodztwa == wojewodztwo)\
                                 .filter(FirmyObszarDzialania.id_powiaty == 0)\
                                 .except_(
                                     db.session.query(Firmy.id_firmy)\
                                     .join(FirmyObszarDzialania)\
                                     .filter(FirmyObszarDzialania.id_wojewodztwa == wojewodztwo)\
                                     .filter(FirmyObszarDzialania.id_powiaty != 0)
                                 )

        combined_companies_ids_subquery = nationwide_companies.union(wojewodztwo_companies).subquery()
        query = query.filter(Firmy.id_firmy.in_(combined_companies_ids_subquery))


    # Handle company type filter
    company_types = [ct for ct in request.args.getlist('company_types') if ct.strip()]
    if company_types:
        # Apply the filter to the current query state
        query = query.filter(Firmy.id_firmy_typ.in_(company_types))


    # EXECUTE THE FINAL FILTERED QUERY
    filtered_companies = query.all()

    # --- Fetch ALL related data for the filtered companies ---
    # Potrzebujemy wszystkich szczegółów, tak jak dla PDF.
    company_ids = [c.id_firmy for c in filtered_companies]

    # Fetch related data efficiently in batches
    related_data = {}
    if company_ids: # Only query if there are companies
        related_data['adresy'] = db.session.query(Adresy).filter(Adresy.id_firmy.in_(company_ids)).all()
        related_data['emails'] = db.session.query(Email).filter(Email.id_firmy.in_(company_ids)).all()
        related_data['telefony'] = db.session.query(Telefon).filter(Telefon.id_firmy.in_(company_ids)).all()
        related_data['osoby'] = db.session.query(Osoby).filter(Osoby.id_firmy.in_(company_ids)).all()
        related_data['oceny'] = db.session.query(Oceny).filter(Oceny.id_firmy.in_(company_ids)).all()
        related_data['obszary'] = db.session.query(FirmyObszarDzialania).filter(FirmyObszarDzialania.id_firmy.in_(company_ids)).all()
        related_data['specjalnosci'] = db.session.query(FirmySpecjalnosci).filter(FirmySpecjalnosci.id_firmy.in_(company_ids)).all()

        # Potrzebujemy szczegółów dla tabel powiązanych przez ID (Specjalnosci, Wojewodztwa, Powiaty, Kraj)
        specialty_ids = list(set([fs.id_specjalnosci for fs in related_data.get('specjalnosci', []) if fs.id_specjalnosci]))
        if specialty_ids:
             related_data['specialty_details'] = {s.id_specjalnosci: s for s in db.session.query(Specjalnosci).filter(Specjalnosci.id_specjalnosci.in_(specialty_ids)).all()}
        else:
             related_data['specialty_details'] = {}

        woj_ids = list(set([fo.id_wojewodztwa for fo in related_data.get('obszary', []) if fo.id_wojewodztwa]))
        powiat_ids = list(set([fo.id_powiaty for fo in related_data.get('obszary', []) if fo.id_powiaty]))
        if woj_ids:
            related_data['wojewodztwa_details'] = {w.id_wojewodztwa: w for w in db.session.query(Wojewodztwa).filter(Wojewodztwa.id_wojewodztwa.in_(woj_ids)).all()}
        else:
             related_data['wojewodztwa_details'] = {}
        if powiat_ids:
            related_data['powiaty_details'] = {p.id_powiaty: p for p in db.session.query(Powiaty).filter(Powiaty.id_powiaty.in_(powiat_ids)).all()}
        else:
             related_data['powiaty_details'] = {}
        # Zakładamy, że Kraj 'POL' jest stały lub można go pobrać jeśli potrzebne nazwy krajów innych niż Polska


    # Organizacja danych powiązanych wg ID firmy dla łatwego dostępu w szablonie
    organized_related_data = {company.id_firmy: {} for company in filtered_companies}
    for data_type, items in related_data.items():
         if '_details' in data_type: # Przechowuj szczegóły lookup'ów oddzielnie
             organized_related_data[data_type] = items
         else:
            for item in items:
                if item.id_firmy not in organized_related_data:
                     organized_related_data[item.id_firmy] = {}
                if data_type not in organized_related_data[item.id_firmy]:
                     organized_related_data[item.id_firmy][data_type] = []
                organized_related_data[item.id_firmy][data_type].append(item)


    # Renderuj szablon HTML do wydruku
    return render_template('export_companies_html.html',
                           companies=filtered_companies,
                           related_data=organized_related_data) # Przekaż zorganizowane dane

def normalize_text(text):
    if text is None:
        return ""
    text = str(text)
    normalized = unidecode(text).lower()
    return ''.join(c for c in normalized if c.isalnum() or c.isspace())