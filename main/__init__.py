from flask import Flask, abort, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_migrate import Migrate
from flask_login import LoginManager, login_required
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from flask_msearch import Search
from authlib.integrations.flask_client import OAuth
from .settings import *
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail
from dotenv import load_dotenv
import os
load_dotenv('.env')
# from flask_uploads import UploadSet, configure_uploads, IMAGES

CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'
    
# App and DB configuration
app = Flask(__name__)
# photos = UploadSet('photos', IMAGES)

#Authlib
oauth = OAuth()
csrf = CSRFProtect(app)

# if PROD:
#     app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI_PROD
# elif TEST:
#     app.config["SQLALCHEMY_DATABASE_URI"] = TEST_URI
# else:
#     app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI_DEV
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("SQLALCHEMY_DATABASE_URI")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = SQLALCHEMY_TRACK_MODIFICATIONS
app.config["SESSION_TYPE"] = SESSION_TYPE
app.config["UPLOAD_PHOTOS_DEST"] = 'static/images'
# configure_uploads(app,photos)
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT = '465',
    MAIL_USE_SSL = True,
    MAIL_USERNAME = 'riyad9949@gmail.com',
    MAIL_PASSWORD = "gfbillzmmkbojpnp",
    SECRET_KEY='192b9bdd22ab9ed4d12e236c78afcb9a393ec15f71bbf5dc987d54727823bcbf',
    SQLALCHEMY_TRACK_MODIFICATIONS= SQLALCHEMY_TRACK_MODIFICATIONS,
)
db = SQLAlchemy(app)
app.config["SESSION_SQLALCHEMY"] = db
# app.config['FLASK_ADMIN_SWATCH'] = 'paper'
session = Session(app)
oauth.init_app(app)
mail = Mail(app)

google = oauth.register(
    name='google',
    server_metadata_url=CONF_URL,
    client_id= os.environ.get("GOOGLE_CLIENT_ID"),
    client_secret = os.environ.get("GOOGLE_CLIENT_SECRET"),
    client_kwargs={
        'scope': 'openid email profile'
    }
)

#Configure the M_Search
search = Search(app)


#Login Manager Configuration
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "warning"

#Register Error
def page_not_found(e):
    return render_template("404.html"), 404

#Register Error
def server_error(e):
    return render_template("500.html"), 500

app.register_error_handler(404, page_not_found)
app.register_error_handler(500, server_error)




#Configure Admin Panel
class MyModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin
    def inaccessible_callback(self, name, **kwargs):
        return abort(404)

# class MyHomeView(AdminIndexView):
#     def is_accessible(self):
#         return (current_user.is_authenticated and current_user.is_admin)
#     def inaccessible_callback(self, name, **kwargs):
#         return abort(404)

# class MyHomeView(AdminIndexView):
#     @expose('/')
#     def index(self):
#         arg1 = 'Hello'
#         return self.render('admin/index.html', arg1=arg1)
#     def is_accessible(self):
#         return (current_user.is_authenticated and current_user.is_admin)
#     def inaccessible_callback(self, name, **kwargs):
#         return abort(404)

admin = Admin(app, name="Bloggers Community")
login_manager.session_protection = SESSION_MANAGER_STRICT
#Static file Protector
# app.view_functions['static'] = login_required(app.send_static_file)
# Database Migrations Setup
migrate = Migrate(app,db)
from . import routes