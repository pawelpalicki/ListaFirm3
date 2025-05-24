# app/routes/rating_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user
from app import db
from app.models import Oceny
from app.forms import SimpleRatingForm
from sqlalchemy.exc import SQLAlchemyError

rating_bp = Blueprint('rating_bp', __name__,
                      template_folder='../templates',
                      url_prefix='/ratings')

@rating_bp.before_request
def require_login_for_rating_bp():
    # Allow access to auth routes and static files without login
    if request.endpoint and (
        request.endpoint.startswith('auth.') or
        request.endpoint == 'static'
    ):
        return

    if not current_user.is_authenticated:
        flash("Musisz się zalogować, aby uzyskać dostęp do tej strony.", "warning")
        return redirect(url_for('auth.login', next=request.url))

@rating_bp.route('/')
def list_ratings():
    ratings = Oceny.query.all()
    return render_template('ratings.html', items=ratings, title='Oceny Współpracy', item_name='Ocena', add_url=url_for('rating_bp.new_rating'))

@rating_bp.route('/new', methods=['GET', 'POST'])
def new_rating():
    form = SimpleRatingForm()
    if form.validate_on_submit():
        try:
            new_rating = Oceny(
                osoba_oceniajaca=form.osoba_oceniajaca.data,
                budowa_dzial=form.budowa_dzial.data,
                rok_wspolpracy=form.rok_wspolpracy.data,
                ocena=form.ocena.data,
                komentarz=form.komentarz.data,
                id_firmy=form.id_firmy.data
            )
            db.session.add(new_rating)
            db.session.commit()
            flash('Ocena została dodana pomyślnie!', 'success')
            return redirect(url_for('rating_bp.list_ratings'))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Wystąpił błąd podczas dodawania oceny: {e}', 'danger')
    return render_template('rating_form.html', form=form, title='Dodaj Ocenę Współpracy', back_url=url_for('rating_bp.list_ratings'))

@rating_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit_rating(id):
    rating = Oceny.query.get_or_404(id)
    form = SimpleRatingForm(obj=rating)
    if form.validate_on_submit():
        try:
            rating.osoba_oceniajaca = form.osoba_oceniajaca.data
            rating.budowa_dzial = form.budowa_dzial.data
            rating.rok_wspolpracy = form.rok_wspolpracy.data
            rating.ocena = form.ocena.data
            rating.komentarz = form.komentarz.data
            rating.id_firmy = form.id_firmy.data
            db.session.commit()
            flash('Ocena została zaktualizowana pomyślnie!', 'success')
            return redirect(url_for('rating_bp.list_ratings'))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Wystąpił błąd podczas aktualizacji oceny: {e}', 'danger')
    return render_template('rating_form.html', form=form, title='Edytuj Ocenę Współpracy', back_url=url_for('rating_bp.list_ratings'))

@rating_bp.route('/<int:id>/delete', methods=['POST'])
def delete_rating(id):
    rating = Oceny.query.get_or_404(id)
    try:
        db.session.delete(rating)
        db.session.commit()
        flash('Ocena została usunięta pomyślnie!', 'success')
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'Wystąpił błąd podczas usuwania oceny: {e}', 'danger')
    return redirect(url_for('rating_bp.list_ratings'))
