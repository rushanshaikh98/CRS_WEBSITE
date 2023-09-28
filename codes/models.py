from sqlalchemy.orm import backref
from . import db, login_manager
from datetime import datetime
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app


@login_manager.user_loader
def load_user(user_id):
	"""For loading the user into the website"""
	return User.query.get(int(user_id))


class City(db.Model):
	"""Class for adding the table cities into the database"""
	__tablename__ = 'cities'

	id = db.Column(db.Integer, primary_key=True)
	city = db.Column(db.String(60), unique=True, nullable=False)


class User(db.Model, UserMixin):
	"""Class for adding the table users into the database"""
	__tablename__ = 'users'

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(60), nullable=False)
	username = db.Column(db.String(50), unique=True, nullable=False)
	email = db.Column(db.String(50), unique=True, nullable=False)
	password = db.Column(db.String(60), nullable=False)
	city_id = db.Column(db.Integer, db.ForeignKey('cities.id', ondelete='SET NULL'), nullable=True)
	city = db.relationship("City", backref=backref("cities_users", uselist=False))
	is_verified = db.Column(db.Boolean, default=False)
	is_admin = db.Column(db.Boolean, default=False)
	is_super_admin = db.Column(db.Boolean, default=False)
	fine_pending = db.Column(db.Boolean, default=False)

	def get_reset_token(self, expires_sec=1800):
		s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
		return s.dumps({'user_id': self.id}).decode('utf-8')

	@staticmethod
	def verify_reset_token(token):
		s = Serializer(current_app.config['SECRET_KEY'])
		try:
			user_id = s.loads(token)['user_id']
		except:
			return None
		return User.query.get(user_id)


class CarModels(db.Model):
	"""Class for adding the table car_models into the database"""
	__tablename__ = 'car_models'

	id = db.Column(db.Integer, primary_key=True)
	model_name = db.Column(db.String(60), unique=True, nullable=False)


class CarCompany(db.Model):
	"""Class for adding the table car_companies into the database"""
	__tablename__ = 'car_companies'

	id = db.Column(db.Integer, primary_key=True)
	company_name = db.Column(db.String(60), unique=True, nullable=False)


class CarCategories(db.Model):
	"""Class for adding the table car_categories into the database"""
	__tablename__ = 'car_categories'

	id = db.Column(db.Integer, primary_key=True)
	category = db.Column(db.String(60), unique=True, nullable=False)


class Car(db.Model):
	"""Class for adding the table cars into the database"""
	__tablename__ = 'cars'

	id = db.Column(db.Integer, primary_key=True)
	car_id = db.Column(db.String(50), unique=True, nullable=False)
	company_id = db.Column(db.Integer, db.ForeignKey('car_companies.id', ondelete='SET NULL'), nullable=True)
	company = db.relationship("CarCompany", backref=backref("car_companies", uselist=False))
	category_id = db.Column(db.Integer, db.ForeignKey('car_categories.id', ondelete='SET NULL'), nullable=True)
	category = db.relationship("CarCategories", backref=backref("car_categories", uselist=False))
	model_id = db.Column(db.Integer, db.ForeignKey('car_models.id', ondelete='SET NULL'), nullable=True)
	model = db.relationship("CarModels", backref=backref("car_models", uselist=False))
	color = db.Column(db.String(20), nullable=False)
	mileage = db.Column(db.Integer, nullable=False)
	ppd = db.Column(db.Integer, nullable=False)
	min_rent = db.Column(db.Integer, nullable=False)
	city_id = db.Column(db.Integer, db.ForeignKey('cities.id', ondelete='SET NULL'), nullable=True)
	city = db.relationship("City", backref=backref("cities_cars", uselist=False))
	deposit = db.Column(db.Integer, nullable=False)
	status = db.Column(db.String(20), nullable=True, default=True)


class Rented(db.Model):
	"""Class for adding the table rented into the database"""
	__tablename__ = 'rented'

	booking_id = db.Column(db.Integer, primary_key=True)
	carID = db.Column(db.Integer, db.ForeignKey("cars.id", ondelete='SET NULL'), nullable=True)
	car = db.relationship("Car", backref=backref("cars_rented", uselist=False))
	user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
	person = db.relationship("User", backref=backref("users_rented", uselist=False))
	booking_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	rented_from = db.Column(db.DateTime, nullable=False)
	rented_till = db.Column(db.DateTime, nullable=False)
	car_taken = db.Column(db.Boolean, default=False)
	car_delivery = db.Column(db.Boolean, default=False)
	city_taken_id = db.Column(db.Integer, db.ForeignKey('cities.id', ondelete='SET NULL'), nullable=True)
	city_taken = db.relationship("City", backref=backref("cities_taken", uselist=False), foreign_keys=[city_taken_id])
	city_delivery_id = db.Column(db.Integer, db.ForeignKey('cities.id', ondelete='SET NULL'), nullable=True)
	city_delivery = db.relationship("City", backref=backref("cities_delivery", uselist=False),
									foreign_keys=[city_delivery_id])
	final_status = db.Column(db.String(30), default=True)
	said_date = db.Column(db.Boolean, default=True)
	said_time = db.Column(db.Boolean, default=True)
	proper_condition = db.Column(db.Boolean, default=True)
	description = db.Column(db.String(200))
	fine = db.Column(db.Integer, default=0)
	fine_paid = db.Column(db.Boolean, default=False)


class UserVerification(db.Model):
	"""Class for adding the table user_verification into the database"""
	__tablename__ = 'user_verification'

	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
	person = db.relationship("User", backref=backref("users_verify", uselist=False))
	id_proof = db.Column(db.String(60), nullable=False)
	approval = db.Column(db.String(60), nullable=False)
	date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class Maintenance(db.Model):
	"""Class for adding the table maintenance into the database"""
	__tablename__ = 'maintenance'

	id = db.Column(db.Integer, primary_key=True)
	carID = db.Column(db.Integer, db.ForeignKey("cars.id", ondelete='SET NULL'), nullable=True)
	car = db.relationship("Car", backref=backref("cars_maintenance", uselist=False))
	date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	description = db.Column(db.String(200), nullable=False)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
	person = db.relationship("User", backref=backref("users_maintenance", uselist=False))


class Temporary(db.Model):
	"""Class for adding the table temporary into the database"""
	__tablename__ = 'temporary'

	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
	person = db.relationship("User", backref=backref("users_temp", uselist=False))
	booking_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	rent_from = db.Column(db.DateTime, nullable=False)
	rent_till = db.Column(db.DateTime, nullable=False)
	city_id = db.Column(db.Integer, db.ForeignKey('cities.id', ondelete='SET NULL'), nullable=True)
	city = db.relationship("City", backref=backref("cities_temp", uselist=False))
