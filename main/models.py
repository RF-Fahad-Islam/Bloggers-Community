# !Database Models Here+-
from . import db, admin, MyModelView, app
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

#MANY to MANY Relationship
user_blog_channel = db.Table('user_blog_channel',
    db.Column("user_id", db.Integer, db.ForeignKey('users.sno')),
    db.Column("blog_profile_id", db.Integer, db.ForeignKey('blogprofile.sno')),
)

user_reading_list = db.Table('user_reading_list',
    db.Column("post_id", db.Integer, db.ForeignKey('posts.sno')),
    db.Column("reading_list_id", db.Integer, db.ForeignKey('readinglists.sno')),
)


class Users(db.Model, UserMixin):
    sno = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.String(30), unique=True, nullable=False)
    firstname = db.Column(db.String(30), nullable=False)
    lastname = db.Column(db.String(30), nullable=False)
    username = db.Column(db.String(30), nullable=False, unique=True)
    picture = db.Column(db.String(200), nullable=True, default='avatar')
    age = db.Column(db.Integer, nullable=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(500), nullable=False)
    bio = db.Column(db.String(101), nullable=True, default="")
    country = db.Column(db.String(15), nullable=True, default="")
    hobbies = db.Column(db.String(200), nullable=True, default="Blogging")
    work = db.Column(db.String(200), nullable=True)
    webLink = db.Column(db.String(500), nullable=True, default="")
    brand_color = db.Column(db.String(30), nullable=True, default="#009EFF")
    joined_date = db.Column(db.DateTime, nullable=True,
                            default=datetime.utcnow)
    comments = db.relationship('Comment', backref='commentor', lazy='dynamic')
    # Returns List of posts that the user created
    posts = db.relationship('Posts', backref="writer", lazy="dynamic")
    readinglist = db.relationship('Readinglists', backref="user",uselist=False)
    # reading_lists = db.relationship('ReadingList', backref="creator", lazy="dynamic")
    
    following = db.relationship('Blogprofile', secondary=user_blog_channel, backref="followers")
    # blog_profile = db.relationship('BlogProfile', backref='user', lazy=True, uselist=False)
    # role = db.Column(db.Integer, db.ForeignKey('role.id'))
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    is_blocked = db.Column(db.Boolean, nullable=True, default=False)
    is_verified = db.Column(db.Boolean, nullable=True, default=False)

    def __repr__(self):
        return f"<User {self.username}>"

    def check_password(self, attempted_password):
        # Test Password Correction
        return check_password_hash(self.password_hash, attempted_password)

    def get_id(self):
        return (self.sno)

    @property
    def password(self):
        return self.password

    @password.setter
    def password(self, attemted_password):
        self.password_hash = generate_password_hash(
            attemted_password, method="sha1")


class Blogprofile(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    # Stores the given id of user and and saves the user object in writer_user
    usersno = db.Column(db.Integer, db.ForeignKey('users.sno'))
    def __repr__(self):
        return f"<Profile {self.sno}>"
    
class Readinglists(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    # Stores the given id of user and and saves the user object in writer_user
    usersno = db.Column(db.Integer, db.ForeignKey('users.sno'))
    blogs = db.relationship('Posts', secondary=user_reading_list, backref="reading_lists")
    def __repr__(self):
        return f"Usersno {self.usersno}"

class Urlshortner(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    point_to = db.Column(db.Text, nullable=False)
    pointer = db.Column(db.String(8), nullable=False, unique=True)
    
class Posts(db.Model):
    __tablename__ = "posts"
    __searchable__ = ["title", "tag", "summary"]
    sno = db.Column(db.Integer, primary_key=True)
    summary = db.Column(db.String(200), nullable=True, default="")
    slug = db.Column(db.String(500), nullable=False)
    title = db.Column(db.String(500), nullable=False, unique=False)
    tag = db.Column(db.String(500), nullable=True)
    body = db.Column(db.Text, nullable=False)
    public = db.Column(db.Boolean, nullable=False, default=True)
    pub_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    viewers_count = db.Column(db.Integer, nullable=False, default=0)
    thumbnail = db.Column(db.String(100), nullable=True)
    # Stores the given id of user and and saves the user object in writer_user
    writer_id = db.Column(db.Integer, db.ForeignKey('users.sno'))
    # comments = db.relationship('Comments', backref='post', lazy='dynamic')
    
    @property
    def publish_date(self):
        if self.pub_date.strftime("%b %d, %Y") == datetime.utcnow.strftime("%b %d, %Y"):
            return "Today"
        elif self.pub_date.strftime("%Y") == datetime.utcnow.strftime("%Y"):
            return self.pub_date.strftime("%b %d")
        else:
            return self.pub_date.strftime("%b %d, %Y")
    @property
    def views(self):
        value = self.viewers_count
        if self.viewers_count >= 1000000:
            value = "%.0f%s" % (self.viewers_count/1000000.00, 'M')
        else:
            if self.viewers_count >= 1000:
                value = "%.0f%s" % (self.viewers_count/1000.0, 'k')
        return value

    @property
    def tags_list(self):
        return self.tag.split(" ")

    def __repr__(self):
        return f"<Post {self.title}>"


class Notices(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(30), nullable=False)
    desc = db.Column(db.String(500), nullable=False)
    create_date = db.Column(db.DateTime, nullable=True,
                            default=datetime.utcnow)



class Comment(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    usersno = db.Column(db.Integer, db.ForeignKey('users.sno'))
    body = db.Column(db.String(500), nullable=False)
    to = db.Column(db.String(500), nullable=True)
    create_date = db.Column(db.DateTime, nullable=True,
                            default=datetime.utcnow)
    # replies = db.relationship('SubComment', backref="thread", lazy="dynamic")
    def __repr__(self):
        return f"{self.body}"
# class SubComment(db.Model):
#     sno = db.Column(db.Integer, primary_key=True)
#     comsno = db.Column(db.Integer, db.ForeignKey('comment.sno'))
#     body = db.Column(db.String(500), nullable=True)
    

# class Roles(db.Model):
#     sno = db.Column(db.Integer(), primary_key=True)
#     name = db.Column(db.String(30), nullable=False, unique=True)
#     desc = db.Column(db.String(), nullable=True)
#     users = db.relationship('User', backref="role", lazy=True)
with app.app_context():
    db.create_all()

#! Admin Views
admin.add_view(MyModelView(Users, db.session))
admin.add_view(MyModelView(Posts, db.session))
admin.add_view(MyModelView(Notices, db.session))
admin.add_view(MyModelView(Comment, db.session))
admin.add_view(MyModelView(Blogprofile, db.session))
admin.add_view(MyModelView(Readinglists, db.session))
admin.add_view(MyModelView(Urlshortner, db.session))
