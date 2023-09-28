from wtforms.validators import ValidationError
from .models import User, Car, CarCompany, CarCategories, CarModels, City
import datetime


class Validators:
    """Class for validating different variables"""
    @staticmethod
    def validate_username(self, field):
        """Method for validating the username and checking if it already exists

        Args
        ------------------
        self: is used as the function is defined in the class
        field: It is the username entered by the user which needs to validated

        Returns
        ------------------
        True if the field is validated or raises a Validation error"""

        if " " not in field.data:
            user = User.query.filter_by(username=field.data).first()
            if user:
                raise ValidationError('Username is already taken!')
        else:
            raise ValidationError('Username cannot have spaces!')

    @staticmethod
    def validate_email(self, field):
        """Method for validating the email and checking if it already exists

        Args
        ------------------
        self: is used as the function is defined in the class
        field: It is the email entered by the user which needs to validated

        Returns
        ------------------
        True if the field is validated or raises a Validation error"""

        user = User.query.filter_by(email=field.data).first()
        if user:
            raise ValidationError('Email is already taken!')

    @staticmethod
    def validate_password(self, field):
        """Method for validating the password

        Args
        ------------------
        self: is used as the function is defined in the class
        field: It is the pass entered by the  user which needs to validated

        Returns
        ------------------
        True if the field is validated or raises a Validation error"""

        passwd = field.data
        special_chars = ['$', '@', '#', '%']
        error = ""
        if len(passwd) < 6:
            error += 'Length should be at least 6!\n'

        if len(passwd) > 20:
            error += 'Length should be not be greater than 20!\n'

        if not any(char.isdigit() for char in passwd):
            error += 'Password should have at least one numeral!\n'

        if not any(char.isupper() for char in passwd):
            error += 'Password should have at least one uppercase letter!\n'

        if not any(char.islower() for char in passwd):
            error += 'Password should have at least one lowercase letter!\n'

        if not any(char in special_chars for char in passwd):
            error += 'Password should have at least one of the symbols $@#%!\n'

        if len(error) > 0:
            raise ValidationError(f'{error}')

    @staticmethod
    def validate_rent_from(self, field):
        """Method for validating the entered dates

        Args
        ------------------
        self: is used as the function is defined in the class
        field: It is the rent from date entered by the user which needs to validated

        Returns
        ------------------
        True if the field is validated or raises a Validation error"""

        if field.data < datetime.date.today():
            raise ValidationError("The date cannot be in the past!")

    @staticmethod
    def validate_rent_till(rented_from, rented_till):

        """Method for validating the car ID and checking if it already exists

        Args
        ------------------
        rented_from: It is the car rent from date entered by the user which needs to validated
        rented_till: It is the car rent till date entered by the user which needs to validated

        Returns
        ------------------
        True if the field is validated or raises a Validation error"""

        if rented_till.data < datetime.date.today():
            raise ValidationError("The date cannot be in the past!")
        elif rented_till.data < rented_from.data:
            raise ValidationError("The rented till date cannot be less than the rented from date!")

    @staticmethod
    def validate_car_id(self, field):
        """Method for validating the car ID and checking if it already exists

        Args
        ------------------
        self: is used as the function is defined in the class
        field: It is the car id entered by the user which needs to validated

        Returns
        ------------------
        True if the field is validated or raises a Validation error"""

        car = Car.query.filter_by(car_id=field.data.replace(" ", "").upper()).first()
        if car:
            raise ValidationError('Car ID is already taken!')

    @staticmethod
    def validate_company_name(self, field):
        """Method for validating the company name and checking if it already exists

        Args
        ------------------
        self: is used as the function is defined in the class
        field: It is the car company name entered by the user which needs to validated

        Returns
        ------------------
        True if the field is validated or raises a Validation error"""

        company = CarCompany.query.filter_by(company_name=field.data.replace(" ", "").upper()).first()
        if company:
            raise ValidationError('Company already exists!')

    @staticmethod
    def validate_city(self, field):
        """Method for validating the city name and checking if it already exists

        Args
        ------------------
        self: is used as the function is defined in the class
        field: It is the city name selected by the user which needs to validated

        Returns
        ------------------
        True if the field is validated or raises a Validation error"""
        city = City.query.filter_by(city=field.data.replace(" ", "").upper()).first()
        if city:
            raise ValidationError('City already exists!')

    @staticmethod
    def validate_category(self, field):
        """Method for validating the category name and checking if it already exists

        Args
        ------------------
        self: is used as the function is defined in the class
        field: It is the category entered by the user which needs to validated

        Returns
        ------------------
        True if the field is validated or raises a Validation error"""

        category = CarCategories.query.filter_by(category=field.data.replace(" ", "").upper()).first()
        if category:
            raise ValidationError('Category already exists!')

    @staticmethod
    def validate_model_name(self, field):
        """Method for validating the model name and checking if it already exists

        Args
        ------------------
        self: is used as the function is defined in the class
        field: It is the model name entered by the user which needs to validated

        Returns
        ------------------
        True if the field is validated or raises a Validation error"""

        model = CarModels.query.filter_by(model_name=field.data.replace(" ", "").upper()).first()
        if model:
            raise ValidationError('Model already exists!')

    @staticmethod
    def validate_mail(self, field):

        """Method for validating the car ID and checking if it already exists

        Args
        ------------------
        self: is used as the function is defined in the class
        field: It is the email entered by the user which needs to checked

        Returns
        ------------------
        True if the field is validated or raises a Validation error"""

        user = User.query.filter_by(email=field.data).first()
        if user is None:
            raise ValidationError('There is no account with such email!')

    @staticmethod
    def validate_car(self, field):

        """Method for validating the car ID and checking if it already exists

        Args
        ------------------
        self: is used as the function is defined in the class
        field: It is the car id entered by the user which needs to validated

        Returns
        ------------------
        True if the field is validated or raises a Validation error"""

        car = Car.query.filter_by(car_id=field.data.replace(" ", "").upper()).first()
        if car is None:
            raise ValidationError('Car does not exist!')

