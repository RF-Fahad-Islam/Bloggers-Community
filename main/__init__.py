from flask import Flask, abort, render_template
from flask_sqlalchemy import SQLAlchemy as _BaseSQLAlchemy
from flask_session import Session
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_admin import Admin, AdminIndexView, expose, BaseView
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from flask_msearch import Search
from authlib.integrations.flask_client import OAuth
from .settings import *

CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'
    
# App and DB configuration
app = Flask(__name__)
#Authlib
oauth = OAuth()

if PROD:
    app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI_PROD
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI_DEV
    
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = SQLALCHEMY_TRACK_MODIFICATIONS
app.secret_key = SECRET_KEY
app.config["SESSION_TYPE"] = SESSION_TYPE
class SQLAlchemy(_BaseSQLAlchemy):
    def apply_pool_defaults(self, app, options):
        super(SQLAlchemy, self).apply_pool_defaults(self, app, options)
        options["pool_pre_ping"] = True
db = SQLAlchemy(app)
app.config["SESSION_SQLALCHEMY"] = db
# app.config['FLASK_ADMIN_SWATCH'] = 'paper'
Session(app)
oauth.init_app(app)
google = oauth.register(
    name='google',
    server_metadata_url=CONF_URL,
    client_id= GOOGLE_CLIENT_ID,
    client_secret = GOOGLE_CLIENT_SECRET,
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

app.register_error_handler(404, page_not_found)
app.register_error_handler(500, abort)

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
#     # @expose('/')
#     # def index(self):
#     #     arg1 = 'Hello'
#     #     return self.render('admin/index.html', arg1=arg1)
#     def is_accessible(self):
#         return (current_user.is_authenticated and current_user.is_admin)
#     def inaccessible_callback(self, name, **kwargs):
#         return abort(404)

admin = Admin(app, name="Bloggers Community")
#Static file Protector
# app.view_functions['static'] = login_required(app.send_static_file)
# Database Migrations Setup
migrate = Migrate(app,db)
from . import routes