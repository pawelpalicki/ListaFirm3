# app/routes/specialty_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models import Specjalnosci # Corrected model name
from app.forms import SpecialtyForm # Form name seems to be English
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func

specialty_bp = Blueprint('specialty_bp', __name__,
                        template_folder='../templates',
                        url_prefix='/specialties')

@specialty_bp.route('/')
def list_specialties():
    specialties = Specjalnosci.query.all()
    # Adjusted add_url to point to the new blueprint
    return render_template('specialties.html', items=specialties, title='Specjalności', item_name='Specjalność', add_url=url_for('specialty_bp.new_specialty'))

@specialty_bp.route('/new', methods=['GET', 'POST'])
def new_specialty():
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
                return redirect(url_for('specialty_bp.list_specialties'))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Wystąpił błąd podczas dodawania specjalności: {e}', 'danger')
    return render_template('simple_form.html', form=form, title='Dodaj Specjalność', back_url=url_for('specialty_bp.list_specialties'))

@specialty_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit_specialty(id):
    specialty = Specjalnosci.query.get_or_404(id)
    form = SpecialtyForm(obj=specialty) # Pass obj for pre-population
    if request.method == 'GET':
        # Explicitly set the form data for the 'name' field from the model attribute 'specjalnosc'
        form.name.data = specialty.specjalnosc 
        # No return here, let it fall through to the final render_template
    
    if form.validate_on_submit(): # This will be checked for POST
        try:
            # Sprawdzamy, czy inna specjalność o tej nazwie już istnieje (case-insensitive)
            existing_spec = Specjalnosci.query.filter(func.lower(Specjalnosci.specjalnosc) == func.lower(form.name.data), Specjalnosci.id_specjalnosci != id).first()
            if existing_spec:
                flash('Specjalność o tej nazwie już istnieje.', 'warning')
            else:
                specialty.specjalnosc = form.name.data
                db.session.commit()
                flash('Specjalność została zaktualizowana pomyślnie!', 'success')
                return redirect(url_for('specialty_bp.list_specialties'))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Wystąpił błąd podczas aktualizacji specjalności: {e}', 'danger')
    # This render_template is for GET requests and for POST if validation fails
    return render_template('simple_form.html', form=form, title='Edytuj Specjalność', back_url=url_for('specialty_bp.list_specialties'))

@specialty_bp.route('/<int:id>/delete', methods=['POST'])
def delete_specialty(id):
    specialty = Specjalnosci.query.get_or_404(id)
    try:
        db.session.delete(specialty)
        db.session.commit()
        flash('Specjalność została usunięta pomyślnie!', 'success')
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'Wystąpił błąd podczas usuwania specjalności: {e}', 'danger')
    return redirect(url_for('specialty_bp.list_specialties'))
