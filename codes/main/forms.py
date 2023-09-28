from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from ..validations import Validators
from flask_login import current_user


class LoginForm(FlaskForm):
	"""Form for taking the details from all users to log in to the website"""
	email = StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired()])
	remember = BooleanField('Remember Me')
	submit = SubmitField('Log In')


class RequestResetForm(FlaskForm, Validators):
	"""Form for taking the email of the user for the reset password"""
	mail = StringField('Email', validators=[DataRequired(), Email()])
	submit = SubmitField('Request Password Reset')


class ResetPasswordForm(FlaskForm, Validators):
	"""Form for taking a new password to change the password of the user"""
	password = PasswordField('Password', validators=[DataRequired()])
	confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField('Reset Password')


class UpdateAccountForm(FlaskForm, Validators):
	"""Form for taking the details of the user to update the account of the user"""
	username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
	email = StringField('Email', validators=[DataRequired(), Email()])
	name = StringField('Name', validators=[DataRequired(), Length(min=2, max=20)])
	city_id = IntegerField('City', validators=[DataRequired()])
	submit = SubmitField('Update!')

	def validate_username(self, username):
		if username.data != current_user.username:
			Validators.validate_username(self, username)

	def validate_email(self, email):
		if email.data != current_user.email:
			Validators.validate_email(self, email)


class ChangePassword(FlaskForm, Validators):
	"""Form for taking the current and new password of the user to change the password of the user"""
	form_password = PasswordField('Password', validators=[DataRequired()])
	password = PasswordField('Password', validators=[DataRequired()])
	confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField('Change!')


class SearchForm(FlaskForm):
	"""Form for entering the search word so that the cars can be searched according to that word"""
	searched = StringField('searched', validators=[DataRequired()])
	search = SubmitField('Search')
