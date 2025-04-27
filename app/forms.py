from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SelectMultipleField, IntegerField, FormField, FieldList, SubmitField
from wtforms.validators import DataRequired, Email, Optional, NumberRange
from wtforms.widgets import ListWidget, CheckboxInput, Select

# Zamiast tworzenia własnych widgetów, użyjmy atrybutów HTML i klas CSS
class Select2MultipleField(SelectMultipleField):
    def __init__(self, label=None, validators=None, **kwargs):
        super(Select2MultipleField, self).__init__(label, validators, **kwargs)
        # Dodajemy klasę CSS dla łatwej identyfikacji przez JavaScript
        self.render_kw = {"class": "select2-multiple", "data-placeholder": "Wybierz opcje..."}

class AddressForm(FlaskForm):
    typ_adresu = SelectField('Typ adresu', coerce=int)
    kod = StringField('Kod pocztowy')
    miejscowosc = StringField('Miejscowość', validators=[Optional()]) # Zmieniono na Optional, jeśli nie jest wymagane w pustym szablonie
    ulica_miejscowosc = StringField('Ulica/Miejscowość', validators=[Optional()]) # Zmieniono na Optional

class EmailForm(FlaskForm):
    typ_emaila = SelectField('Typ emaila', coerce=int)
    email = StringField('Email', validators=[Optional(), Email()]) # Dodano Optional

class PhoneForm(FlaskForm):
    typ_telefonu = SelectField('Typ telefonu', coerce=int)
    telefon = StringField('Telefon', validators=[Optional()]) # Dodano Optional

class PersonForm(FlaskForm):
    imie = StringField('Imię', validators=[DataRequired()])
    nazwisko = StringField('Nazwisko', validators=[DataRequired()])
    stanowisko = StringField('Stanowisko')
    email = StringField('Email', validators=[Optional(), ])
    telefon = StringField('Telefon')

class RatingForm(FlaskForm):
    osoba_oceniajaca = StringField('Osoba oceniająca', validators=[DataRequired()])
    budowa_dzial = StringField('Budowa/Dział', validators=[DataRequired()])
    rok_wspolpracy = IntegerField('Rok współpracy', validators=[DataRequired()])
    ocena = IntegerField('Ocena (1-5)', validators=[DataRequired(), NumberRange(min=1, max=5)])
    komentarz = TextAreaField('Komentarz')

class CompanyForm(FlaskForm):
    nazwa_firmy = StringField('Nazwa firmy', validators=[DataRequired()])
    typ_firmy = SelectField('Typ firmy')
    strona_www = StringField('Strona WWW', validators=[Optional()]) # Dodano Optional
    uwagi = TextAreaField('Uwagi')

    # Areas of operation
    kraj = SelectField('Kraj działania', choices=[('', 'Brak'), ('POL', 'Cały kraj')], default='')
    # Zmiana na Select2MultipleField
    wojewodztwa = Select2MultipleField('Województwa', coerce=str)
    powiaty = Select2MultipleField('Powiaty', coerce=int)

    # Specialties
    specjalnosci = Select2MultipleField('Specjalności', coerce=int)

    # Related data
    # Używamy min_entries=0, aby lista mogła być pusta
    adresy = FieldList(FormField(AddressForm), min_entries=0)
    emaile = FieldList(FormField(EmailForm), min_entries=0)
    telefony = FieldList(FormField(PhoneForm), min_entries=0)
    osoby = FieldList(FormField(PersonForm), min_entries=0)
    oceny = FieldList(FormField(RatingForm), min_entries=0)

    # Dodano atrybuty do przechowywania opcji dla szablonów
    address_type_choices = []
    email_type_choices = []
    phone_type_choices = []
    company_type_choices = []
    specialty_choices = []
    wojewodztwa_choices = []
    # Powiaty są ładowane dynamicznie, więc nie potrzebujemy ich tutaj dla szablonu

    def __init__(self, *args, **kwargs):
        super(CompanyForm, self).__init__(*args, **kwargs)
        # Importy modeli wewnątrz, aby uniknąć problemów z cyklicznym importem
        from app.models import FirmyTyp, AdresyTyp, EmailTyp, TelefonTyp, Wojewodztwa, Powiaty, Specjalnosci
        from app import db

        # Załaduj opcje i zapisz je jako atrybuty instancji
        self.company_type_choices = [(t.ID_FIRMY_TYP, t.Typ_firmy) for t in FirmyTyp.query.order_by(FirmyTyp.Typ_firmy).all()]
        self.typ_firmy.choices = self.company_type_choices

        self.address_type_choices = [(t.ID_ADRESY_TYP, t.Typ_adresu) for t in AdresyTyp.query.order_by(AdresyTyp.Typ_adresu).all()]
        # Ustaw opcje dla istniejących wpisów ORAZ dla pola szablonu (jeśli WTForms go udostępnia - ale my użyjemy self.address_type_choices)
        for adres_entry in self.adresy:
            adres_entry.typ_adresu.choices = self.address_type_choices
        # if hasattr(self.adresy, 'template'): # Sprawdzenie, czy WTForms udostępnia szablon - zazwyczaj nie
        #     self.adresy.template.typ_adresu.choices = self.address_type_choices

        self.email_type_choices = [(t.ID_EMAIL_TYP, t.Typ_emaila) for t in EmailTyp.query.order_by(EmailTyp.Typ_emaila).all()]
        for email_entry in self.emaile:
            email_entry.typ_emaila.choices = self.email_type_choices

        self.phone_type_choices = [(t.ID_TELEFON_TYP, t.Typ_telefonu) for t in TelefonTyp.query.order_by(TelefonTyp.Typ_telefonu).all()]
        for telefon_entry in self.telefony:
            telefon_entry.typ_telefonu.choices = self.phone_type_choices

        self.wojewodztwa_choices = [(w.ID_WOJEWODZTWA, w.Wojewodztwo) for w in Wojewodztwa.query.order_by(Wojewodztwa.Wojewodztwo).all()]
        self.wojewodztwa.choices = self.wojewodztwa_choices
        # Dla powiatów - ładujemy wszystkie jako początkowe opcje, JS je przefiltruje
        self.powiaty.choices = [(p.ID_POWIATY, f"{p.Powiat} ({p.wojewodztwo.Wojewodztwo if p.wojewodztwo else 'Brak woj.'})") for p in Powiaty.query.order_by(Powiaty.Powiat).all()]


        self.specialty_choices = [(s.ID_SPECJALNOSCI, s.Specjalnosc) for s in Specjalnosci.query.order_by(Specjalnosci.Specjalnosc).all()]
        self.specjalnosci.choices = self.specialty_choices

class SimplePersonForm(FlaskForm):
    # Użyj nazw atrybutów z modelu Osoby
    Imie = StringField('Imię', validators=[DataRequired()])
    Nazwisko = StringField('Nazwisko', validators=[DataRequired()])
    Stanowisko = StringField('Stanowisko')
    e_mail = StringField('E-mail', validators=[Optional(), Email()]) 
    telefon = StringField('Telefon') 
    ID_FIRMY = SelectField('Firma', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Zapisz')

    def __init__(self, *args, **kwargs):
        super(SimplePersonForm, self).__init__(*args, **kwargs)
        # Importuj model wewnątrz metody, jeśli chcesz uniknąć problemów z cyklicznym importem
        from app.models import Firmy
        # Załaduj opcje do poprawnego pola (ID_FIRMY)
        # Dodano order_by dla lepszej użyteczności listy rozwijanej
        self.ID_FIRMY.choices = [(f.ID_FIRMY, f.Nazwa_Firmy) for f in Firmy.query.order_by(Firmy.Nazwa_Firmy).all()]
        # Dodaj pustą opcję na początku, jeśli pole nie zawsze musi być wybrane od razu
        self.ID_FIRMY.choices.insert(0, (0, '--- Wybierz ---')) 

class SimpleRatingForm(FlaskForm):
    # Użyj nazw atrybutów z modelu Osoby
    Osoba_oceniajaca = StringField('Osoba oceniająca', validators=[DataRequired()])
    Budowa_Dzial = StringField('Budowa/Dział', validators=[DataRequired()])
    Rok_wspolpracy = IntegerField('Rok współpracy', validators=[DataRequired()])
    Ocena = IntegerField('Ocena (1-5)', validators=[DataRequired(), NumberRange(min=1, max=5)])
    Komentarz = TextAreaField('Komentarz')
    ID_FIRMY = SelectField('Firma', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Zapisz')

    def __init__(self, *args, **kwargs):
        super(SimpleRatingForm, self).__init__(*args, **kwargs)
        from app.models import Firmy
        # Load companies for dropdown
        self.ID_FIRMY.choices = [(f.ID_FIRMY, f.Nazwa_Firmy) for f in Firmy.query.order_by(Firmy.Nazwa_Firmy).all()]
        # dodaj pustą opcję na początku, jeśli pole nie zawsze musi być wybrane od razu
        self.ID_FIRMY.choices.insert(0, (0, '--- Wybierz ---')) # Pamiętaj o walidatorze DataRequired, jeśli dodasz pustą opcję


# Forms for adding/editing the four tables
class SpecialtyForm(FlaskForm):
    name = StringField('Nazwa Specjalności', validators=[DataRequired()])
    submit = SubmitField('Zapisz')

class AddressTypeForm(FlaskForm):
    name = StringField('Nazwa Typu Adresu', validators=[DataRequired()])
    submit = SubmitField('Zapisz')

class EmailTypeForm(FlaskForm):
    name = StringField('Nazwa Typu E-maila', validators=[DataRequired()])
    submit = SubmitField('Zapisz')

class PhoneTypeForm(FlaskForm):
    name = StringField('Nazwa Typu Telefonu', validators=[DataRequired()])
    submit = SubmitField('Zapisz')

class CompanyTypeForm(FlaskForm):
    name = StringField('Nazwa Typu Firmy', validators=[DataRequired()])
    submit = SubmitField('Zapisz')