from app import db

class Firmy(db.Model):
    __tablename__ = 'FIRMY'
    ID_FIRMY = db.Column(db.Integer, primary_key=True)
    Nazwa_Firmy = db.Column(db.Text)
    ID_FIRMY_TYP = db.Column(db.Text, db.ForeignKey('FIRMY_TYP.ID_FIRMY_TYP'))
    Strona_www = db.Column(db.Text)
    Uwagi = db.Column(db.Text)
    
    adresy = db.relationship('Adresy', backref='firma', lazy='dynamic')
    emails = db.relationship('Email', backref='firma', lazy='dynamic')
    telefony = db.relationship('Telefon', backref='firma', lazy='dynamic')
    osoby = db.relationship('Osoby', backref='firma', lazy='dynamic')
    oceny = db.relationship('Oceny', backref='firma', lazy='dynamic')
    
    firmy_specjalnosci = db.relationship('FirmySpecjalnosci', backref='firma', lazy='dynamic')
    firmy_obszar_dzialania = db.relationship('FirmyObszarDzialania', backref='firma', lazy='dynamic')

class FirmyTyp(db.Model):
    __tablename__ = 'FIRMY_TYP'
    ID_FIRMY_TYP = db.Column(db.Text, primary_key=True)
    Typ_firmy = db.Column(db.Text)
    
    firmy = db.relationship('Firmy', backref='typ_firmy', lazy='dynamic')

class AdresyTyp(db.Model):
    __tablename__ = 'ADRESY_TYP'
    ID_ADRESY_TYP = db.Column(db.Integer, primary_key=True)
    Typ_adresu = db.Column(db.Text)
    
    adresy = db.relationship('Adresy', backref='typ_adresu', lazy='dynamic')

class Adresy(db.Model):
    __tablename__ = 'ADRESY'
    ID_ADRESY = db.Column(db.Integer, primary_key=True)
    Kod = db.Column(db.Text)
    Miejscowosc = db.Column(db.Text)
    Ulica_Miejscowosc = db.Column(db.Text)
    ID_ADRESY_TYP = db.Column(db.Integer, db.ForeignKey('ADRESY_TYP.ID_ADRESY_TYP'))
    ID_FIRMY = db.Column(db.Integer, db.ForeignKey('FIRMY.ID_FIRMY'))

class EmailTyp(db.Model):
    __tablename__ = 'EMAIL_TYP'
    ID_EMAIL_TYP = db.Column(db.Integer, primary_key=True)
    Typ_emaila = db.Column(db.Text)
    
    emails = db.relationship('Email', backref='typ_emaila', lazy='dynamic')

class Email(db.Model):
    __tablename__ = 'EMAIL'
    ID_EMAIL = db.Column(db.Integer, primary_key=True)
    e_mail = db.Column(db.Text)
    ID_EMAIL_TYP = db.Column(db.Integer, db.ForeignKey('EMAIL_TYP.ID_EMAIL_TYP'))
    ID_FIRMY = db.Column(db.Integer, db.ForeignKey('FIRMY.ID_FIRMY'))

class TelefonTyp(db.Model):
    __tablename__ = 'TELEFON_TYP'
    ID_TELEFON_TYP = db.Column(db.Integer, primary_key=True)
    Typ_telefonu = db.Column(db.Text)
    
    telefony = db.relationship('Telefon', backref='typ_telefonu', lazy='dynamic')

class Telefon(db.Model):
    __tablename__ = 'TELEFON'
    ID_TELEFON = db.Column(db.Integer, primary_key=True)
    telefon = db.Column(db.Text)
    ID_TELEFON_TYP = db.Column(db.Integer, db.ForeignKey('TELEFON_TYP.ID_TELEFON_TYP'))
    ID_FIRMY = db.Column(db.Integer, db.ForeignKey('FIRMY.ID_FIRMY'))

class Specjalnosci(db.Model):
    __tablename__ = 'SPECJALNOSCI'
    ID_SPECJALNOSCI = db.Column(db.Integer, primary_key=True)
    Specjalnosc = db.Column(db.Text)
    
    firmy_specjalnosci = db.relationship('FirmySpecjalnosci', backref='specjalnosc', lazy='dynamic')

class FirmySpecjalnosci(db.Model):
    __tablename__ = 'FIRMYSPECJALNOSCI'
    ID_FIRMY = db.Column(db.Integer, db.ForeignKey('FIRMY.ID_FIRMY'), primary_key=True)
    ID_SPECJALNOSCI = db.Column(db.Integer, db.ForeignKey('SPECJALNOSCI.ID_SPECJALNOSCI'), primary_key=True)

class Kraj(db.Model):
    __tablename__ = 'KRAJ'
    ID_KRAJ = db.Column(db.Text, primary_key=True)
    Kraj = db.Column(db.Text)
    
    firmy_obszar_dzialania = db.relationship('FirmyObszarDzialania', backref='kraj', lazy='dynamic')

class Wojewodztwa(db.Model):
    __tablename__ = 'WOJEWODZTWA'
    ID_WOJEWODZTWA = db.Column(db.Text, primary_key=True)
    Wojewodztwo = db.Column(db.Text)
    
    powiaty = db.relationship('Powiaty', backref='wojewodztwo', lazy='dynamic')
    firmy_obszar_dzialania = db.relationship('FirmyObszarDzialania', backref='wojewodztwo', lazy='dynamic')

class Powiaty(db.Model):
    __tablename__ = 'POWIATY'
    ID_POWIATY = db.Column(db.Integer, primary_key=True)
    Powiat = db.Column(db.Text)
    ID_WOJEWODZTWA = db.Column(db.Text, db.ForeignKey('WOJEWODZTWA.ID_WOJEWODZTWA'))
    
    firmy_obszar_dzialania = db.relationship('FirmyObszarDzialania', backref='powiat', lazy='dynamic')

class FirmyObszarDzialania(db.Model):
    __tablename__ = 'FIRMYOBSZARDZIALANIA'
    ID_FIRMY = db.Column(db.Integer, db.ForeignKey('FIRMY.ID_FIRMY'), primary_key=True)
    ID_KRAJ = db.Column(db.Text, db.ForeignKey('KRAJ.ID_KRAJ'), primary_key=True)
    ID_WOJEWODZTWA = db.Column(db.Text, db.ForeignKey('WOJEWODZTWA.ID_WOJEWODZTWA'), primary_key=True)
    ID_POWIATY = db.Column(db.Integer, db.ForeignKey('POWIATY.ID_POWIATY'), primary_key=True)

class Osoby(db.Model):
    __tablename__ = 'OSOBY'
    ID_OSOBY = db.Column(db.Integer, primary_key=True)
    Imie = db.Column(db.Text)
    Nazwisko = db.Column(db.Text)
    Stanowisko = db.Column(db.Text)
    e_mail = db.Column(db.Text)
    telefon = db.Column(db.Text)
    ID_FIRMY = db.Column(db.Integer, db.ForeignKey('FIRMY.ID_FIRMY'))

class Oceny(db.Model):
    __tablename__ = 'OCENY'
    OCENY_ID = db.Column(db.Integer, primary_key=True)
    Osoba_oceniajaca = db.Column(db.Text)
    Budowa_Dzial = db.Column(db.Text)
    Rok_wspolpracy = db.Column(db.Integer)
    Ocena = db.Column(db.Integer)
    Komentarz = db.Column(db.Text)
    ID_FIRMY = db.Column(db.Integer, db.ForeignKey('FIRMY.ID_FIRMY'))