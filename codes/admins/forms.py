from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from ..validations import Validators


class CreateAdmins(FlaskForm, Validators):
	"""Form to take input from the super admin to create a new admin and validating the inputs provided
	if required when clicking on the submit button else submitting the data to method/class where the is called"""
	username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
	email = StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired()])
	confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
	name = StringField('Name', validators=[DataRequired(), Length(min=2, max=20)])
	city_id = IntegerField('City', validators=[DataRequired()])
	submit = SubmitField('Create Admin!')


class AddCity(FlaskForm, Validators):
	"""Form to take input of the city name from the super admin to add a new city into the City model and validating it if
	required"""
	city = StringField('City Name', validators=[DataRequired()])
	submit = SubmitField('Add City')


class AddCompany(FlaskForm, Validators):
	"""Form to take input of the company name from the super admin to add a new company into the CarCompany model and
	validating it if required"""
	company_name = StringField('Company Name', validators=[DataRequired()])
	submit = SubmitField('Add Company')


class AddCategory(FlaskForm, Validators):
	"""Form to take input of the category name from the super admin to add a new category into the CarCategories model and
	validating it if required"""
	category = StringField('Category', validators=[DataRequired()])
	submit = SubmitField('Add Category')


class AddModel(FlaskForm, Validators):
	"""Form to take input of the model name from the super admin to add a new model into the CarModels model and
	validating it if required"""
	model_name = StringField('Model Name', validators=[DataRequired()])
	submit = SubmitField('Add Model')


class DeleteCity(FlaskForm):
	"""Form to take input of the city name from super admin to delete the city"""
	city_id = IntegerField('City Name', validators=[DataRequired()])
	submit = SubmitField('Delete City')


class DeleteCompany(FlaskForm):
	"""Form to take input of the company name from super admin to delete the company"""
	company_id = IntegerField('Company Name', validators=[DataRequired()])
	submit = SubmitField('Delete Company')


class DeleteCategory(FlaskForm):
	"""Form to take input of the category name from super admin to delete the category"""
	category_id = IntegerField('Category Name', validators=[DataRequired()])
	submit = SubmitField('Delete Category')


class DeleteModel(FlaskForm):
	"""Form to take input of the model name from super admin to delete the model"""
	model_id = IntegerField('Model Name', validators=[DataRequired()])
	submit = SubmitField('Delete Model')


class UpdateCity(FlaskForm, Validators):
	"""Form for selecting the current city and entering the new city name in order to update name of the city"""
	city_id = IntegerField('City Name', validators=[DataRequired()])
	city = StringField(' New City Name', validators=[DataRequired()])
	submit = SubmitField('Update City')


class UpdateCompany(FlaskForm, Validators):
	"""Form for selecting the current company and entering the new company name in order to update name of the company"""
	company_name = StringField('Company Name', validators=[DataRequired()])
	company_id = IntegerField('Company Name', validators=[DataRequired()])
	submit = SubmitField('Update Company')


class UpdateCategory(FlaskForm, Validators):
	"""Form for selecting the current category and entering the new category name in order to update
	name of the category"""
	category = StringField('Category', validators=[DataRequired()])
	category_id = IntegerField('Category Name', validators=[DataRequired()])
	submit = SubmitField('Update Category')


class UpdateModel(FlaskForm, Validators):
	"""Form for selecting the current model and entering the new model name in order to update name of the model"""
	model_name = StringField('Model Name', validators=[DataRequired()])
	model_id = IntegerField('Model Name', validators=[DataRequired()])
	submit = SubmitField('Update Model')
