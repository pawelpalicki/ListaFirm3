from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify # Removed Response
from flask_login import current_user # Importujemy tylko 'current_user' (do użycia w szablonach/logice)

# WAŻNA UWAGA: Pozostałe Twoje importy są tutaj prawidłowe i powinny pozostać!
# Nie przenoś ich do __init__.py ani nie usuwaj.
from sqlalchemy import or_, and_, func
from app.models import Firmy, FirmyTyp, Adresy, AdresyTyp, Email, EmailTyp, Telefon, TelefonTyp, Specjalnosci, FirmySpecjalnosci, Kraj, Wojewodztwa, Powiaty, FirmyObszarDzialania, Osoby, Oceny
from app import db # Importujesz 'db' z zainicjalizowanej aplikacji
# unidecode is now used in app.utils
from app.forms import CompanyForm # Removed unused forms
from sqlalchemy.exc import SQLAlchemyError
from app.utils import normalize_text # Import normalize_text

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

def _get_filtered_companies_query(search_query=None, specialties_list=None, wojewodztwo_id=None, powiat_id=None, company_types_list=None):
    query = Firmy.query

    if search_query:
        normalized_search = normalize_text(search_query) # Use imported normalize_text
        # Using .contains for broader matching, similar to %term%
        # Using func.lower for case-insensitive search at DB level where possible
        
        matching_company_ids = set()

        # Search in Firmy
        firmy_q = db.session.query(Firmy.id_firmy).filter(
            or_(
                func.lower(Firmy.nazwa_firmy).contains(normalized_search),
                func.lower(Firmy.strona_www).contains(normalized_search),
                func.lower(Firmy.uwagi).contains(normalized_search)
            )
        )
        for firma in firmy_q.all():
            matching_company_ids.add(firma.id_firmy)

        # Search in Adresy
        adresy_q = db.session.query(Adresy.id_firmy).filter(
            Adresy.id_firmy.isnot(None) & # Ensure id_firmy is not NULL
            or_(
                func.lower(Adresy.kod).contains(normalized_search),
                func.lower(Adresy.miejscowosc).contains(normalized_search),
                func.lower(Adresy.ulica_miejscowosc).contains(normalized_search)
            )
        )
        for adres in adresy_q.all():
            matching_company_ids.add(adres.id_firmy)
        
        # Search in Email
        email_q = db.session.query(Email.id_firmy).filter(
            Email.id_firmy.isnot(None) &
            func.lower(Email.e_mail).contains(normalized_search)
        )
        for email in email_q.all():
            matching_company_ids.add(email.id_firmy)

        # Search in Telefon
        telefon_q = db.session.query(Telefon.id_firmy).filter(
            Telefon.id_firmy.isnot(None) &
            func.lower(Telefon.telefon).contains(normalized_search)
        )
        for telefon in telefon_q.all():
            matching_company_ids.add(telefon.id_firmy)

        # Search in Osoby
        osoby_q = db.session.query(Osoby.id_firmy).filter(
            Osoby.id_firmy.isnot(None) &
            or_(
                func.lower(Osoby.imie).contains(normalized_search),
                func.lower(Osoby.nazwisko).contains(normalized_search),
                func.lower(Osoby.stanowisko).contains(normalized_search),
                func.lower(Osoby.e_mail).contains(normalized_search),
                func.lower(Osoby.telefon).contains(normalized_search)
            )
        )
        for osoba in osoby_q.all():
            matching_company_ids.add(osoba.id_firmy)

        # Search in Oceny
        oceny_q = db.session.query(Oceny.id_firmy).filter(
            Oceny.id_firmy.isnot(None) &
            or_(
                func.lower(Oceny.osoba_oceniajaca).contains(normalized_search),
                func.lower(Oceny.budowa_dzial).contains(normalized_search),
                func.lower(Oceny.komentarz).contains(normalized_search)
            )
        )
        for ocena in oceny_q.all():
            matching_company_ids.add(ocena.id_firmy)

        # Search in Specjalnosci (via FirmySpecjalnosci)
        spec_q = db.session.query(FirmySpecjalnosci.id_firmy).join(Specjalnosci).filter(
            func.lower(Specjalnosci.specjalnosc).contains(normalized_search)
        )
        for spec in spec_q.all():
            matching_company_ids.add(spec.id_firmy)

        # Search in FirmyTyp (directly on Firmy or by joining FirmyTyp)
        ft_q = db.session.query(Firmy.id_firmy).join(FirmyTyp).filter(
            func.lower(FirmyTyp.typ_firmy).contains(normalized_search)
        )
        for ft in ft_q.all():
            matching_company_ids.add(ft.id_firmy)
        
        # Search in Wojewodztwa, Powiaty, Kraj (via FirmyObszarDzialania)
        fod_woj_q = db.session.query(FirmyObszarDzialania.id_firmy).join(Wojewodztwa).filter(
            func.lower(Wojewodztwa.wojewodztwo).contains(normalized_search)
        )
        for fod in fod_woj_q.all():
            matching_company_ids.add(fod.id_firmy)

        fod_pow_q = db.session.query(FirmyObszarDzialania.id_firmy).join(Powiaty).filter(
            func.lower(Powiaty.powiat).contains(normalized_search)
        )
        for fod in fod_pow_q.all():
            matching_company_ids.add(fod.id_firmy)

        fod_kraj_q = db.session.query(FirmyObszarDzialania.id_firmy).join(Kraj).filter(
            func.lower(Kraj.kraj).contains(normalized_search)
        )
        for fod in fod_kraj_q.all():
            matching_company_ids.add(fod.id_firmy)
            
        if matching_company_ids:
            query = query.filter(Firmy.id_firmy.in_(list(matching_company_ids)))
        else:
            # If search term is provided but no matches, return no results
            query = query.filter(False)


    if specialties_list:
        query = query.join(FirmySpecjalnosci)\
                     .filter(FirmySpecjalnosci.id_specjalnosci.in_(specialties_list))

    if powiat_id:
        nationwide_companies_subquery = db.session.query(Firmy.id_firmy)\
                                          .join(FirmyObszarDzialania)\
                                          .filter(FirmyObszarDzialania.id_kraj == 'POL')
        powiat_data = Powiaty.query.filter_by(id_powiaty=powiat_id).first()
        if powiat_data:
            wojewodztwo_id_for_powiat = powiat_data.id_wojewodztwa
            powiat_companies_subquery = db.session.query(Firmy.id_firmy)\
                                             .join(FirmyObszarDzialania)\
                                             .filter(FirmyObszarDzialania.id_powiaty == powiat_id)
            wojewodztwo_empty_powiat_companies_subquery = db.session.query(Firmy.id_firmy)\
                                                              .join(FirmyObszarDzialania)\
                                                              .filter(
                                                                  and_(
                                                                      FirmyObszarDzialania.id_wojewodztwa == wojewodztwo_id_for_powiat,
                                                                      FirmyObszarDzialania.id_powiaty == 0
                                                                  )
                                                              )
            combined_ids_subquery = nationwide_companies_subquery.union(
                powiat_companies_subquery, 
                wojewodztwo_empty_powiat_companies_subquery
            ).subquery()
        else:
            combined_ids_subquery = nationwide_companies_subquery.subquery()
        query = query.filter(Firmy.id_firmy.in_(combined_ids_subquery))

    elif wojewodztwo_id and not powiat_id: # Only wojewodztwo_id is present
        nationwide_companies_subquery = db.session.query(Firmy.id_firmy)\
                                          .join(FirmyObszarDzialania)\
                                          .filter(FirmyObszarDzialania.id_kraj == 'POL')
        wojewodztwo_companies_subquery = db.session.query(Firmy.id_firmy)\
                                           .join(FirmyObszarDzialania)\
                                           .filter(FirmyObszarDzialania.id_wojewodztwa == wojewodztwo_id)\
                                           .filter(FirmyObszarDzialania.id_powiaty == 0)\
                                           .except_(
                                               db.session.query(Firmy.id_firmy)\
                                               .join(FirmyObszarDzialania)\
                                               .filter(FirmyObszarDzialania.id_wojewodztwa == wojewodztwo_id)\
                                               .filter(FirmyObszarDzialania.id_powiaty != 0)
                                           )
        combined_ids_subquery = nationwide_companies_subquery.union(wojewodztwo_companies_subquery).subquery()
        query = query.filter(Firmy.id_firmy.in_(combined_ids_subquery))

    if company_types_list:
        query = query.filter(Firmy.id_firmy_typ.in_(company_types_list))
        
    return query

@main.route('/')
def index():
    search_term = request.args.get('search', '')
    specialties = request.args.getlist('specialties')
    wojewodztwo = request.args.get('wojewodztwo')
    powiat = request.args.get('powiat')
    company_types = [ct for ct in request.args.getlist('company_types') if ct.strip()]

    query = _get_filtered_companies_query(
        search_query=search_term,
        specialties_list=specialties,
        wojewodztwo_id=wojewodztwo,
        powiat_id=powiat,
        company_types_list=company_types
    )
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
                           all_company_types=all_company_types,
                           search_term=search_term, # Pass search term back to template
                           selected_specialties=specialties,
                           selected_wojewodztwo=wojewodztwo,
                           selected_powiat=powiat,
                           selected_company_types=company_types
                           )

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

@main.route('/export_companies_html')
def export_companies_html():
    # Ta funkcja będzie generować stronę HTML do wydruku/zapisu
    # Get filter parameters from request arguments
    search_term = request.args.get('search', '')
    specialties = request.args.getlist('specialties')
    wojewodztwo = request.args.get('wojewodztwo')
    powiat = request.args.get('powiat')
    company_types = [ct for ct in request.args.getlist('company_types') if ct.strip()]

    # Use the helper function to get the filtered query
    query = _get_filtered_companies_query(
        search_query=search_term,
        specialties_list=specialties,
        wojewodztwo_id=wojewodztwo,
        powiat_id=powiat,
        company_types_list=company_types
    )
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