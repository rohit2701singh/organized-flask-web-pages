# Creates the Flask app instance, Loads configurations
# Initializes extensions like SQLAlchemy & Flask-Login
# Registers Blueprints (for modular routing)
# Always be mindful of where and how you're importing modules, otherwise you will caught in circular import and app will crash

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app.config["SECRET_KEY"] = os.getenv('SECRET_PROTECTION_KEY')
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users_info.db"

db = SQLAlchemy()
db.init_app(app)

bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"

from myapp import routes
# we have imported routes here so that when we run our run.py file it can find those. By why not at the top?
# we have not imported it at the top because our routes.py is importing our 'app' variable. 
# So we can't import this at the top of the file or else we'll get into circular imports.