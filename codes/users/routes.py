from flask import render_template, url_for, flash, redirect, Blueprint, request
from flask_login import current_user, login_required
from .. import db, bcrypt
from ..decorators import user_required, admin_role_required
from ..models import User, City, UserVerification, Rented, Temporary, Car
from ..users.forms import RegistrationForm, ApprovalForm, TakingDates
from ..utils import save_picture
from ..main.forms import SearchForm
import datetime
import stripe
import os


users = Blueprint('users', __name__)
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")


@users.context_processor
def base():
    form = SearchForm()
    return dict(form=form)


@users.route("/register", methods=['GET', 'POST'])
def register():

    """Method to register to the website by an unauthenticated user. If the request method is get, a form is passed for
    the user to enter his details and upon the successful validation of that form, the details of that user are added
    to the database so that he can log in to the website.
    -----------------------------
    Returns: The success flash message and redirects to log in page"""

    cities = City.query.all()
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if request.method == "POST":
        if form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user = User(username=form.username.data, email=form.email.data, password=hashed_password, name=form.name.data,
                        city_id=form.city_id.data)
            db.session.add(user)
            db.session.commit()
            flash(f'Your account has been created successfully!', 'success')
            return redirect(url_for('main.login'))
    return render_template('register.html', form=form, cities=cities)


@users.route("/verify_account", methods=['GET', 'POST'])
@login_required
@user_required
def apply_for_verification():

    """Method to apply for verification by a user so that he can get verified in order to book cars. If the request
    method is get, a form is called where he needs to submit his id proof.
    -----------------------------
    Returns: The success flash message and redirects to the home page"""

    records = UserVerification.query.filter_by(user_id=current_user.id).all()
    form = ApprovalForm()
    if request.method == "POST":
        if form.validate_on_submit():
            if form.id_proof.data:
                picture_file = save_picture(form.id_proof.data)
                current_user.image_file = picture_file
                row = UserVerification(user_id=current_user.id, id_proof=picture_file, approval="",
                                   date=datetime.date.today())
                db.session.add(row)
                db.session.commit()
            flash(f'Your documents are submitted successfully! Please wait for the approval.', 'info')
            return redirect(url_for('main.home'))
    return render_template('apply_for_verification.html', title='Apply for Verification', form=form,
                           records=records)


@users.route("/display_users_list")
@login_required
@admin_role_required
def display_users_list():

    """Method to display the list of all the users which have currently applied for the user verification which can only
    be accessed by an admin.
    -----------------------------
    Returns: The users list if users are there for verification else return an info flash message
    and redirects to home"""

    users_list = db.session.query(UserVerification, User).filter(UserVerification.user_id == User.id)\
        .filter(UserVerification.approval == "").all()
    if users_list:
        return render_template('verify_users_list.html', users_list=users_list)
    else:
        flash("There are no users to verify!", "info")
        return redirect(url_for('main.home'))


@users.route("/taking_dates", methods=['GET', 'POST'])
@login_required
@user_required
def taking_dates():

    """Method for taking the dates from the user when he has to book the car in order to display the cars accordingly.
    If the request method is get, a form is called for the user to enter both the dates and upon the validation of form
    is he is redirected to the home page where he is shown the available cars according to his requirements.
    -----------------------------
    Returns: Redirects to home page where all the available cars are shown to the user"""

    form = TakingDates()
    if request.method == "POST":
        if form.validate_on_submit():
            rent_from_date = form.rent_from.data
            rent_till_date = form.rent_till.data
            city_delivery = form.city_id.data
            record = Temporary.query.filter_by(user_id=current_user.id).first()
            if record:
                record.rent_from = rent_from_date
                record.rent_till = rent_till_date
                record.city_id = city_delivery
                db.session.commit()
            else:
                new = Temporary(user_id=current_user.id, rent_from=rent_from_date, rent_till=rent_till_date,
                                city_id=city_delivery)
                db.session.add(new)
                db.session.commit()
            return redirect(url_for('main.home'))
    cities = City.query.all()
    return render_template('taking_dates.html', form=form, cities=cities)


@users.route("/bookings")
@login_required
@user_required
def bookings():

    """Method to display all the booking he has done through his website with all the status which can only be accessed
    by an authenticated user.
    -----------------------------
    Returns: The bookings list if the user has bookings else returns info flash message and redirects to home page"""

    page = request.args.get('page', 1, type=int)
    orders = Rented.query.filter_by(user_id=current_user.id).order_by(Rented.booking_time.desc())\
        .paginate(page=page, per_page=5)
    current_date = datetime.datetime.today()
    if orders.items:
        return render_template('orders.html', orders=orders, current_date=current_date)
    else:
        flash("You dont have any bookings!", "info")
        return redirect(url_for('main.home'))


@users.route('/cancel_booking/<string:ids>')
@login_required
@user_required
def cancel_booking(ids):

    """Method to cancel the booking for a user. This method is called when the user clicks the cancel button which is
    clicked by the user.
    -----------------------------
    Returns: The success flash message and redirects again to the bookings page"""

    record = Rented.query.filter_by(booking_id=ids).first()
    if record.rented_from > datetime.datetime.today():
        record.final_status = "false"
        db.session.commit()
        flash("Your booking has been cancelled!", "warning")
        return redirect(url_for('users.bookings'))
    else:
        flash("You cannot cancel this booking now!", "danger")
        return redirect(url_for('main.home'))


@users.route('/pay_fine/<string:ids>')
@login_required
@user_required
def pay_fine(ids):

    """Method to pay fine for all the user. It updates all the details in the database when the fine
    is paid by the user.
    -----------------------------
    Returns: The success flash message and redirects to home page"""

    record = Rented.query.filter_by(booking_id=ids).first()
    user = User.query.filter_by(id=record.user_id).first()
    record.fine_paid = True
    user.fine_pending = False
    db.session.commit()
    flash('You have successfully paid the fine amount!', "success")
    return redirect(url_for('main.home'))


@users.route('/index/<string:ids>/<int:days>')
def index(ids, days):

    """Method to call the payment page for paying the Rent of the car by clicked on the book car button.
    -----------------------------
    Returns: The payment page with a button to pay the required amount of money"""

    car = Car.query.filter_by(id=ids).first()
    total_amount = (days*car.ppd) + car.deposit

    return render_template('index.html', total_amount=total_amount,
                           key=os.environ.get("STRIPE_PUBLISHABLE_KEY"), ids=car.id)


@users.route('/fine_index/<string:ids>/<int:total_amount>')
def fine_index(ids, total_amount):

    """Method to call the payment page for paying the fine of the car by clicked on the pay fine button.
    -----------------------------
    Returns: The payment page with a button to pay the required amount of money"""

    return render_template('fine_index.html', total_amount=total_amount,
                           key=os.environ.get("STRIPE_PUBLISHABLE_KEY"), ids=ids)


@users.route('/charge/<int:total_amount>/<int:ids>')
def charge(total_amount, ids):

    """Method for paying the amount of money, a user need to pay for booking a car.
    -----------------------------
    Returns: The payment page entering all the details to pay the amount required"""

    amount = total_amount*100

    card_obj = stripe.PaymentMethod.create(
        type="card",
        card={
            "number": "4242424242424242",
            "exp_month": 7,
            "exp_year": 2023,
            "cvc": 980
        },
    )

    customer = stripe.Customer.create(
        email=current_user.email,
        source=request.form['stripeToken']
    )

    charge = stripe.PaymentIntent.create(
        customer=customer.id,
        amount=amount,
        payment_method=card_obj.id,
        currency='inr',
        description='Rent Car'
    )

    return redirect(url_for('cars.confirm_car', ids=ids))


@users.route('/fine_charge/<int:total_amount>/<int:ids>')
def fine_charge(total_amount, ids):

    """Method for paying the amount of money, a user need to pay for paying the fine.
    -----------------------------
    Returns: The payment page entering all the details to pay the amount required"""

    amount = total_amount*100

    customer = stripe.Customer.create(
        email=current_user.email,
        source=request.form['stripeToken']
    )

    charge = stripe.PaymentIntent.create(
        customer=customer.id,
        amount=amount,
        currency='INR',
        description='Rent Car'
    )

    return redirect(url_for('users.pay_fine', ids=ids))
