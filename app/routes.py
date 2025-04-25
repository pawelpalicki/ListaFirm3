from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from sqlalchemy import or_, func
from app.models import *
from app import db
from unidecode import unidecode
from app.forms import CompanyForm # Upewnij się, że CompanyForm jest importowany
from sqlalchemy.exc import SQLAlchemyError # Ważne: Importujemy SQLAlchemyError

main = Blueprint('main', __name__)

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
            if (normalized_search in normalize_text(firma.Nazwa_Firmy).lower() or
                normalized_search in normalize_text(firma.Strona_www).lower() or
                normalized_search in normalize_text(firma.Uwagi).lower()):
                matching_company_ids.add(firma.ID_FIRMY)

        # Wyszukiwanie w tabeli ADRESY
        adres_results = Adresy.query.all()
        for adres in adres_results:
            if (normalized_search in normalize_text(adres.Kod).lower() or
                normalized_search in normalize_text(adres.Miejscowosc).lower() or
                normalized_search in normalize_text(adres.Ulica_Miejscowosc).lower()):
                if adres.ID_FIRMY:
                    matching_company_ids.add(adres.ID_FIRMY)

        # Wyszukiwanie w tabeli EMAIL
        email_results = Email.query.all()
        for email in email_results:
            if normalized_search in normalize_text(email.e_mail).lower():
                if email.ID_FIRMY:
                    matching_company_ids.add(email.ID_FIRMY)

        # Wyszukiwanie w tabeli TELEFON
        telefon_results = Telefon.query.all()
        for telefon in telefon_results:
            if normalized_search in normalize_text(telefon.telefon).lower():
                if telefon.ID_FIRMY:
                    matching_company_ids.add(telefon.ID_FIRMY)

        # Wyszukiwanie w tabeli OSOBY
        osoby_results = Osoby.query.all()
        for osoba in osoby_results:
            if (normalized_search in normalize_text(osoba.Imie).lower() or
                normalized_search in normalize_text(osoba.Nazwisko).lower() or
                normalized_search in normalize_text(osoba.Stanowisko).lower() or
                normalized_search in normalize_text(osoba.e_mail).lower() or
                normalized_search in normalize_text(osoba.telefon).lower()):
                if osoba.ID_FIRMY:
                    matching_company_ids.add(osoba.ID_FIRMY)

        # Wyszukiwanie w tabeli OCENY
        oceny_results = Oceny.query.all()
        for ocena in oceny_results:
            if (normalized_search in normalize_text(ocena.Osoba_oceniajaca).lower() or
                normalized_search in normalize_text(ocena.Budowa_Dzial).lower() or
                normalized_search in normalize_text(ocena.Komentarz).lower()):
                if ocena.ID_FIRMY:
                    matching_company_ids.add(ocena.ID_FIRMY)

        # Wyszukiwanie w tabeli SPECJALNOSCI (przez relację)
        specjalnosci_results = Specjalnosci.query.all()
        for spec in specjalnosci_results:
            if normalized_search in normalize_text(spec.Specjalnosc).lower():
                firmy_spec = FirmySpecjalnosci.query.filter_by(ID_SPECJALNOSCI=spec.ID_SPECJALNOSCI).all()
                for fs in firmy_spec:
                    matching_company_ids.add(fs.ID_FIRMY)

        # Wyszukiwanie po typie firmy
        firmy_typ_results = FirmyTyp.query.all()
        for typ in firmy_typ_results:
            if normalized_search in normalize_text(typ.Typ_firmy).lower():
                firmy_by_typ = Firmy.query.filter_by(ID_FIRMY_TYP=typ.ID_FIRMY_TYP).all()
                for firma in firmy_by_typ:
                    matching_company_ids.add(firma.ID_FIRMY)

        # Wyszukiwanie po obszarze działania (województwa, powiaty, kraj)
        wojewodztwa_results = Wojewodztwa.query.all()
        for woj in wojewodztwa_results:
            if normalized_search in normalize_text(woj.Wojewodztwo).lower():
                firmy_woj = FirmyObszarDzialania.query.filter_by(ID_WOJEWODZTWA=woj.ID_WOJEWODZTWA).all()
                for fw in firmy_woj:
                    matching_company_ids.add(fw.ID_FIRMY)

        powiaty_results = Powiaty.query.all()
        for pow in powiaty_results:
            if normalized_search in normalize_text(pow.Powiat).lower():
                firmy_pow = FirmyObszarDzialania.query.filter_by(ID_POWIATY=pow.ID_POWIATY).all()
                for fp in firmy_pow:
                    matching_company_ids.add(fp.ID_FIRMY)

        kraje_results = Kraj.query.all()
        for kraj in kraje_results:
            if normalized_search in normalize_text(kraj.Kraj).lower():
                firmy_kraj = FirmyObszarDzialania.query.filter_by(ID_KRAJ=kraj.ID_KRAJ).all()
                for fk in firmy_kraj:
                    matching_company_ids.add(fk.ID_FIRMY)

        # Filtrowanie głównego zapytania, aby zawierało tylko firmy pasujące do wyszukiwania
        if matching_company_ids:
            query = query.filter(Firmy.ID_FIRMY.in_(matching_company_ids))
        else:
            # Jeśli nie znaleziono dopasowań, zwróć pustą listę
            query = query.filter(False)

    # Handle specialty filter
    specialties = request.args.getlist('specialties')
    if specialties:
        query = query.join(FirmySpecjalnosci)\
                    .filter(FirmySpecjalnosci.ID_SPECJALNOSCI.in_(specialties))
    
    # Handle area filter (województwo)
    wojewodztwo = request.args.get('wojewodztwo')
    if wojewodztwo:
        # Include companies with nationwide service
        nationwide_companies = db.session.query(Firmy.ID_FIRMY)\
                                .join(FirmyObszarDzialania)\
                                .filter(FirmyObszarDzialania.ID_KRAJ == 'POL')
        
        # Companies serving in the selected wojewodztwo
        wojewodztwo_companies = db.session.query(Firmy.ID_FIRMY)\
                                .join(FirmyObszarDzialania)\
                                .filter(FirmyObszarDzialania.ID_WOJEWODZTWA == wojewodztwo)
        
        query = query.filter(Firmy.ID_FIRMY.in_(nationwide_companies.union(wojewodztwo_companies)))
    
    # Handle area filter (powiat)
    powiat = request.args.get('powiat')
    if powiat:
        # Include companies with nationwide service
        nationwide_companies = db.session.query(Firmy.ID_FIRMY)\
                                .join(FirmyObszarDzialania)\
                                .filter(FirmyObszarDzialania.ID_KRAJ == 'POL')
        
        # Companies serving in the selected powiat's wojewodztwo
        powiat_data = Powiaty.query.filter_by(ID_POWIATY=powiat).first()
        if powiat_data:
            wojewodztwo_id = powiat_data.ID_WOJEWODZTWA
            wojewodztwo_companies = db.session.query(Firmy.ID_FIRMY)\
                                    .join(FirmyObszarDzialania)\
                                    .filter(FirmyObszarDzialania.ID_WOJEWODZTWA == wojewodztwo_id)
        else:
            wojewodztwo_companies = db.session.query(Firmy.ID_FIRMY).filter(False)
        
        # Companies serving in the selected powiat
        powiat_companies = db.session.query(Firmy.ID_FIRMY)\
                            .join(FirmyObszarDzialania)\
                            .filter(FirmyObszarDzialania.ID_POWIATY == powiat)
        
        query = query.filter(Firmy.ID_FIRMY.in_(nationwide_companies.union(wojewodztwo_companies, powiat_companies)))
    
    # Handle company type filter
    company_types = [ct for ct in request.args.getlist('company_types') if ct.strip()]
    if company_types:
        query = query.filter(Firmy.ID_FIRMY_TYP.in_(company_types))

    
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

@main.route('/company/<int:company_id>')
def company_details(company_id):
    company = Firmy.query.get_or_404(company_id)
    
    # Calculate average rating
    avg_rating = db.session.query(func.avg(Oceny.Ocena))\
                          .filter(Oceny.ID_FIRMY == company_id)\
                          .scalar() or 0
    avg_rating = round(avg_rating, 1)
    
    # Get area of operation
    nationwide = db.session.query(FirmyObszarDzialania)\
                          .filter(FirmyObszarDzialania.ID_FIRMY == company_id,
                                  FirmyObszarDzialania.ID_KRAJ == 'POL')\
                          .first() is not None
    
    wojewodztwa = db.session.query(Wojewodztwa)\
                           .join(FirmyObszarDzialania)\
                           .filter(FirmyObszarDzialania.ID_FIRMY == company_id)\
                           .all()
    
    powiaty = db.session.query(Powiaty, Wojewodztwa.ID_WOJEWODZTWA)\
                       .join(FirmyObszarDzialania, Powiaty.ID_POWIATY == FirmyObszarDzialania.ID_POWIATY)\
                       .join(Wojewodztwa, Powiaty.ID_WOJEWODZTWA == Wojewodztwa.ID_WOJEWODZTWA)\
                       .filter(FirmyObszarDzialania.ID_FIRMY == company_id)\
                       .all()
    
    # Get company specialties
    specialties = db.session.query(Specjalnosci)\
                           .join(FirmySpecjalnosci)\
                           .filter(FirmySpecjalnosci.ID_FIRMY == company_id)\
                           .all()
    
    return render_template('company_details.html',
                          company=company,
                          avg_rating=avg_rating,
                          nationwide=nationwide,
                          wojewodztwa=wojewodztwa,
                          powiaty=powiaty,
                          specialties=specialties)

@main.route('/api/powiaty/<wojewodztwo_id>')
def get_powiaty(wojewodztwo_id):
    powiaty = Powiaty.query.filter_by(ID_WOJEWODZTWA=wojewodztwo_id).all()
    return jsonify([{'id': p.ID_POWIATY, 'name': p.Powiat} for p in powiaty])




@main.route('/api/adres_typ', methods=['POST'])
def add_adres_typ():
    data = request.json
    if not data or 'name' not in data:
        return jsonify({'error': 'Brak wymaganych danych'}), 400

    try:
        # Sprawdzamy, czy typ już istnieje
        existing = AdresyTyp.query.filter_by(Typ_adresu=data['name']).first()
        if existing:
            return jsonify({'error': 'Ten typ adresu już istnieje', 'id': existing.ID_ADRESY_TYP}), 400

        # Dodajemy nowy typ adresu
        max_id = db.session.query(db.func.max(AdresyTyp.ID_ADRESY_TYP)).scalar() or 0
        new_typ = AdresyTyp(ID_ADRESY_TYP=max_id + 1, Typ_adresu=data['name'])
        db.session.add(new_typ)
        db.session.commit()

        return jsonify({'id': new_typ.ID_ADRESY_TYP, 'name': new_typ.Typ_adresu}), 201
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
        existing = EmailTyp.query.filter_by(Typ_emaila=data['name']).first()
        if existing:
            return jsonify({'error': 'Ten typ emaila już istnieje', 'id': existing.ID_EMAIL_TYP}), 400

        # Dodajemy nowy typ emaila
        max_id = db.session.query(db.func.max(EmailTyp.ID_EMAIL_TYP)).scalar() or 0
        new_typ = EmailTyp(ID_EMAIL_TYP=max_id + 1, Typ_emaila=data['name'])
        db.session.add(new_typ)
        db.session.commit()

        return jsonify({'id': new_typ.ID_EMAIL_TYP, 'name': new_typ.Typ_emaila}), 201
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
        existing = TelefonTyp.query.filter_by(Typ_telefonu=data['name']).first()
        if existing:
            return jsonify({'error': 'Ten typ telefonu już istnieje', 'id': existing.ID_TELEFON_TYP}), 400

        # Dodajemy nowy typ telefonu
        max_id = db.session.query(db.func.max(TelefonTyp.ID_TELEFON_TYP)).scalar() or 0
        new_typ = TelefonTyp(ID_TELEFON_TYP=max_id + 1, Typ_telefonu=data['name'])
        db.session.add(new_typ)
        db.session.commit()

        return jsonify({'id': new_typ.ID_TELEFON_TYP, 'name': new_typ.Typ_telefonu}), 201
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
        existing = FirmyTyp.query.filter_by(Typ_firmy=data['name']).first()
        if existing:
            return jsonify({'error': 'Ten typ firmy już istnieje', 'id': existing.ID_FIRMY_TYP}), 400

        # Dodajemy nowy typ firmy
        # Dla ID_FIRMY_TYP możemy stworzyć nowy identyfikator tekstowy
        import uuid
        new_id = str(uuid.uuid4())[:8].upper()  # Skrócony UUID jako identyfikator
        new_typ = FirmyTyp(ID_FIRMY_TYP=new_id, Typ_firmy=data['name'])
        db.session.add(new_typ)
        db.session.commit()

        return jsonify({'id': new_typ.ID_FIRMY_TYP, 'name': new_typ.Typ_firmy}), 201
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
        existing = Specjalnosci.query.filter_by(Specjalnosc=data['name']).first()
        if existing:
            return jsonify({'error': 'Ta specjalność już istnieje', 'id': existing.ID_SPECJALNOSCI}), 400

        # Dodajemy nową specjalność
        max_id = db.session.query(db.func.max(Specjalnosci.ID_SPECJALNOSCI)).scalar() or 0
        new_spec = Specjalnosci(ID_SPECJALNOSCI=max_id + 1, Specjalnosc=data['name'])
        db.session.add(new_spec)
        db.session.commit()

        return jsonify({'id': new_spec.ID_SPECJALNOSCI, 'name': new_spec.Specjalnosc}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@main.route('/company/new', methods=['GET', 'POST'])
def new_company():
    from app.forms import CompanyForm
    form = CompanyForm()
    
    if form.validate_on_submit():
        # Create new company
        company = Firmy(
            Nazwa_Firmy=form.nazwa_firmy.data,
            ID_FIRMY_TYP=form.typ_firmy.data,
            Strona_www=form.strona_www.data,
            Uwagi=form.uwagi.data
        )
        db.session.add(company)
        db.session.flush()  # Get the ID of the new company
        
        # Add addresses
        for address_form in form.adresy:
            if address_form.miejscowosc.data:  # Only add if miejscowosc is provided
                address = Adresy(
                    Kod=address_form.kod.data,
                    Miejscowosc=address_form.miejscowosc.data,
                    Ulica_Miejscowosc=address_form.ulica_miejscowosc.data,
                    ID_ADRESY_TYP=address_form.typ_adresu.data,
                    ID_FIRMY=company.ID_FIRMY
                )
                db.session.add(address)
        
        # Add emails
        for email_form in form.emaile:
            if email_form.email.data:  # Only add if email is provided
                email = Email(
                    e_mail=email_form.email.data,
                    ID_EMAIL_TYP=email_form.typ_emaila.data,
                    ID_FIRMY=company.ID_FIRMY
                )
                db.session.add(email)
        
        # Add phones
        for phone_form in form.telefony:
            if phone_form.telefon.data:  # Only add if phone is provided
                phone = Telefon(
                    telefon=phone_form.telefon.data,
                    ID_TELEFON_TYP=phone_form.typ_telefonu.data,
                    ID_FIRMY=company.ID_FIRMY
                )
                db.session.add(phone)
        
        # Add people
        for person_form in form.osoby:
            if person_form.imie.data and person_form.nazwisko.data:  # Only add if name is provided
                person = Osoby(
                    Imie=person_form.imie.data,
                    Nazwisko=person_form.nazwisko.data,
                    Stanowisko=person_form.stanowisko.data,
                    e_mail=person_form.email.data,
                    telefon=person_form.telefon.data,
                    ID_FIRMY=company.ID_FIRMY
                )
                db.session.add(person)
        
        # Add ratings
        for rating_form in form.oceny:
            if rating_form.osoba_oceniajaca.data:  # Only add if osoba_oceniajaca is provided
                rating = Oceny(
                    Osoba_oceniajaca=rating_form.osoba_oceniajaca.data,
                    Budowa_Dzial=rating_form.budowa_dzial.data,
                    Rok_wspolpracy=rating_form.rok_wspolpracy.data,
                    Ocena=rating_form.ocena.data,
                    Komentarz=rating_form.komentarz.data,
                    ID_FIRMY=company.ID_FIRMY
                )
                db.session.add(rating)
        
        # Add area of operation
        if form.kraj.data == 'POL':
            # Add nationwide operation
            obszar = FirmyObszarDzialania(
                ID_FIRMY=company.ID_FIRMY,
                ID_KRAJ='POL',
                ID_WOJEWODZTWA='',
                ID_POWIATY=0
            )
            db.session.add(obszar)
        else:
            # Add wojewodztwa
            for woj_id in form.wojewodztwa.data:
                obszar = FirmyObszarDzialania(
                    ID_FIRMY=company.ID_FIRMY,
                    ID_KRAJ='',
                    ID_WOJEWODZTWA=woj_id,
                    ID_POWIATY=0
                )
                db.session.add(obszar)
            
            # Add powiaty
            for pow_id in form.powiaty.data:
                # Get the wojewodztwo for this powiat
                powiat = Powiaty.query.get(pow_id)
                obszar = FirmyObszarDzialania(
                    ID_FIRMY=company.ID_FIRMY,
                    ID_KRAJ='',
                    ID_WOJEWODZTWA=powiat.ID_WOJEWODZTWA,
                    ID_POWIATY=pow_id
                )
                db.session.add(obszar)
        
        # Add specialties
        for spec_id in form.specjalnosci.data:
            spec = FirmySpecjalnosci(
                ID_FIRMY=company.ID_FIRMY,
                ID_SPECJALNOSCI=spec_id
            )
            db.session.add(spec)
        
        db.session.commit()
        flash('Firma została dodana pomyślnie!', 'success')
        return redirect(url_for('main.company_details', company_id=company.ID_FIRMY))
    
    return render_template('company_form.html', form=form, title='Nowa firma')

@main.route('/company/<int:company_id>/edit', methods=['GET', 'POST'])
def edit_company(company_id):
    # from app.forms import CompanyForm # Przenosimy import formularza na początek modułu
    company = Firmy.query.get_or_404(company_id)

    if request.method == 'GET':
        form = CompanyForm(obj=company)

        # Populate address forms
        while len(form.adresy) < len(company.adresy):
            form.adresy.append_entry()
        for i, address in enumerate(company.adresy):
            form.adresy[i].typ_adresu.data = address.ID_ADRESY_TYP
            form.adresy[i].kod.data = address.Kod
            form.adresy[i].miejscowosc.data = address.Miejscowosc
            form.adresy[i].ulica_miejscowosc.data = address.Ulica_Miejscowosc

        # Populate email forms
        while len(form.emaile) < len(company.emaile):
            form.emaile.append_entry()
        for i, email in enumerate(company.emaile):
            form.emaile[i].typ_emaila.data = email.ID_EMAIL_TYP
            form.emaile[i].email.data = email.e_mail

        # Populate phone forms
        while len(form.telefony) < len(company.telefony):
            form.telefony.append_entry()
        for i, phone in enumerate(company.telefony):
            form.telefony[i].typ_telefonu.data = phone.ID_TELEFON_TYP
            form.telefony[i].telefon.data = phone.telefon

        # Populate person forms
        while len(form.osoby) < len(company.osoby):
            form.osoby.append_entry()
        for i, person in enumerate(company.osoby):
            form.osoby[i].imie.data = person.Imie
            form.osoby[i].nazwisko.data = person.Nazwisko
            form.osoby[i].stanowisko.data = person.Stanowisko
            form.osoby[i].email.data = person.e_mail
            form.osoby[i].telefon.data = person.telefon

        # Populate rating forms
        while len(form.oceny) < len(company.oceny):
            form.oceny.append_entry()
        for i, rating in enumerate(company.oceny):
            form.oceny[i].osoba_oceniajaca.data = rating.Osoba_oceniajaca
            form.oceny[i].budowa_dzial.data = rating.Budowa_Dzial
            form.oceny[i].rok_wspolpracy.data = rating.Rok_wspolpracy
            form.oceny[i].ocena.data = rating.Ocena
            form.oceny[i].komentarz.data = rating.Komentarz

        # Populate area of operation
        nationwide = db.session.query(FirmyObszarDzialania).filter(
            FirmyObszarDzialania.ID_FIRMY == company_id,
            FirmyObszarDzialania.ID_KRAJ == 'POL'
        ).first() is not None
        if nationwide:
            form.kraj.data = 'POL'
        else:
            wojewodztwa_ids = [
                w.ID_WOJEWODZTWA
                for w in db.session.query(FirmyObszarDzialania).filter(
                    FirmyObszarDzialania.ID_FIRMY == company_id,
                    FirmyObszarDzialania.ID_WOJEWODZTWA != ''
                ).distinct()
            ]
            form.wojewodztwa.data = wojewodztwa_ids

            powiaty_ids = [
                p.ID_POWIATY
                for p in db.session.query(FirmyObszarDzialania).filter(
                    FirmyObszarDzialania.ID_FIRMY == company_id,
                    FirmyObszarDzialania.ID_POWIATY != 0
                ).all()
            ]
            form.powiaty.data = powiaty_ids

        # Populate specialties
        specialties = [
            s.ID_SPECJALNOSCI
            for s in db.session.query(FirmySpecjalnosci).filter(
                FirmySpecjalnosci.ID_FIRMY == company_id
            ).all()
        ]
        form.specjalnosci.data = specialties

        return render_template('company_edit_form.html', form=form, title='Edycja firmy') # Dodano przekazywanie form do szablonu

    else:
        form = CompanyForm() # Inicjalizacja formularza dla POST
        if form.validate_on_submit():
            try:
                # Update company basic info
                company.Nazwa_Firmy = form.nazwa_firmy.data
                company.ID_FIRMY_TYP = form.typ_firmy.data
                company.Strona_www = form.strona_www.data
                company.Uwagi = form.uwagi.data

                # Remove existing related data
                db.session.query(Adresy).filter(Adresy.ID_FIRMY == company_id).delete()
                db.session.query(Email).filter(Email.ID_FIRMY == company_id).delete()
                db.session.query(Telefon).filter(Telefon.ID_FIRMY == company_id).delete()
                db.session.query(Osoby).filter(Osoby.ID_FIRMY == company_id).delete()
                db.session.query(Oceny).filter(Oceny.ID_FIRMY == company_id).delete()
                db.session.query(FirmyObszarDzialania).filter(FirmyObszarDzialania.ID_FIRMY == company_id).delete()
                db.session.query(FirmySpecjalnosci).filter(FirmySpecjalnosci.ID_FIRMY == company_id).delete()

                # Add addresses
                if form.adresy: # Sprawdzamy, czy lista adresów nie jest pusta
                    for address_form in form.adresy:
                        if address_form.miejscowosc.data: # Dodatkowy warunek, czy miejscowość została wprowadzona
                            address = Adresy(
                                Kod=address_form.kod.data,
                                Miejscowosc=address_form.miejscowosc.data,
                                Ulica_Miejscowosc=address_form.ulica_miejscowosc.data,
                                ID_ADRESY_TYP=address_form.typ_adresu.data,
                                ID_FIRMY=company_id
                            )
                            db.session.add(address)

                # Add emails
                if form.emaile:
                    for email_form in form.emaile:
                        if email_form.email.data:
                            email = Email(
                                e_mail=email_form.email.data,
                                ID_EMAIL_TYP=email_form.typ_emaila.data,
                                ID_FIRMY=company_id
                            )
                            db.session.add(email)

                # Add phones
                if form.telefony:
                    for phone_form in form.telefony:
                        if phone_form.telefon.data:
                            phone = Telefon(
                                telefon=phone_form.telefon.data,
                                ID_TELEFON_TYP=phone_form.typ_telefonu.data,
                                ID_FIRMY=company_id
                            )
                            db.session.add(phone)

                # Add people
                if form.osoby:
                    for person_form in form.osoby:
                        if person_form.imie.data and person_form.nazwisko.data:
                            person = Osoby(
                                Imie=person_form.imie.data,
                                Nazwisko=person_form.nazwisko.data,
                                Stanowisko=person_form.stanowisko.data,
                                e_mail=person_form.email.data,
                                telefon=person_form.telefon.data,
                                ID_FIRMY=company_id
                            )
                            db.session.add(person)

                # Add ratings
                if form.oceny:
                    for rating_form in form.oceny:
                        if rating_form.osoba_oceniajaca.data:
                            rating = Oceny(
                                Osoba_oceniajaca=rating_form.osoba_oceniajaca.data,
                                Budowa_Dzial=rating_form.budowa_dzial.data,
                                Rok_wspolpracy=rating_form.rok_wspolpracy.data,
                                Ocena=rating_form.ocena.data,
                                Komentarz=rating_form.komentarz.data,
                                ID_FIRMY=company_id
                            )
                            db.session.add(rating)

                # Add area of operation
                if form.kraj.data == 'POL':
                    obszar = FirmyObszarDzialania(
                        ID_FIRMY=company_id,
                        ID_KRAJ='POL',
                        ID_WOJEWODZTWA='',
                        ID_POWIATY=0
                    )
                    db.session.add(obszar)
                else:
                    if form.wojewodztwa.data:  # Dodano sprawdzenie, czy wojewodztwa są wybrane
                        for woj_id in form.wojewodztwa.data:
                            obszar = FirmyObszarDzialania(
                                ID_FIRMY=company_id,
                                ID_KRAJ='',
                                ID_WOJEWODZTWA=woj_id,
                                ID_POWIATY=0
                            )
                            db.session.add(obszar)

                    if form.powiaty.data: # Dodano sprawdzenie, czy powiaty są wybrane
                        for pow_id in form.powiaty.data:
                            powiat = Powiaty.query.get(pow_id)
                            if powiat: # Dodano sprawdzenie, czy powiat istnieje
                                obszar = FirmyObszarDzialania(
                                    ID_FIRMY=company_id,
                                    ID_KRAJ='',
                                    ID_WOJEWODZTWA=powiat.ID_WOJEWODZTWA,
                                    ID_POWIATY=pow_id
                                )
                                db.session.add(obszar)

                # Add specialties
                if form.specjalnosci.data:
                    for spec_id in form.specjalnosci.data:
                        spec = FirmySpecjalnosci(
                            ID_FIRMY=company_id,
                            ID_SPECJALNOSCI=spec_id
                        )
                        db.session.add(spec)

                db.session.commit()
                flash('Firma została zaktualizowana pomyślnie!', 'success')
                return redirect(url_for('main.company_details', company_id=company_id))
            except SQLAlchemyError as e: # Obsługa błędów bazy danych
                db.session.rollback()
                flash(f'Wystąpił błąd podczas aktualizacji firmy: {e}', 'error')
                return render_template('company_edit_form.html', form=form, title='Edycja firmy') # Dodano context
        else:
            return render_template('company_edit_form.html', form=form, title='Edycja firmy') # Dodano context



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
            existing_spec = Specjalnosci.query.filter(func.lower(Specjalnosci.Specjalnosc) == func.lower(form.name.data)).first()
            if existing_spec:
                flash('Specjalność o tej nazwie już istnieje.', 'warning')
            else:
                max_id = db.session.query(func.max(Specjalnosci.ID_SPECJALNOSCI)).scalar() or 0
                new_spec = Specjalnosci(ID_SPECJALNOSCI=max_id + 1, Specjalnosc=form.name.data)
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
        form.name.data = specialty.Specjalnosc
        return render_template('simple_form.html', form=form, title='Edytuj Specjalność', back_url=url_for('main.list_specialties'))
    else: # POST request
        if form.validate_on_submit():
            try:
                # Sprawdzamy, czy inna specjalność o tej nazwie już istnieje (case-insensitive)
                existing_spec = Specjalnosci.query.filter(func.lower(Specjalnosci.Specjalnosc) == func.lower(form.name.data), Specjalnosci.ID_SPECJALNOSCI != id).first()
                if existing_spec:
                    flash('Specjalność o tej nazwie już istnieje.', 'warning')
                else:
                    specialty.Specjalnosc = form.name.data
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
            existing_type = AdresyTyp.query.filter(func.lower(AdresyTyp.Typ_adresu) == func.lower(form.name.data)).first()
            if existing_type:
                flash('Typ adresu o tej nazwie już istnieje.', 'warning')
            else:
                max_id = db.session.query(func.max(AdresyTyp.ID_ADRESY_TYP)).scalar() or 0
                new_type = AdresyTyp(ID_ADRESY_TYP=max_id + 1, Typ_adresu=form.name.data)
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
         # Explicitly set the form data for the 'name' field from the model attribute 'Typ_adresu'
        form.name.data = address_type.Typ_adresu
        return render_template('simple_form.html', form=form, title='Edytuj Typ Adresu', back_url=url_for('main.list_address_types'))
    else: # POST request
        if form.validate_on_submit():
            try:
                # Sprawdzamy, czy inny typ adresu o tej nazwie już istnieje (case-insensitive)
                existing_type = AdresyTyp.query.filter(func.lower(AdresyTyp.Typ_adresu) == func.lower(form.name.data), AdresyTyp.ID_ADRESY_TYP != id).first()
                if existing_type:
                    flash('Typ adresu o tej nazwie już istnieje.', 'warning')
                else:
                    address_type.Typ_adresu = form.name.data
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
            existing_type = EmailTyp.query.filter(func.lower(EmailTyp.Typ_emaila) == func.lower(form.name.data)).first()
            if existing_type:
                flash('Typ emaila o tej nazwie już istnieje.', 'warning')
            else:
                max_id = db.session.query(func.max(EmailTyp.ID_EMAIL_TYP)).scalar() or 0
                new_type = EmailTyp(ID_EMAIL_TYP=max_id + 1, Typ_emaila=form.name.data)
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
        form.name.data = email_type.Typ_emaila
        return render_template('simple_form.html', form=form, title='Edytuj Typ E-maila', back_url=url_for('main.list_email_types'))
    else: # POST request
        if form.validate_on_submit():
            try:
                # Sprawdzamy, czy inny typ emaila o tej nazwie już istnieje (case-insensitive)
                existing_type = EmailTyp.query.filter(func.lower(EmailTyp.Typ_emaila) == func.lower(form.name.data), EmailTyp.ID_EMAIL_TYP != id).first()
                if existing_type:
                    flash('Typ emaila o tej nazwie już istnieje.', 'warning')
                else:
                    email_type.Typ_emaila = form.name.data
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
            existing_type = TelefonTyp.query.filter(func.lower(TelefonTyp.Typ_telefonu) == func.lower(form.name.data)).first()
            if existing_type:
                flash('Typ telefonu o tej nazwie już istnieje.', 'warning')
            else:
                max_id = db.session.query(func.max(TelefonTyp.ID_TELEFON_TYP)).scalar() or 0
                new_type = TelefonTyp(ID_TELEFON_TYP=max_id + 1, Typ_telefonu=form.name.data)
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
        form.name.data = phone_type.Typ_telefonu
        return render_template('simple_form.html', form=form, title='Edytuj Typ Telefonu', back_url=url_for('main.list_phone_types'))
    else: # POST request
        if form.validate_on_submit():
            try:
                # Sprawdzamy, czy inny typ telefonu o tej nazwie już istnieje (case-insensitive)
                existing_type = TelefonTyp.query.filter(func.lower(TelefonTyp.Typ_telefonu) == func.lower(form.name.data), TelefonTyp.ID_TELEFON_TYP != id).first()
                if existing_type:
                    flash('Typ telefonu o tej nazwie już istnieje.', 'warning')
                else:
                    phone_type.Typ_telefonu = form.name.data
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
            existing_type = FirmyTyp.query.filter(func.lower(FirmyTyp.Typ_firmy) == func.lower(form.name.data)).first()
            if existing_type:
                flash('Typ firmy o tej nazwie już istnieje.', 'warning')
            else:
                # Generate a unique ID for FirmyTyp (using UUID snippet from previous try)
                import uuid
                new_id = str(uuid.uuid4())[:8].upper() # Skrócony UUID jako identyfikator
                new_type = FirmyTyp(ID_FIRMY_TYP=new_id, Typ_firmy=form.name.data)
                db.session.add(new_type)
                db.session.commit()
                flash('Typ firmy został dodany pomyślnie!', 'success')
                return redirect(url_for('main.list_company_types'))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Wystąpił błąd podczas dodawania typu firmy: {e}', 'danger')
    return render_template('simple_form.html', form=form, title='Dodaj Typ Firmy', back_url=url_for('main.list_company_types'))

@main.route('/company_types/<string:id>/edit', methods=['GET', 'POST'])
def edit_company_type(id):
    from app.forms import CompanyTypeForm # Local import
    company_type = FirmyTyp.query.get_or_404(id)
    form = CompanyTypeForm(obj=company_type)
    if request.method == 'GET':
         # Explicitly set the form data for the 'name' field from the model attribute 'Typ_firmy'
        form.name.data = company_type.Typ_firmy
        return render_template('simple_form.html', form=form, title='Edytuj Typ Firmy', back_url=url_for('main.list_company_types'))
    else: # POST request
        if form.validate_on_submit():
            try:
                # Check if another company type with this name already exists (case-insensitive)
                existing_type = FirmyTyp.query.filter(func.lower(FirmyTyp.Typ_firmy) == func.lower(form.name.data), FirmyTyp.ID_FIRMY_TYP != id).first()
                if existing_type:
                     flash('Typ firmy o tej nazwie już istnieje.', 'warning')
                else:
                    company_type.Typ_firmy = form.name.data
                    db.session.commit()
                    flash('Typ firmy został zaktualizowany pomyślnie!', 'success')
                    return redirect(url_for('main.list_company_types'))
            except SQLAlchemyError as e:
                db.session.rollback()
                flash(f'Wystąpił błąd podczas aktualizacji typu firmy: {e}', 'danger')
        return render_template('simple_form.html', form=form, title='Edytuj Typ Firmy', back_url=url_for('main.list_company_types'))

@main.route('/company_types/<string:id>/delete', methods=['POST'])
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