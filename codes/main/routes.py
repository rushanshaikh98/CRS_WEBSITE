import datetime

from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from .. import db, bcrypt
from ..models import User, Car, City, CarCompany, CarModels, CarCategories, Temporary, Rented
from ..main.forms import LoginForm, UpdateAccountForm, ResetPasswordForm, RequestResetForm, ChangePassword, SearchForm
from ..utils import send_reset_email
main = Blueprint('main', __name__)


@main.context_processor
def base():
    form = SearchForm()
    return dict(form=form)


@main.route("/")
@main.route("/home")
def home():

    """Method for displaying the home page of the website to any type of user. It detects the user by his role
    and redirects to user according to his requirements.
    -----------------------------
    Returns: The home page according to the requirements of the user"""

    page = request.args.get('page', 1, type=int)
    if current_user.is_authenticated:
        if current_user.is_admin:
            return render_template('home.html')
        dates = Temporary.query.filter_by(user_id=current_user.id).first()
        if dates:
            if dates.rent_from < datetime.datetime.today():
                flash("Please Enter the dates again!", "info")
                return redirect(url_for('users.taking_dates'))
        else:
            return redirect(url_for('users.taking_dates'))
        rented_cars = Rented.query.with_entities(Rented.carID).filter(dates.rent_from <= Rented.rented_till) \
            .filter(dates.rent_till >= Rented.rented_from).filter(Rented.final_status == "true").all()
        lst = []
        for i in rented_cars:
            lst += i
        cars = Car.query.filter_by(city_id=current_user.city_id).filter(Car.id.notin_(lst)) \
            .filter_by(status="true").paginate(page=page, per_page=2)
        if cars:
            return render_template('home.html', cars=cars, dates=dates)
        else:
            flash("There are no cars available in your city in the asked time!", "info")
            return render_template('layout.html')
    else:
        cars = Car.query.paginate(page=page, per_page=2)
        return render_template('home.html', cars=cars)


@main.route("/about")
def about():
    """Method for displaying the about page of the app which is the same for all the types of users
    -----------------------------
    Returns: The about page of the website"""
    return render_template('about.html', title='About')


@main.route("/login", methods=['GET', 'POST'])
def login():

    """Method for logging in to the website for all types of users. If the request method is get, a form is called and
    the user needs to enter his credentials and upon the validation of the form, he is logged in to his account.
    -----------------------------
    Returns: The success message and redirects to home if proper credentials else displays a warning message"""

    form = LoginForm()
    user = User.query.filter_by(email=form.email.data).first()
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    if request.method == "POST":
        if form.validate_on_submit():
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                if user.is_admin:
                    login_user(user, remember=form.remember.data)
                    next_page = request.args.get('next')
                    flash('Welcome Admin!', 'success')
                    return redirect(next_page) if next_page else redirect(url_for('main.home'))
                else:
                    login_user(user, remember=form.remember.data)
                    next_page = request.args.get('next')
                    flash('You are logged in!', 'success')
                    return redirect(next_page) if next_page else redirect(url_for('users.taking_dates'))
            else:
                flash('Please check your Credentials!', 'danger')
    return render_template('login.html', form=form)


@main.route("/logout")
def logout():
    """Method for logging out from the app for all the users
    -----------------------------
    Returns: Redirects to the home page of an unauthenticated user"""
    logout_user()
    return redirect(url_for('main.home'))


@main.route("/account", methods=['GET', 'POST'])
@login_required
def account():

    """Method for displaying current account details and updating them as well for all the users. If the request method
    is get, a form is called to display all the current details and that form is editable and upon the validation of
    that form, the details of users are updated in the User model
    ---------------------------
    Returns: Success flash message if the account is updated"""

    cities = City.query.all()
    current_city = City.query.filter_by(id=current_user.city_id).first()
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.name = form.name.data
        current_user.city_id = form.city_id.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('main.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.name.data = current_user.name
    return render_template('update_account.html', title='Account', form=form, cities=cities,
                           current_city=current_city)


@main.route("/reset_password", methods=['GET', 'POST'])
def reset_request():

    """Method for applying for the reset password request. If the request method is get, a form is passed and upon the
    validation of that form, the reset link is sent to the registered email id.
    -----------------------------
    Returns: The success and message and redirects to the home page"""

    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if request.method == "POST":
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.mail.data).first()
            send_reset_email(user)
            flash('An email has been sent with instructions to reset password!', 'info')
            return redirect(url_for('main.login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@main.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):

    """Method for resetting the password for all the users. If the request method is get, a form is called which takes
    the password from the user as an input and upon the validation of the form, the changes are made in the database.
    -----------------------------
    Returns: The success message and redirects to log in page"""

    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if not user:
        flash('That is an invalid or expired token!', 'warning')
        return redirect(url_for('main.reset_request'))
    form = ResetPasswordForm()
    if request.method == "POST":
        if form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user.password = hashed_password
            db.session.commit()
            flash(f'Your password has been updated successfully!', 'success')
            return redirect(url_for('main.login'))
    return render_template('reset_token.html', title='Reset Password', form=form)


@main.route("/change_password", methods=['GET', 'POST'])
@login_required
def change_password():
    """Method to change password for all the users. If the request method is post, a form is called where the user needs
    to enter the current password and upon the validation of the form the changes are made in the Users model
    -------------------------------
    Returns: Success message and redirects to the home page"""
    form = ChangePassword()
    if form.validate_on_submit():
        if bcrypt.check_password_hash(current_user.password, form.form_password.data):
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            current_user.password = hashed_password
            db.session.commit()
            flash("Your password is updated successfully!", "success")
            return redirect(url_for('main.home'))
        else:
            flash("Please enter correct password for your account!", 'danger')
    return render_template('change_password.html', title='Change Password', form=form)


@main.route('/search', methods=['POST'])
@login_required
def search():

    """Method for searching the cars according to the word entered by the user.
    -----------------------------
    Returns: The list of the cars which are matching with the word entered by the user"""

    page = request.args.get('page', 1, type=int)
    form = SearchForm()
    cars = Car.query.paginate(page=page, per_page=2)
    dates = Temporary.query.filter_by(user_id=current_user.id).first()
    rented_cars = Rented.query.with_entities(Rented.carID).filter(dates.rent_from <= Rented.rented_till) \
        .filter(dates.rent_till >= Rented.rented_from).filter(Rented.final_status == "true").all()
    lst = []
    for i in rented_cars:
        lst += i
    if form.validate_on_submit():
        searched_cars = form.searched.data
        record = CarCompany.query.filter(CarCompany.company_name.ilike('%' + searched_cars + '%')).first()
        if record:
            cars = Car.query.filter_by(company_id=record.id).filter_by(city_id=current_user.city_id).\
                filter(Car.id.notin_(lst)).filter_by(status="true").paginate(page=page, per_page=2)
        record = CarCategories.query.filter(CarCategories.category.ilike('%' + searched_cars + '%')).first()
        if record:
            cars = Car.query.filter_by(category_id=record.id).filter_by(city_id=current_user.city_id)\
                .filter(Car.id.notin_(lst)).filter_by(status="true").paginate(page=page, per_page=2)
        record = CarModels.query.filter(CarModels.model_name.ilike('%' + searched_cars + '%')).first()
        if record:
            cars = Car.query.filter_by(model_id=record.id).filter_by(city_id=current_user.city_id)\
                .filter(Car.id.notin_(lst)).filter_by(status="true").paginate(page=page, per_page=2)
        record = City.query.filter(City.city.ilike('%' + searched_cars + '%')).first()
        if record:
            cars = Car.query.filter_by(city_id=record.id).filter_by(city_id=current_user.city_id)\
                .filter(Car.id.notin_(lst)).filter_by(status="true").paginate(page=page, per_page=2)
        return render_template('home.html', cars=cars, dates=dates)
    return render_template('home.html', cars=cars, dates=dates)
