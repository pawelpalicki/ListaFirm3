# app/routes/addresstype_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models import AdresyTyp # Corrected model name
from app.forms import AddressTypeForm # Form name
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func

addresstype_bp = Blueprint('addresstype_bp', __name__,
                           template_folder='../templates',
                           url_prefix='/address_types')

@addresstype_bp.route('/')
def list_address_types():
    address_types = AdresyTyp.query.all()
    # Adjusted add_url to point to the new blueprint
    return render_template('address_types.html', items=address_types, title='Typy Adresów', item_name='Typ Adresu', add_url=url_for('addresstype_bp.new_address_type'))

@addresstype_bp.route('/new', methods=['GET', 'POST'])
def new_address_type():
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
                return redirect(url_for('addresstype_bp.list_address_types'))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Wystąpił błąd podczas dodawania typu adresu: {e}', 'danger')
    return render_template('simple_form.html', form=form, title='Dodaj Typ Adresu', back_url=url_for('addresstype_bp.list_address_types'))

@addresstype_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit_address_type(id):
    address_type = AdresyTyp.query.get_or_404(id)
    form = AddressTypeForm(obj=address_type) # Pass obj for pre-population
    if request.method == 'GET':
        # Explicitly set the form data for the 'name' field from the model attribute 'typ_adresu'
        form.name.data = address_type.typ_adresu
        # No return here, let it fall through to the final render_template
        
    if form.validate_on_submit(): # This will be checked for POST
        try:
            # Sprawdzamy, czy inny typ adresu o tej nazwie już istnieje (case-insensitive)
            existing_type = AdresyTyp.query.filter(func.lower(AdresyTyp.typ_adresu) == func.lower(form.name.data), AdresyTyp.id_adresy_typ != id).first()
            if existing_type:
                flash('Typ adresu o tej nazwie już istnieje.', 'warning')
            else:
                address_type.typ_adresu = form.name.data
                db.session.commit()
                flash('Typ adresu został zaktualizowany pomyślnie!', 'success')
                return redirect(url_for('addresstype_bp.list_address_types'))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Wystąpił błąd podczas aktualizacji typu adresu: {e}', 'danger')
    # This render_template is for GET requests and for POST if validation fails
    return render_template('simple_form.html', form=form, title='Edytuj Typ Adresu', back_url=url_for('addresstype_bp.list_address_types'))

@addresstype_bp.route('/<int:id>/delete', methods=['POST'])
def delete_address_type(id):
    address_type = AdresyTyp.query.get_or_404(id)
    try:
        db.session.delete(address_type)
        db.session.commit()
        flash('Typ adresu został usunięty pomyślnie!', 'success')
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'Wystąpił błąd podczas usuwania typu adresu: {e}', 'danger')
    return redirect(url_for('addresstype_bp.list_address_types'))
