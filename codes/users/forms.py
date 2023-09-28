from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, DateField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, Length, Email, EqualTo
from ..validations import Validators


class RegistrationForm(FlaskForm, Validators):
	"""Form for taking the details form to user to register to the website"""
	username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
	email = StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired()])
	confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
	name = StringField('Name', validators=[DataRequired(), Length(min=2, max=20)])
	city_id = IntegerField('City', validators=[DataRequired()])
	submit = SubmitField('Sign Up')


class ApprovalForm(FlaskForm):
	"""Form to taking the id proof from a user to verify that user"""
	id_proof = FileField('Upload your id proof', validators=[FileAllowed(['jpg', 'jpeg', 'png'])])
	submit = SubmitField('Send!')


class TakingDates(FlaskForm, Validators):
	"""Form for taking the dates from the user to book the cars"""
	rent_from = DateField('Rent From', format='%Y-%m-%d', validators=[DataRequired()])
	rent_till = DateField('Rent Till', format='%Y-%m-%d', validators=[DataRequired()])
	city_id = IntegerField('City', validators=[DataRequired()])
	submit = SubmitField('See Cars!')

	def validate_rent_till(self, rent_till):
		Validators.validate_rent_till(self.rent_from, rent_till)
