from flask import render_template, Blueprint, flash, redirect, url_for, request
from .. import db
from flask_login import current_user, login_required
from ..decorators import admin_role_required, user_required, user_verified
from ..models import Car, CarCategories, CarModels, CarCompany, City, Temporary, Rented, Maintenance, User
from .forms import CreateCars, GetCar, UpdateCar, ReturnCar, CarMaintenance
from ..main.forms import SearchForm
import datetime

cars = Blueprint('cars', __name__)


@cars.context_processor
def base():
    form = SearchForm()
    return dict(form=form)


@cars.route("/create_cars",  methods=['GET', 'POST'])
@login_required
@admin_role_required
def create_cars():

    """Method to add cars in to the Car model which can only be accessed by the admin. If the request method is get, a
    form is called for accepting the details of the car and upon the validation of the form, the car is entered in
    to the Car model.
    -----------------------------
    Returns: The success flash message and redirects to the home page"""

    form = CreateCars()
    categories = CarCategories.query.all()
    companies = CarCompany.query.all()
    models = CarModels.query.all()
    cities = City.query.all()
    if request.method == "POST":
        if form.validate_on_submit():
            car = Car(car_id=form.car_id.data.replace(" ", "").upper(), company_id=form.company_id.data,
                      category_id=form.category_id.data, model_id=form.model_id.data,
                      color=form.color.data.replace(" ", "").upper(),
                      mileage=form.mileage.data, ppd=form.ppd.data, min_rent=form.min_rent.data,
                      city_id=form.city_id.data, deposit=form.deposit.data)
            db.session.add(car)
            db.session.commit()
            flash(f'Car has been added successfully!', 'success')
            return redirect(url_for('main.home'))
    return render_template('create_cars.html', form=form, categories=categories, models=models, companies=companies,
                           cities=cities)


@cars.route("/get_car",  methods=['GET', 'POST'])
@login_required
@admin_role_required
def get_car():

    """Method to get a car by its car id for various purposes which can only be accessed by the admin. If the request
     method is get, a form is called to accept the car id and upon the validation of the form, the car is
     displayed to the admin.
    -----------------------------
    Returns: The car details method to update the car of that car id."""

    form = GetCar()
    if request.method == "POST":
        if form.validate_on_submit():
            car = Car.query.filter_by(car_id=form.car.data.replace(" ", "").upper()).first()
            return redirect(url_for('cars.update_car', car_id=car.car_id))
    return render_template('get_car.html', form=form)


@cars.route("/update_car",  methods=['GET', 'POST'])
@login_required
@admin_role_required
def update_car():

    """Method to update a car which can only be accessed by the admin. If the request method is get, a form is called
    which already has the current details of that car and the user can update that details and upon the validation of
    the form, the car is updated.
    -----------------------------
    Returns: The success flash message and redirects to the home page"""

    car_id = request.args.get('car_id')
    car = Car.query.filter_by(car_id=car_id).first()
    cities = City.query.all()
    current_city = City.query.filter_by(id=car.city_id).first()
    form = UpdateCar()
    if request.method == "POST":
        if form.validate_on_submit():
            car.color = form.color.data.replace(" ", "").upper()
            car.mileage = form.mileage.data
            car.ppd = form.ppd.data
            car.min_rent = form.min_rent.data
            car.deposit = form.deposit.data
            car.city_id = form.city_id.data
            car.status = form.status.data
            db.session.commit()
            flash(' Car has been updated successfully!', 'success')
            return redirect(url_for('main.home'))
    elif request.method == "GET":
        form.color.data = car.color
        form.mileage.data = car.mileage
        form.ppd.data = car.ppd
        form.min_rent.data = car.min_rent
        form.deposit.data = car.deposit
        form.city_id.data = car.city_id
    return render_template('update_car.html', title='Car', form=form, car=car, cities=cities,
                           current_city=current_city)


@cars.route('/view_car/<string:car_id>')
def view_car(car_id):

    """Method to view a car by clicking on the view car button which does not require to be an authenticated or an
    unauthenticated user.
    -----------------------------
    Returns: The car details which was viewed by the user"""

    car = Car.query.filter_by(car_id=car_id).first()
    return render_template('view_car.html', car=car)


@cars.route('/book_car/<int:car_id>')
@login_required
@user_required
@user_verified
def book_car(car_id):

    """Method to book a car for a verified user. The car is booked only if he does not have any other bookings during
    that time period and if he does not have any pending fine.
    -----------------------------
    Returns: The success flash message and redirects to the home page if no pending fine or bookings at that time else
    return a warning flash message"""

    if not current_user.fine_pending:
        user = Temporary.query.filter_by(user_id=current_user.id).first()
        rented_cars = Rented.query.filter(user.rent_from <= Rented.rented_till) \
            .filter(user.rent_till >= Rented.rented_from).filter_by(carID=car_id)\
            .filter(Rented.final_status == "true").all()
        record = Rented.query.filter(user.rent_from <= Rented.rented_till) \
            .filter(user.rent_till >= Rented.rented_from).filter_by(user_id=current_user.id) \
            .filter(Rented.final_status == "true").all()
        if rented_cars:
            flash("Sorry! This car is already booked!", "warning")
            return redirect(url_for('main.home'))
        elif record:
            flash("Sorry! You already have a booking for this time period and you can only book a single at a"
                  " given time!", "warning")
            return redirect(url_for('main.home'))
        else:
            car = Car.query.filter_by(id=car_id).first()
            dates = Temporary.query.filter_by(user_id=current_user.id).first()
            days = int(str(dates.rent_till - dates.rent_from).split(" ")[0])
            rent_from = str(dates.rent_from).split(" ")[0]
            rent_till = str(dates.rent_till).split(" ")[0]
            return render_template('payment.html', car=car, days=days, rent_from=rent_from, rent_till=rent_till,
                                   dates=dates)
    else:
        flash("You first need the to pay your previous fine to book a car!", "warning")
        return redirect(url_for('users.bookings'))


@cars.route('/confirm_car')
@login_required
@user_required
def confirm_car():

    """Method to confirm the booking of the user in the database only after he has completed his payment.
    -----------------------------
    Returns: The success flash message and redirects to the home page"""

    ids = request.args.get('ids')
    dates = Temporary.query.filter_by(user_id=current_user.id).first()
    rent = Rented(carID=ids, user_id=current_user.id, booking_time=datetime.datetime.now(),
                  rented_from=dates.rent_from, rented_till=dates.rent_till,
                  city_taken_id=current_user.city_id, city_delivery_id=dates.city_id)

    db.session.add(rent)
    db.session.commit()
    flash("The car has been booked successfully!", "success")
    return redirect(url_for('main.home'))


@cars.route("/get_delete_car",  methods=['GET', 'POST'])
@login_required
@admin_role_required
def get_delete_car():

    """Method to get the car by the admin in order to delete that car. If the request method is get, a form is called
    to take car id and upon the validation of the form, it returns that car.
    -----------------------------
    Returns: The car details with a delete button."""

    form = GetCar()
    if form.validate_on_submit():
        car = Car.query.filter_by(car_id=form.car.data.replace(" ", "").upper()).first()
        return render_template('delete_car.html', car=car)
    return render_template('get_car.html', form=form)


@cars.route("/delete_car/<string:car_id>")
@login_required
@admin_role_required
def delete_car(car_id):

    """Method to delete a car which can only be accessed by the admin. The car will be deleted from the database if no
    further booking of that car are there in the database else it will not be deleted.
    -----------------------------
    Returns: The success flash message and redirects to the home page"""

    record = Rented.query.filter_by(carID=car_id).filter(Rented.final_status == "true").first()
    if record:
        if record.rented_from > datetime.datetime.today():
            flash("This car cannot be deleted as it is booked by a someone!", "info")
        else:
            Car.query.filter_by(id=car_id).delete()
            db.session.commit()
            flash("Car deleted successfully!", "success")
    else:
        Car.query.filter_by(id=car_id).delete()
        db.session.commit()
        flash("Car deleted successfully!", "success")
    return redirect(url_for('main.home'))


@cars.route("/cars_taking_list")
@login_required
@admin_role_required
def cars_taking_list():

    """Method which can only be accessed by the admin for displaying all the cars which are to be taken by the users
    on that day from the admin city.
    -----------------------------
    Returns: The cars list if there are bookings for that day else returns an info message and redirects to the home
    page"""

    page = request.args.get('page', 1, type=int)
    orders = Rented.query.filter_by(city_taken_id=current_user.city_id).filter_by(final_status="true")\
        .filter_by(rented_from=datetime.date.today()).filter_by(car_taken=False)\
        .paginate(page=page, per_page=5)
    if orders.items:
        return render_template('cars_taking.html', orders=orders)
    else:
        flash('There are no booking for today!', 'info')
    return redirect(url_for('main.home'))


@cars.route("/car_taken/<string:ids>")
@login_required
@admin_role_required
def car_taken(ids):

    """Method which can only be accessed by the admin for entering that the car is taken by the user in the admin.
    -----------------------------
    Returns: Enter the data that the car is taken by the user and redirects to the home page"""

    record = Rented.query.filter_by(booking_id=ids).first()
    record.car_taken = True
    db.session.commit()
    return redirect(url_for('main.home'))


@cars.route("/cars_delivery_list")
@login_required
@admin_role_required
def cars_delivery_list():

    """Method which can only be accessed by the admin for displaying all the cars which are to be delivered back by the
    users on that day to the admin city.
    -----------------------------
    Returns: The cars list if there are returns for that day else returns an info message and redirects to the home
    page"""

    page = request.args.get('page', 1, type=int)
    orders = Rented.query.filter_by(city_delivery_id=current_user.city_id).filter_by(final_status="true")\
        .filter_by(rented_till=datetime.date.today()).filter_by(car_taken=True)\
        .filter_by(car_delivery=False).paginate(page=page, per_page=5)
    if orders.items:
        return render_template('cars_delivery.html', orders=orders)
    else:
        flash('There are no car returns for today!', 'info')
    return redirect(url_for('main.home'))


@cars.route("/car_return_review/<string:ids>", methods=['GET', 'POST'])
@login_required
@admin_role_required
def car_return_review(ids):

    """Method which can only be accessed by the admin for entering the details of the car when the car is returned.
    If the request method is get, a form is called which takes all the data from the admin and upon the validation of
    that form, the data is entered in the database and user is charged fine if any.
    -----------------------------
    Returns: The success flash message and redirects to the home page"""

    form = ReturnCar()
    if request.method == "POST":
        if form.validate_on_submit():
            record = Rented.query.filter_by(booking_id=ids).first()
            record.said_date = bool(int(form.said_date.data))
            record.said_time = bool(int(form.said_time.data))
            record.proper_condition = bool(int(form.proper_condition.data))
            record.description = form.description.data
            record.fine = form.fine.data
            if form.fine.data > 0:
                user = User.query.filter_by(id=record.user_id).first()
                user.fine_pending = True
            record.car_delivery = True
            db.session.commit()
            flash('Car reviewed!', "success")
            return redirect(url_for('main.home'))
    return render_template('return_car_form.html', form=form)


@cars.route("/cars_taking_list_late")
@login_required
@admin_role_required
def cars_taking_list_late():

    """Method which can only be accessed by the admin for displaying all the cars which are to be not taken even
    after the booking date by the users on that day from the admin city.
    -----------------------------
    Returns: The cars list if there are bookings for that day else returns an info message and redirects to the home
    page"""

    page = request.args.get('page', 1, type=int)
    orders = Rented.query.filter_by(city_taken_id=current_user.city_id).filter_by(final_status="true")\
        .filter(Rented.rented_from < datetime.date.today()).filter(Rented.rented_till > datetime.date.today())\
        .filter_by(car_taken=False).paginate(page=page, per_page=5)
    if orders.items:
        return render_template('cars_taking.html', orders=orders)
    else:
        flash('There are no previous bookings which are pending!', 'info')
    return redirect(url_for('main.home'))


@cars.route("/cars_delivery_list_late")
@login_required
@admin_role_required
def cars_delivery_list_late():
    """Method which can only be accessed by the admin for displaying all the cars which are to be delivered back by the
    users on that day to the admin city but is not delivered on that day.
    -----------------------------
    Returns: The cars list if there are returns for that day else returns an info message and redirects to the home
    page"""

    page = request.args.get('page', 1, type=int)
    orders = Rented.query.filter_by(city_delivery_id=current_user.city_id).filter_by(final_status="true")\
        .filter(Rented.rented_till < datetime.date.today()).filter_by(car_taken=True)\
        .filter_by(car_delivery=False).paginate(page=page, per_page=5)
    if orders.items:
        return render_template('cars_delivery.html', orders=orders)
    else:
        flash('There are no car returns for previous days!', 'info')
    return redirect(url_for('main.home'))


@cars.route("/get_maintenance_car",  methods=['GET', 'POST'])
@login_required
@admin_role_required
def get_maintenance_car():

    """Method to get a car by its car id for various purposes which can only be accessed by the admin. If the request
    method is get, a form is called to accept the car id and upon the validation of the form, the car is displayed
    to the admin.
    -----------------------------
    Returns: The car details method to maintain the car of that car id"""

    form = GetCar()
    if request.method == "POST":
        if form.validate_on_submit():
            car = Car.query.filter_by(car_id=form.car.data.replace(" ", "").upper()).first()
            car_id = car.id
            return redirect(url_for('cars.car_maintenance', car_id=car_id))
    return render_template('get_car.html', form=form)


@cars.route("/car_maintenance", methods=['GET', 'POST'])
@login_required
@admin_role_required
def car_maintenance():

    """Method to enter the car maintenance for a car if required which can only be accessed by an admin.
    If the request method is get, a form is called to enter the car details and upon the validation of that form, the details are added to the
    database and also the car is made unavailable for booking.
    -----------------------------
    Returns: The success flash message and redirects to the home page"""

    form = CarMaintenance()
    car_id = request.args.get('car_id')
    car = Car.query.filter_by(id=car_id).first()
    if request.method == "POST":
        if form.validate_on_submit():
            record = Maintenance(carID=car_id, date=datetime.datetime.utcnow(), description=form.description.data,
                                 user_id=current_user.id)
            db.session.add(record)
            car.status = False
            db.session.commit()
            flash('Car successfully added to maintenance!', 'success')
            return redirect(url_for('main.home'))
    return render_template('car_maintenance.html', form=form)
