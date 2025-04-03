# Creates the Flask app instance, Loads configurations
# Initializes extensions like SQLAlchemy & Flask-Login
# Registers Blueprints (for modular routing)
# Always be mindful of where and how you're importing modules, otherwise you will caught in circular import and app will crash

from flask import Flask, redirect, url_for, abort
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, current_user
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


from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from myapp.models import Post, User


class AdminModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == 'Admin'


class UserView(AdminModelView):
    can_create = True
    can_edit = True
    can_delete = True
    
    form_columns = ["id", "username", "email", "password", "image_file"]

    column_list = ['id', 'username', 'email', 'password', 'image_file']
    column_labels = {'id': 'Id', 'username': 'Username', 'email': 'Email Address', 'password': 'Password', 'image_file': 'Image File'}
    column_filters = ('id', 'username', 'email', 'image_file')


class PostView(AdminModelView):
        can_create = True
        can_delete = True
        can_edit = True
        page_size = 8  # the number of entries to display on the list view

        form_columns = ["title", "date_posted", "content", "user_id"]

        column_list = ["title", "date_posted", "content", "author"]
        column_labels = {'title': 'Title', 'date_posted': 'Date Posted', 'content': 'Content', 'author': 'Author'}
        column_filters = ('title', 'date_posted', 'author')

        def _format_author(view, context, model, name):
            return f"id: {model.author.id} ({model.author.username})"  # Display the username instead of `user_id`

        column_formatters = {"author": _format_author}
        

app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
admin = Admin() # /admin in URL
admin.init_app(app)

admin.add_view(UserView(User, db.session))
admin.add_view(PostView(Post, db.session))


from myapp import routes
# we have imported routes here so that when we run our run.py file it can find those. By why not at the top?
# we have not imported it at the top because our routes.py is importing our 'app' variable. 
# So we can't import this at the top of the file or else we'll get into circular imports.