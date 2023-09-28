from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from .config import Config
from flask_mail import Mail

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'main.login'
login_manager.login_message_category = 'info'
mail = Mail()


def create_app(config_class=Config):
	"""Method for creating the app"""
	app = Flask(__name__)
	app.config.from_object(Config)
	app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
	db.init_app(app)
	mail.init_app(app)
	login_manager.init_app(app)
	from .main.routes import main
	from .cars.routes import cars
	from .users.routes import users
	from .admins.routes import admins
	from .errors.handlers import errors
	app.register_blueprint(main)
	app.register_blueprint(cars)
	app.register_blueprint(users)
	app.register_blueprint(admins)
	app.register_blueprint(errors)
	return app
