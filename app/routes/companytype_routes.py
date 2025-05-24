# app/routes/companytype_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user
from app import db
from app.models import FirmyTyp # Corrected model name
from app.forms import CompanyTypeForm # Form name
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func

companytype_bp = Blueprint('companytype_bp', __name__,
                           template_folder='../templates',
                           url_prefix='/company_types')

@companytype_bp.before_request
def require_login_for_companytype_bp():
    # Allow access to auth routes and static files without login
    if request.endpoint and (
        request.endpoint.startswith('auth.') or
        request.endpoint == 'static'
    ):
        return

    if not current_user.is_authenticated:
        flash("Musisz się zalogować, aby uzyskać dostęp do tej strony.", "warning")
        return redirect(url_for('auth.login', next=request.url))

@companytype_bp.route('/')
def list_company_types():
    company_types = FirmyTyp.query.all()
    # Adjusted add_url to point to the new blueprint
    return render_template('company_types.html', items=company_types, title='Typy Firm', item_name='Typ Firmy', add_url=url_for('companytype_bp.new_company_type'))

@companytype_bp.route('/new', methods=['GET', 'POST'])
def new_company_type():
    form = CompanyTypeForm()
    if form.validate_on_submit():
        try:
            # Check if company type already exists (case-insensitive)
            existing_type = FirmyTyp.query.filter(func.lower(FirmyTyp.typ_firmy) == func.lower(form.name.data)).first()
            if existing_type:
                flash('Typ firmy o tej nazwie już istnieje.', 'warning')
            else:
                new_type = FirmyTyp(typ_firmy=form.name.data)
                db.session.add(new_type)
                db.session.commit()
                flash('Typ firmy został dodany pomyślnie!', 'success')
                return redirect(url_for('companytype_bp.list_company_types'))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Wystąpił błąd podczas dodawania typu firmy: {e}', 'danger')
    return render_template('simple_form.html', form=form, title='Dodaj Typ Firmy', back_url=url_for('companytype_bp.list_company_types'))

@companytype_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit_company_type(id):
    company_type = FirmyTyp.query.get_or_404(id)
    form = CompanyTypeForm(obj=company_type) # Pass obj for pre-population
    if request.method == 'GET':
        # Explicitly set the form data for the 'name' field from the model attribute 'typ_firmy'
        form.name.data = company_type.typ_firmy
        # No return here, let it fall through to the final render_template

    if form.validate_on_submit(): # This will be checked for POST
        try:
            # Check if another company type with this name already exists (case-insensitive)
            existing_type = FirmyTyp.query.filter(func.lower(FirmyTyp.typ_firmy) == func.lower(form.name.data), FirmyTyp.id_firmy_typ != id).first()
            if existing_type:
                flash('Typ firmy o tej nazwie już istnieje.', 'warning')
            else:
                company_type.typ_firmy = form.name.data
                db.session.commit()
                flash('Typ firmy został zaktualizowany pomyślnie!', 'success')
                return redirect(url_for('companytype_bp.list_company_types'))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Wystąpił błąd podczas aktualizacji typu firmy: {e}', 'danger')
    # This render_template is for GET requests and for POST if validation fails
    return render_template('simple_form.html', form=form, title='Edytuj Typ Firmy', back_url=url_for('companytype_bp.list_company_types'))

@companytype_bp.route('/<int:id>/delete', methods=['POST'])
def delete_company_type(id):
    company_type = FirmyTyp.query.get_or_404(id)
    try:
        db.session.delete(company_type)
        db.session.commit()
        flash('Typ firmy został usunięty pomyślnie!', 'success')
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'Wystąpił błąd podczas usuwania typu firmy: {e}', 'danger')
    return redirect(url_for('companytype_bp.list_company_types'))
