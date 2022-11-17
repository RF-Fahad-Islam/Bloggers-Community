from flask import Flask, abort, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_admin import Admin, AdminIndexView, expose, BaseView
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from flask_msearch import Search
import os

# App and DB configuration
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://bloggers_community_user:SBSIwvrOMsiHjhPw6cfpZyEjmpkUIgI6@dpg-cdqs2mmn6mpqj2cjcncg-a.singapore-postgres.render.com/bloggers_community"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = os.environ.get("SQLALCHEMY_TRACK_MODIFICATIONS")
app.secret_key = "super-secret-key"
app.config["SESSION_TYPE"] = 'sqlalchemy'
db = SQLAlchemy(app)
app.config["SESSION_SQLALCHEMY"] = db
# app.config['FLASK_ADMIN_SWATCH'] = 'paper'
Session(app)

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