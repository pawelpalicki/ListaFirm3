# app/routes/emailtype_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models import EmailTyp # Corrected model name
from app.forms import EmailTypeForm # Form name
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func

emailtype_bp = Blueprint('emailtype_bp', __name__,
                         template_folder='../templates',
                         url_prefix='/email_types')

@emailtype_bp.route('/')
def list_email_types():
    email_types = EmailTyp.query.all()
    # Adjusted add_url to point to the new blueprint
    return render_template('email_types.html', items=email_types, title='Typy E-maili', item_name='Typ E-maila', add_url=url_for('emailtype_bp.new_email_type'))

@emailtype_bp.route('/new', methods=['GET', 'POST'])
def new_email_type():
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
                return redirect(url_for('emailtype_bp.list_email_types'))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Wystąpił błąd podczas dodawania typu emaila: {e}', 'danger')
    return render_template('simple_form.html', form=form, title='Dodaj Typ E-maila', back_url=url_for('emailtype_bp.list_email_types'))

@emailtype_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit_email_type(id):
    email_type = EmailTyp.query.get_or_404(id)
    form = EmailTypeForm(obj=email_type) # Pass obj for pre-population
    if request.method == 'GET':
        # Explicitly set the form data for the 'name' field from the model attribute 'typ_emaila'
        form.name.data = email_type.typ_emaila
        # No return here, let it fall through to the final render_template

    if form.validate_on_submit(): # This will be checked for POST
        try:
            # Sprawdzamy, czy inny typ emaila o tej nazwie już istnieje (case-insensitive)
            existing_type = EmailTyp.query.filter(func.lower(EmailTyp.typ_emaila) == func.lower(form.name.data), EmailTyp.id_email_typ != id).first()
            if existing_type:
                flash('Typ emaila o tej nazwie już istnieje.', 'warning')
            else:
                email_type.typ_emaila = form.name.data
                db.session.commit()
                flash('Typ emaila został zaktualizowany pomyślnie!', 'success')
                return redirect(url_for('emailtype_bp.list_email_types'))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Wystąpił błąd podczas aktualizacji typu emaila: {e}', 'danger')
    # This render_template is for GET requests and for POST if validation fails
    return render_template('simple_form.html', form=form, title='Edytuj Typ E-maila', back_url=url_for('emailtype_bp.list_email_types'))

@emailtype_bp.route('/<int:id>/delete', methods=['POST'])
def delete_email_type(id):
    email_type = EmailTyp.query.get_or_404(id)
    try:
        db.session.delete(email_type)
        db.session.commit()
        flash('Typ emaila został usunięty pomyślnie!', 'success')
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'Wystąpił błąd podczas usuwania typu emaila: {e}', 'danger')
    return redirect(url_for('emailtype_bp.list_email_types'))
