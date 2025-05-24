# app/routes/person_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models import Osoby
from app.forms import SimplePersonForm
from sqlalchemy.exc import SQLAlchemyError

person_bp = Blueprint('person_bp', __name__,
                      template_folder='../templates',
                      url_prefix='/persons')

@person_bp.route('/')
def list_persons():
    persons = Osoby.query.all()
    return render_template('persons.html', items=persons, title='Osoby Kontaktowe', item_name='Osoba Kontaktowa', add_url=url_for('person_bp.new_person'))

@person_bp.route('/new', methods=['GET', 'POST'])
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
            return redirect(url_for('person_bp.list_persons'))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Wystąpił błąd podczas dodawania osoby kontaktowej: {e}', 'danger')
    return render_template('person_form.html', form=form, title='Dodaj Osobę Kontaktową', back_url=url_for('person_bp.list_persons'))

@person_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit_person(id):
    person = Osoby.query.get_or_404(id)
    form = SimplePersonForm(obj=person) 

    if form.validate_on_submit():
        try:
            person.imie = form.imie.data
            person.nazwisko = form.nazwisko.data
            person.stanowisko = form.stanowisko.data
            person.e_mail = form.e_mail.data 
            person.telefon = form.telefon.data 
            person.id_firmy = form.id_firmy.data 
            db.session.commit()
            flash('Osoba kontaktowa została zaktualizowana pomyślnie!', 'success')
            return redirect(url_for('person_bp.list_persons'))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Wystąpił błąd podczas aktualizacji osoby kontaktowej: {e}', 'danger')

    return render_template('person_form.html', form=form, title='Edytuj Osobę Kontaktową', back_url=url_for('person_bp.list_persons'))

@person_bp.route('/<int:id>/delete', methods=['POST'])
def delete_person(id):
    person = Osoby.query.get_or_404(id)
    try:
        db.session.delete(person)
        db.session.commit()
        flash('Osoba kontaktowa została usunięta pomyślnie!', 'success')
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'Wystąpił błąd podczas usuwania osoby kontaktowej: {e}', 'danger')
    return redirect(url_for('person_bp.list_persons'))
