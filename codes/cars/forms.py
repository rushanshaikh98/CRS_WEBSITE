from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, Length
from ..validations import Validators


class CreateCars(FlaskForm, Validators):
	"""Form for taking the details of a car from the admin to add a car in the Car model"""
	car_id = StringField('Number_plate', validators=[DataRequired(), Length(min=2, max=20)])
	company_id = IntegerField('Company', validators=[DataRequired()])
	category_id = IntegerField('Category', validators=[DataRequired()])
	model_id = IntegerField('Model', validators=[DataRequired()])
	color = StringField('Color', validators=[DataRequired()])
	mileage = IntegerField('Mileage', validators=[DataRequired()])
	ppd = IntegerField('Price Per Day', validators=[DataRequired()])
	min_rent = IntegerField('Minimum Rent', validators=[DataRequired()])
	deposit = IntegerField('Deposit Amount', validators=[DataRequired()])
	city_id = IntegerField('City', validators=[DataRequired()])
	submit = SubmitField('Create Car!')


class GetCar(FlaskForm, Validators):
	"""Form for taking the car id from the admin to get a car for different purposes"""
	car = StringField('Number_plate', validators=[DataRequired()])
	submit = SubmitField('Get Car!')


class UpdateCar(FlaskForm, Validators):
	"""Form for taking the details of a car from the admin to update it in the Car model"""
	color = StringField('Color', validators=[DataRequired()])
	mileage = IntegerField('Mileage', validators=[DataRequired()])
	ppd = IntegerField('Price Per Day', validators=[DataRequired()])
	min_rent = IntegerField('Minimum Rent', validators=[DataRequired()])
	deposit = IntegerField('Deposit Amount', validators=[DataRequired()])
	city_id = IntegerField('City')
	status = StringField('Final Status', validators=[DataRequired()])
	submit = SubmitField('Update Car!')


class ReturnCar(FlaskForm):
	"""Form for entering the details of the car after it is reviewed by the admin"""
	said_date = StringField('Said Date', validators=[DataRequired()])
	said_time = StringField('Said Time', validators=[DataRequired()])
	proper_condition = StringField('Proper Condition', validators=[DataRequired()])
	description = TextAreaField('Description')
	fine = IntegerField('Fine Amount')
	submit = SubmitField('Add Details!')


class CarMaintenance(FlaskForm):
	"""Form for accepting the description of the car from admin for maintaining it"""
	description = TextAreaField('Description', validators=[DataRequired()])
	submit = SubmitField('Done!')
