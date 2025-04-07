# Creates the Flask app instance, Loads configurations
# Initializes extensions like SQLAlchemy & Flask-Login
# Registers Blueprints (for modular routing)q
# Always be mindful of where and how you're importing modules, otherwise you will caught in circular import and app will crash
# flask-admin- https://gpttutorpro.com/how-to-use-flask-admin-to-create-an-admin-interface-for-your-web-application/


from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, current_user
import os
from dotenv import load_dotenv
from flask_ckeditor import CKEditor

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

app.config['CKEDITOR_ENABLE_CODESNIPPET'] = True
app.config['CKEDITOR_HEIGHT'] = 300
app.config['CKEDITOR_PKG_TYPE'] = 'full'

ckeditor = CKEditor()
ckeditor.init_app(app)


from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from myapp.models import Post, User


class AdminModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == 'Admin'


# AttributeError: 'tuple' object has no attribute 'items' when creating User object in Admin page. 
# Regression was introduced in WTForms==3.2.1. (use WTForms==3.1.2)
class UserView(AdminModelView):
    can_create = True
    can_edit = True
    can_delete = True
    
    form_columns = ["username", "email", "password", "image_file", "role"]

    column_list = ['id', 'username', 'email', 'password', 'image_file', 'role']
    column_labels = {'id': 'Id', 'username': 'Username', 'email': 'Email Address', 'password': 'Password', 'image_file': 'Image File', 'role':'Role'}
    column_filters = ('id', 'username', 'email', 'image_file', 'role')
    column_editable_list = ['username', 'email', 'image_file', 'role']

    # Override the on_model_change method to hash the password
    def on_model_change(self, form, model, is_created):
        model.password = bcrypt.generate_password_hash(model.password).decode('utf-8')


class PostView(AdminModelView):
        can_create = True
        can_delete = True
        can_edit = True
        page_size = 8  # the number of entries to display on the list view

        column_list = ["title", "date_posted", "content", "author"]
        column_labels = {'title': 'Title', 'date_posted': 'Date Posted', 'content': 'Content', 'author': 'Author'}
        column_filters = ('title', 'date_posted', 'author')

        def _format_author(view, context, model, name): # or use v,c,m,p as argument
            return f"id: {model.author.id} ({model.author.username})"

        column_formatters = {"author": _format_author, "content" : lambda v, c, m, p: m.content[:500] + '......'}   #  truncates the content column to 500 characters and adds an ellipsis
        
        form_columns = ("title", "date_posted", "content", "user_id")


app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
admin = Admin() # /admin in URL
admin.init_app(app)

admin.add_view(UserView(User, db.session))
admin.add_view(PostView(Post, db.session))


from myapp import routes
# we have imported routes here so that when we run our run.py file it can find those. By why not at the top?
# we have not imported it at the top because our routes.py is importing our 'app' variable. 
# So we can't import this at the top of the file or else we'll get into circular imports.