# app/routes/phonetype_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models import TelefonTyp # Corrected model name
from app.forms import PhoneTypeForm # Form name
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func

phonetype_bp = Blueprint('phonetype_bp', __name__,
                         template_folder='../templates',
                         url_prefix='/phone_types')

@phonetype_bp.route('/')
def list_phone_types():
    phone_types = TelefonTyp.query.all()
    # Adjusted add_url to point to the new blueprint
    return render_template('phone_types.html', items=phone_types, title='Typy Telefonów', item_name='Typ Telefonu', add_url=url_for('phonetype_bp.new_phone_type'))

@phonetype_bp.route('/new', methods=['GET', 'POST'])
def new_phone_type():
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
                return redirect(url_for('phonetype_bp.list_phone_types'))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Wystąpił błąd podczas dodawania typu telefonu: {e}', 'danger')
    return render_template('simple_form.html', form=form, title='Dodaj Typ Telefonu', back_url=url_for('phonetype_bp.list_phone_types'))

@phonetype_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit_phone_type(id):
    phone_type = TelefonTyp.query.get_or_404(id)
    form = PhoneTypeForm(obj=phone_type) # Pass obj for pre-population
    if request.method == 'GET':
        # Explicitly set the form data for the 'name' field from the model attribute 'typ_telefonu'
        form.name.data = phone_type.typ_telefonu
        # No return here, let it fall through to the final render_template

    if form.validate_on_submit(): # This will be checked for POST
        try:
            # Sprawdzamy, czy inny typ telefonu o tej nazwie już istnieje (case-insensitive)
            existing_type = TelefonTyp.query.filter(func.lower(TelefonTyp.typ_telefonu) == func.lower(form.name.data), TelefonTyp.id_telefon_typ != id).first()
            if existing_type:
                flash('Typ telefonu o tej nazwie już istnieje.', 'warning')
            else:
                phone_type.typ_telefonu = form.name.data
                db.session.commit()
                flash('Typ telefonu został zaktualizowany pomyślnie!', 'success')
                return redirect(url_for('phonetype_bp.list_phone_types'))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Wystąpił błąd podczas aktualizacji typu telefonu: {e}', 'danger')
    # This render_template is for GET requests and for POST if validation fails
    return render_template('simple_form.html', form=form, title='Edytuj Typ Telefonu', back_url=url_for('phonetype_bp.list_phone_types'))

@phonetype_bp.route('/<int:id>/delete', methods=['POST'])
def delete_phone_type(id):
    phone_type = TelefonTyp.query.get_or_404(id)
    try:
        db.session.delete(phone_type)
        db.session.commit()
        flash('Typ telefonu został usunięty pomyślnie!', 'success')
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'Wystąpił błąd podczas usuwania typu telefonu: {e}', 'danger')
    return redirect(url_for('phonetype_bp.list_phone_types'))
