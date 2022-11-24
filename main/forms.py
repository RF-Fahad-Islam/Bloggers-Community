# Flask WTF Forms Classes for forms management
from flask_wtf import FlaskForm
from wtforms.fields import StringField, PasswordField,SubmitField, TextAreaField, IntegerField
from wtforms.fields.simple import HiddenField
from wtforms.validators import Length, DataRequired, EqualTo, Email, ValidationError, Optional
from .models import Users, Posts
from flask_login import current_user
from .utilities import string_to_slug

class RegisterForm(FlaskForm):
    def validate_email(self, email):
        user = Users.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError(f"'{email.data}' Email Already Exitsts! Please try with different email.")
    
    def validate_username(self, username):
        user = Users.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError(f"'{username.data}' is not available. Please try a different username.")
                                    
    firstname = StringField(label="First Name", validators=[DataRequired(), Length(min=2, max=15)])
    lastname = StringField(label="Last Name", validators=[DataRequired(), Length(min=2, max=15)])
    email = StringField(label="Email", validators=[DataRequired(), Email()])
    username = StringField(label="Username", validators=[DataRequired(), Length(min=3, max=30)])
    country = StringField(label="Country", validators=[DataRequired()])
    work = StringField(label="Profession", validators=[DataRequired()])
    password = PasswordField(label="Password", validators=[DataRequired(), Length(min=6, max=30)])
    repassword = PasswordField(label="Confirm Password", validators=[EqualTo('password')])
    submit = SubmitField(label="Create Account")
    
class LoginForm(FlaskForm):
    def validate_email(self, email):
        user = Users.query.filter_by(email=email.data).first()
        if not user: #If User doesn't exists
            raise ValidationError(f"Account Doesn't exists! Create a account and then try again.")
    def validate_password(self, password):
        user = Users.query.filter_by(email=self.email.data).first()
        if not user.check_password(password.data): #If User doesn't exists
            raise ValidationError(f"Wrong Password. Try again.")
        
    email = StringField(label="Email")
    password = PasswordField(label="Password",validators=[DataRequired(),Length(min=6, max=30)])
    submit = SubmitField(label="Login")
    
class BlogWriter(FlaskForm):
    def validate_title(self, title):
        post = current_user.posts.filter_by(slug=string_to_slug(title.data)).first()
        if int(self.sno.data) == 0 and post:
            raise ValidationError("Title can't be duplicated! Blog Title is similar to one of your blogs. Change the title.")
    
    def validate_tag(self,tag):
        tags_list = tag.data.split(" ")
        for t in tags_list:
            if tags_list.count(t)>1: #if duplicate tag found
                raise ValidationError(f"You can use a tag only once a post. '{t}' tag use more than once.")
    def validate_summmary(self, summary):
        if len(summary.data)>200:
            raise ValidationError(f"SEO Description exceeds 200 characters limit.")
    
    title = StringField(label="Title", validators=[DataRequired(), Length(min=10, max=120)])
    body = TextAreaField(label="body", validators=[DataRequired(), Length(min=15)])
    summary = TextAreaField(label="body", validators=[Length(max=200)])
    tag = StringField(label="tag", validators=[DataRequired(), Length(min=3, max=50)])
    sno =  HiddenField(label="sno", validators=[DataRequired()])
    submit = SubmitField(label="Publish Blog")
    
class NoticeForm(FlaskForm):
    title = StringField(label="Title", validators=[DataRequired(), Length(min=3, max=100)])
    desc = TextAreaField(label="Descrption", validators=[DataRequired(), Length(max=300)])
    submit = SubmitField(label="Create Notice")
    
class SettingForm(RegisterForm, FlaskForm):
    def validate_username(self, username):
        user = Users.query.filter_by(username=username.data).first()
        if user != None and user.username != current_user.username:
            raise ValidationError(f"'{username}' - username already exists. Choose a different username.")
    def validate_email(self, email):
        pass
    email = StringField(label="Email")
    age = IntegerField(label="Age", validators=[Optional(strip_whitespace=True)])
    weblink = StringField(label="Your website or social Link", validators=[Optional(strip_whitespace=True)])
    hobbies = StringField(label="Hobbies", validators=[Optional(strip_whitespace=True)], default="Blogging")
    brand_color = StringField(label="Brand Color", default="black")
    bio = StringField(label="Bio",default="I am new (^_^)", validators=[Length(min=4, max=101)])
    password = PasswordField(label="password")
    submit = SubmitField(label="Update Profile")
    
class CommentForm(FlaskForm):
    def validate_comment(self,body):
        if len(body)>500:
            raise ValidationError(f"Comment Can't be greater than 500 characters")
    body = TextAreaField(label='body',validators=[DataRequired(), Length(min=3, max=500)])
    to = StringField(label="to")
    url = StringField(label="url")
    submit = SubmitField(label="Post")
        
