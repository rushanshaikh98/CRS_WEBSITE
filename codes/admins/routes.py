from flask import render_template, url_for, flash, redirect, Blueprint, request
from .. import db, bcrypt
from ..decorators import super_admin_role_required, admin_role_required
from ..models import User, CarCompany, CarModels, CarCategories, City, UserVerification, Car
from ..admins.forms import CreateAdmins, AddCity, AddCompany, AddModel, AddCategory, DeleteCity, DeleteModel, \
    DeleteCompany, DeleteCategory, UpdateCity, UpdateCompany, UpdateCategory, UpdateModel
from flask_login import login_required

admins = Blueprint('admins', __name__)


@admins.route("/create_admins",  methods=['GET', 'POST'])
@login_required
@super_admin_role_required
def create_admins():

    """Method to create admins which can only be done by the super admin! If the request method is get it will return
    a form and if request method is post, upon the validation of that form, the values are passed to this function
    and added to the User model as an admin.
    -----------------------------
    Returns: The success flash message and redirects to the home page"""

    cities = City.query.all()
    form = CreateAdmins()
    if request.method == 'POST':
        if form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user = User(username=form.username.data, email=form.email.data, password=hashed_password,
                        name=form.name.data, city_id=form.city_id.data, is_admin=True)
            db.session.add(user)
            db.session.commit()
            flash(f'Admin has been created successfully!', 'success')
            return redirect(url_for('main.home'))
    return render_template('create_admins.html', form=form, cities=cities)


@admins.route("/add_company", methods=['GET', 'POST'])
@login_required
@super_admin_role_required
def add_company():

    """Method to add a company into the CarCompany model which is only accessible by the super admin! If the request method is
    post, a form is called to take the input values from the super admin and if request method is post, upon the
    validation of that form, the values are passed to this function and added to the CarCompany model.
    -----------------------------
    Returns: The success flash message and redirects to the home page"""

    form = AddCompany()
    if request.method == 'POST':
        if form.validate_on_submit():
            company = CarCompany(company_name=form.company_name.data.replace(" ", "").upper())
            db.session.add(company)
            db.session.commit()
            flash(f'Company has been added successfully!', 'success')
            return redirect(url_for('main.home'))
    return render_template('add_company.html', form=form)


@admins.route("/add_city", methods=['GET', 'POST'])
@login_required
@super_admin_role_required
def add_city():

    """Method to add a company into the City model which is only accessible by the super admin! If the request method is
    get, a form is called to take the input values from the super admin and if the request method is post, upon the
    validation of that form, the values are passed to this function and added to the City model.
    -----------------------------
    Returns: The success flash message and redirects to the home page"""

    form = AddCity()
    if request.method == 'POST':
        if form.validate_on_submit():
            city = City(city=form.city.data.replace(" ", "").upper())
            db.session.add(city)
            db.session.commit()
            flash(f'City has been added successfully!', 'success')
            return redirect(url_for('main.home'))
    return render_template('add_city.html', form=form)


@admins.route("/add_category", methods=['GET', 'POST'])
@login_required
@super_admin_role_required
def add_category():

    """Method to add a category into the CarCategories model which is only accessible by the super admin! If the request method is
     get, a form is called to take the input values from the super admin and if the request method is post, upon the
     validation of that form, the values are passed to this function and added to the CarCategories model.
    -----------------------------
    Returns: The success flash message and redirects to the home page"""

    form = AddCategory()
    if request.method == 'POST':
        if form.validate_on_submit():
            category = CarCategories(category=form.category.data.replace(" ", "").upper())
            db.session.add(category)
            db.session.commit()
            flash(f'Category has been added successfully!', 'success')
            return redirect(url_for('main.home'))
    return render_template('add_category.html', form=form)


@admins.route("/add_model", methods=['GET', 'POST'])
@login_required
@super_admin_role_required
def add_model():

    """Method to add a car model into the CarModels model which is only accessible by the super admin! If the request method is
    get, a form is called to take the input values from the super admin and if the request method is post, upon the
    validation of that form, the values are passed to this function and added to the CarModels model.
    -----------------------------
    Returns: The success flash message and redirects to the home page"""

    form = AddModel()
    if request.method == 'POST':
        if form.validate_on_submit():
            model = CarModels(model_name=form.model_name.data.replace(" ", "").upper())
            db.session.add(model)
            db.session.commit()
            flash(f'Model has been added successfully!', 'success')
            return redirect(url_for('main.home'))
    return render_template('add_model.html', form=form)


@admins.route("/verify_user/<string:user_id>")
@login_required
@admin_role_required
def verify_user(user_id):

    """Method to display the details and image uploaded by a user for the verification by selecting a specific users
    from many users which can only be accessed by the admin.
    -----------------------------
    Returns: Details of the user and the id proof image he has submitted with buttons to review the request"""

    user_ver = UserVerification.query.filter_by(user_id=user_id).filter(UserVerification.approval == "").first()
    user = User.query.filter_by(id=user_id).first()
    image_file = url_for('static', filename='id_proofs/' + user_ver.id_proof)
    return render_template('verify_user.html', user_ver=user_ver, user=user, image_file=image_file)


@admins.route("/accept_user/<string:user_id>")
@login_required
@admin_role_required
def accept_user(user_id):

    """Method to approve the verification request by the user which can only be accessed by the admin. It is called
    when the accept button in verify user method is clicked. It also enters the user as verified in the database.
    -----------------------------
    Returns: The success flash message and redirects again to requests list"""

    user_ver = UserVerification.query.filter_by(user_id=user_id).filter(UserVerification.approval == "").first()
    user = User.query.filter_by(id=user_id).first()
    user.is_verified = True
    user_ver.approval = "true"
    db.session.commit()
    flash('User successfully verified!', 'success')
    return redirect(url_for('users.display_users_list'))


@admins.route("/reject_user/<string:user_id>")
@login_required
@admin_role_required
def reject_user(user_id):

    """Method to reject the verification request by the user which can only be accessed by the admin. It is called
    when the reject button in verify user method is clicked. It also enters the user as rejected in the database.
    -----------------------------
    Returns: The danger flash message and redirects again to requests list"""

    user_ver = UserVerification.query.filter_by(user_id=user_id).filter(UserVerification.approval == "").first()
    user_ver.approval = "false"
    db.session.commit()
    flash('User successfully rejected!', 'danger')
    return redirect(url_for('users.display_users_list'))


@admins.route("/admins_list")
@login_required
@super_admin_role_required
def admin_list():

    """Method to display the admins list for the deletion purpose which can only be accessed by a super admin.
    ------------------------------
    Returns: A list of admins with a button with each admin if any admins else redirects to home with a flash message"""

    admins_list = User.query.filter_by(is_admin=True).filter_by(is_super_admin=False).all()
    if admins_list:
        return render_template('admin_list.html', admins_list=admins_list)
    else:
        flash("There are no admins!", "info")
        return redirect(url_for('main.home'))


@admins.route("/delete_admin/<string:user_id>")
@login_required
@super_admin_role_required
def delete_admin(user_id):

    """Method to delete an admin which can only be accessed by the super admin. It is called when the delete button in
    admin list is hit. It deletes an admin from the database.
    -----------------------------
    Returns: The success flash message and redirects again to admins list"""

    User.query.filter_by(id=user_id).delete()
    db.session.commit()
    flash('Admin successfully deleted!', 'danger')
    return redirect(url_for('admins.admin_list'))


@admins.route("/delete_city", methods=['GET', 'POST'])
@login_required
@super_admin_role_required
def delete_city():

    """Method to delete a city from the City model which can only be accessed by the super admin. If the request method
    is get, a form is called to select a city from the existing cities in the database and if that city does not have
    any users, it is deleted else it is not deleted.
    -----------------------------
    Returns: The success flash message and redirects to the home page if the city does not have any users else
    warning flash message is returned"""

    form = DeleteCity()
    cities = City.query.all()
    if cities:
        if request.method == "POST":
            if form.validate_on_submit():
                users = User.query.filter_by(city_id=form.city_id.data).first()
                if users:
                    flash("City cannot be deleted as it has users!", "warning")
                else:
                    City.query.filter_by(id=form.city_id.data).delete()
                    db.session.commit()
                    flash('City has been deleted successfully!', 'success')
                return redirect(url_for('main.home'))
        return render_template('delete_city.html', form=form, cities=cities)
    else:
        flash('There are no cities!', 'warning')


@admins.route("/delete_company", methods=['GET', 'POST'])
@login_required
@super_admin_role_required
def delete_company():

    """Method to delete a company from the CarCompany model which can only be accessed by the super admin. If the request
    method is get, a form is called to select a company from the existing companies in the database and if that company
    does not have any cars in the database, it is deleted else it is not deleted.
    -----------------------------
    Returns: The success flash message and redirects to the home page if the company does not have cars else
    warning flash message is returned"""

    form = DeleteCompany()
    companies = CarCompany.query.all()
    if companies:
        if request.method == "POST":
            if form.validate_on_submit():
                cars = Car.query.filter_by(company_id=form.company_id.data).first()
                if cars:
                    flash('Company cannot be deleted as our company owns some cars of this company!', "warning")
                else:
                    CarCompany.query.filter_by(id=form.company_id.data).delete()
                    db.session.commit()
                    flash('Company has been deleted successfully!', 'success')
                return redirect(url_for('main.home'))
        return render_template('delete_company.html', form=form, companies=companies)
    else:
        flash('There are no companies!', 'warning')


@admins.route("/delete_category", methods=['GET', 'POST'])
@login_required
@super_admin_role_required
def delete_category():

    """Method to delete a category from the CarCategories model which can only be accessed by the super admin. If the request
    method is get, a form is called to select a category from the existing categories in the database and if that
    category does not have any cars in the database, it is deleted else it is not deleted.
    -----------------------------
    Returns: The success flash message and redirects to the home page if the category does not have cars else
    warning flash message is returned"""

    form = DeleteCategory()
    categories = CarCategories.query.all()
    if categories:
        if request.method == "POST":
            if form.validate_on_submit():
                cars = Car.query.filter_by(category_id=form.category_id.data).first()
                if cars:
                    flash('Category cannot be deleted as our company owns some cars of this category!', "warning")
                else:
                    CarCategories.query.filter_by(id=form.category_id.data).delete()
                    db.session.commit()
                    flash('Category has been deleted successfully!', 'success')
                return redirect(url_for('main.home'))
        return render_template('delete_category.html', form=form, categories=categories)
    else:
        flash('There are no more categories!', 'warning')


@admins.route("/delete_model", methods=['GET', 'POST'])
@login_required
@super_admin_role_required
def delete_model():

    """Method to delete a model from the CarModels model which can only be accessed by the super admin. If the request is get,
    a form is called to select a model from the existing models in the database and if that model does not have any
    cars in the database, it is deleted else it is not deleted.
    -----------------------------
    Returns: The success flash message and redirects to the home page if the model does not have cars users else
    warning flash message is returned"""

    form = DeleteModel()
    models = CarModels.query.all()
    if models:
        if request.method == "POST":
            if form.validate_on_submit():
                cars = Car.query.filter_by(model_id=form.model_id.data).first()
                if cars:
                    flash('Model cannot be deleted as our company owns this model!', "warning")
                else:
                    CarModels.query.filter_by(id=form.model_id.data).delete()
                    db.session.commit()
                    flash('Car Model has been deleted successfully!', 'success')
                return redirect(url_for('main.home'))
        return render_template('delete_model.html', form=form, models=models)
    else:
        flash('There are no more models!', 'warning')


@admins.route("/update_city", methods=['GET', 'POST'])
@login_required
@super_admin_role_required
def update_city():

    """Method to update a city name which can be accessed by the super admin. If the request method is get, a form is
    called to select a city from the existing cities and a new city name is entered and validation of the form,it
    updates the city name in the City model.
    -----------------------------
    Returns: The success flash message and redirects to the home page"""

    form = UpdateCity()
    cities = City.query.all()
    if cities:
        if request.method == "POST":
            if form.validate_on_submit():
                city = City.query.filter_by(id=form.city_id.data).first()
                city.city = form.city.data.replace(" ", "").upper()
                db.session.commit()
                flash(f'City has been updated successfully!', 'success')
                return redirect(url_for('main.home'))
        return render_template('update_city.html', form=form, cities=cities)
    else:
        flash(f'There are no cities in the database!', 'info')
        return redirect(url_for('main.home'))


@admins.route("/update_company", methods=['GET', 'POST'])
@login_required
@super_admin_role_required
def update_company():

    """Method to update a company name which can be accessed by the super admin. If the request method is get, a form
    is called to select a company from the existing companies and a new company name is entered and upon the validation
    of the form, it updates the company name in the CarCompany model.
    -----------------------------
    Returns: The success flash message and redirects to the home page"""

    form = UpdateCompany()
    companies = CarCompany.query.all()
    if companies:
        if request.method == "POST":
            if form.validate_on_submit():
                company = CarCompany.query.filter_by(id=form.company_id.data).first()
                company.company_name = form.company_name.data.replace(" ", "").upper()
                db.session.commit()
                flash(f'Company has been updated successfully!', 'success')
                return redirect(url_for('main.home'))
        return render_template('update_company.html', form=form, companies=companies)
    else:
        flash(f'There are no companies in the database!', 'info')
        return redirect(url_for('main.home'))


@admins.route("/update_category", methods=['GET', 'POST'])
@login_required
@super_admin_role_required
def update_category():

    """Method to update a category name which can be accessed by the super admin. If the request method is get, a form
    is called to select a category from the existing categories and a new category name is entered and upon the
    validation of the form, it updates the category name in the CarCategories model.
    -----------------------------
    Returns: The success flash message and redirects to the home page"""

    form = UpdateCategory()
    categories = CarCategories.query.all()
    if categories:
        if request.method == "POST":
            if form.validate_on_submit():
                category = CarCategories.query.filter_by(id=form.category_id.data).first()
                category.category = form.category.data.replace(" ", "").upper()
                db.session.commit()
                flash(f'Category has been updated successfully!', 'success')
                return redirect(url_for('main.home'))
        return render_template('update_category.html', form=form, categories=categories)
    else:
        flash(f'There are no categories in the database!', 'info')
        return redirect(url_for('main.home'))


@admins.route("/update_model", methods=['GET', 'POST'])
@login_required
@super_admin_role_required
def update_model():

    """Method to update a model name which can be accessed by the super admin. If the request method is get, a form is
    called to select a model from the existing models and a new company name is entered and upon the validation of the
    form, it updates the model name in the CarModels model.
    -----------------------------
    Returns: The success flash message and redirects to the home page"""

    form = UpdateModel()
    models = CarModels.query.all()
    if models:
        if request.method == "POST":
            if form.validate_on_submit():
                model = CarModels.query.filter_by(id=form.model_id.data).first()
                model.model_name = form.model_name.data.replace(" ", "").upper()
                db.session.commit()
                flash(f'Model has been updated successfully!', 'success')
                return redirect(url_for('main.home'))
        return render_template('update_model.html', form=form, models=models)
    else:
        flash(f'There are no models in the database!', 'info')
        return redirect(url_for('main.home'))
