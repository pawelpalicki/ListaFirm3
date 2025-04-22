from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SelectMultipleField, IntegerField, FormField, FieldList
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
    miejscowosc = StringField('Miejscowość', validators=[DataRequired()])
    ulica_miejscowosc = StringField('Ulica/Miejscowość', validators=[DataRequired()])

class EmailForm(FlaskForm):
    typ_emaila = SelectField('Typ emaila', coerce=int)
    email = StringField('Email', validators=[DataRequired(), Email()])

class PhoneForm(FlaskForm):
    typ_telefonu = SelectField('Typ telefonu', coerce=int)
    telefon = StringField('Telefon', validators=[DataRequired()])

class PersonForm(FlaskForm):
    imie = StringField('Imię', validators=[DataRequired()])
    nazwisko = StringField('Nazwisko', validators=[DataRequired()])
    stanowisko = StringField('Stanowisko')
    email = StringField('Email', validators=[Optional(), Email()])
    telefon = StringField('Telefon')

class RatingForm(FlaskForm):
    osoba_oceniajaca = StringField('Osoba oceniająca', validators=[DataRequired()])
    budowa_dzial = StringField('Budowa/Dział', validators=[DataRequired()])
    rok_wspolpracy = IntegerField('Rok współpracy', validators=[DataRequired()])
    ocena = IntegerField('Ocena (1-5)', validators=[DataRequired(), NumberRange(min=1, max=5)])
    komentarz = TextAreaField('Komentarz')

class CompanyForm(FlaskForm):
    nazwa_firmy = TextAreaField('Nazwa firmy', validators=[DataRequired()])
    typ_firmy = SelectField('Typ firmy')
    strona_www = StringField('Strona WWW')
    uwagi = TextAreaField('Uwagi')

    # Areas of operation
    kraj = SelectField('Kraj działania', choices=[('', 'Brak'), ('POL', 'Cały kraj')])
    # Zmiana na Select2MultipleField
    wojewodztwa = Select2MultipleField('Województwa', coerce=str)
    powiaty = Select2MultipleField('Powiaty', coerce=int)

    # Specialties
    specjalnosci = Select2MultipleField('Specjalności', coerce=int)

    # Related data
    adresy = FieldList(FormField(AddressForm), min_entries=1)
    emaile = FieldList(FormField(EmailForm), min_entries=1)
    telefony = FieldList(FormField(PhoneForm), min_entries=1)
    osoby = FieldList(FormField(PersonForm), min_entries=1)
    oceny = FieldList(FormField(RatingForm), min_entries=1)

    def __init__(self, *args, **kwargs):
        super(CompanyForm, self).__init__(*args, **kwargs)
        from app.models import FirmyTyp, AdresyTyp, EmailTyp, TelefonTyp, Wojewodztwa, Powiaty, Specjalnosci
        from app import db

        # Load data for dropdowns
        self.typ_firmy.choices = [(t.ID_FIRMY_TYP, t.Typ_firmy) for t in FirmyTyp.query.all()]

        # Load data for address type dropdown in all address forms
        address_types = [(t.ID_ADRESY_TYP, t.Typ_adresu) for t in AdresyTyp.query.all()]
        for form in self.adresy:
            form.typ_adresu.choices = address_types

        # Load data for email type dropdown in all email forms
        email_types = [(t.ID_EMAIL_TYP, t.Typ_emaila) for t in EmailTyp.query.all()]
        for form in self.emaile:
            form.typ_emaila.choices = email_types

        # Load data for phone type dropdown in all phone forms
        phone_types = [(t.ID_TELEFON_TYP, t.Typ_telefonu) for t in TelefonTyp.query.all()]
        for form in self.telefony:
            form.typ_telefonu.choices = phone_types

        # Load data for wojewodztwa and powiaty
        self.wojewodztwa.choices = [(w.ID_WOJEWODZTWA, w.Wojewodztwo) for w in Wojewodztwa.query.all()]
        self.powiaty.choices = [(p.ID_POWIATY, f"{p.Powiat} ({p.ID_WOJEWODZTWA})") for p in Powiaty.query.all()]

        # Load data for specialties
        self.specjalnosci.choices = [(s.ID_SPECJALNOSCI, s.Specjalnosc) for s in Specjalnosci.query.all()]

class SimplePersonForm(FlaskForm):
    imie = StringField('Imię', validators=[DataRequired()])
    nazwisko = StringField('Nazwisko', validators=[DataRequired()])
    stanowisko = StringField('Stanowisko')
    email = StringField('Email', validators=[Optional(), Email()])
    telefon = StringField('Telefon')
    firma = SelectField('Firma', coerce=int, validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        super(SimplePersonForm, self).__init__(*args, **kwargs)
        from app.models import Firmy
        # Load companies for dropdown
        self.firma.choices = [(f.ID_FIRMY, f.Nazwa_Firmy) for f in Firmy.query.all()]

class SimpleRatingForm(FlaskForm):
    osoba_oceniajaca = StringField('Osoba oceniająca', validators=[DataRequired()])
    budowa_dzial = StringField('Budowa/Dział', validators=[DataRequired()])
    rok_wspolpracy = IntegerField('Rok współpracy', validators=[DataRequired()])
    ocena = IntegerField('Ocena (1-5)', validators=[DataRequired(), NumberRange(min=1, max=5)])
    komentarz = TextAreaField('Komentarz')
    firma = SelectField('Firma', coerce=int, validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        super(SimpleRatingForm, self).__init__(*args, **kwargs)
        from app.models import Firmy
        # Load companies for dropdown
        self.firma.choices = [(f.ID_FIRMY, f.Nazwa_Firmy) for f in Firmy.query.all()]