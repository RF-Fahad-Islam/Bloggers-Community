from . import db,app, login_manager, search,oauth
from flask import render_template, redirect, session, request, jsonify, url_for, flash, abort
from .models import Users, Posts, Notices
from .forms import RegisterForm, LoginForm, BlogWriter, SettingForm, NoticeForm
from .utilities import *
from flask_login import login_required, login_user, logout_user, current_user

params = {
    "page_title":"Bloggers Community | Made By Fahad",
    "app_name":"Bloggers Community",
    "url":"https://bloggers-community.onrender.com",
    "github":"https://github.com/RF-Fahad-Islam/",
    "admin_email":"riyad9949@gmail.com",
    "admin_password":"$$01308388895$$@Rf",
    "admin_userid":"I_AM_THE_CREATOR_OF_THIS_WEBSITE_FAHAD"
}

#Set Login Manager
@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

#Global Variables for templates
@app.context_processor
def context_processor():
    return dict(params=params)


@app.route("/")
def home():
    posts = Posts.query.all()
    notices = Notices.query.all()
    notices.reverse()
    posts.reverse()
    return render_template('index.html',notices=notices,  posts=posts)

# Handle Other Urls
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    abort(404)

@app.route("/tags")
def handleTags():
    tags = all_tags()
    return render_template('tags.html', tags=tags)

@app.route("/p/<string:username>")
def userProfile(username):
    user = db.one_or_404(db.select(Users).filter_by(username=username))
    posts = user.posts.all()
    total_viewers_count = total_viewers(posts) 
    return render_template("profile.html",  user=user,posts=posts, total_viewers=total_viewers_count)

# @app.route("/signup", methods=["GET", "POST"])
# def signup():
#     form = RegisterForm()
#     if form.validate_on_submit():
#         firstname = form.firstname.data
#         lastname = form.lastname.data
#         email = form.email.data
#         username = form.username.data
#         password = form.password.data
#         country = form.country.data
#         work = form.work.data
#         userid = generateId(30)
#         if email == params["admin_email"]:
#             is_admin = True
#         else:
#             is_admin = False
#         newUser = Users(firstname=firstname, lastname=lastname, userid=userid, country=country, email=email, username=string_to_slug(username), password=password, work=work, is_admin=is_admin)
#         db.session.add(newUser)
#         db.session.commit()
#         return redirect(url_for('login'))
#     flash_form_error_messages(form)
#     print(form.errors)
#     return render_template("signup.html",  form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if  user != None and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for("home"))
        else:
            flash_form_error_messages(form)
            
    flash_form_error_messages(form)
    return render_template("login.html", form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect("/")

@app.route('/settings', methods=["GET", "POST"])
def settingProfile():
    form = SettingForm()
    if form.validate_on_submit():
        firstname = form.firstname.data
        lastname = form.lastname.data
        username = form.username.data
        bio = form.bio.data
        brand_color = form.brand_color.data
        hobbies = form.hobbies.data
        work = form.work.data
        country = form.country.data
        webLink = form.weblink.data
        age = form.age.data
        attpassword = form.password.data
        #Update the values on Database
        user = Users.query.filter_by(sno=current_user.sno).first()
        if not attpassword == None:
            user.password = attpassword
            
        user.firstname = firstname
        user.lastname = lastname
        user.username = string_to_slug(username)
        user.bio = bio
        user.brand_color = brand_color
        user.hobbies = hobbies
        user.work = work
        user.country = country
        user.webLink = webLink
        user.age = age
        db.session.commit()
        
        flash("Successfully updated your profile!", category="success")
        return redirect(url_for('settingProfile'))
    
    flash_form_error_messages(form)
    
    return render_template("setting.html",  form=form)

@app.route('/b/<string:username>/<string:postSlug>')
def handleUsersPosts(username, postSlug):
    user = db.one_or_404(db.select(Users).filter_by(username=username))
    post = user.posts.filter_by(slug=postSlug).first()
    if post is None: return abort(404)
    try:
        if current_user.sno == user.sno: pass
    except:
         post.viewers_count += 1
    posts = user.posts.all()
    pos = posts.index(post)
    next_post = None
    prev_post = None
    if len(posts) >3:
        if pos > 0 and pos < len(posts)-1: #IF position of the post is in the middle
            next_post = posts[pos+1] #Next position
            prev_post = posts[pos-1]
        elif pos == 0 and posts[pos+1] != None:
            next_post = posts[pos+1]
        else:
            prev_post = posts[pos-1]
    recommendeds = Posts.query.msearch(post.tags_list[0], fields=["tag"]).order_by(Posts.viewers_count.desc())[:5]
    if not recommendeds and len(post.tags_list)>1:
        recommendeds = Posts.query.msearch(post.tags_list[1], fields=["tag"]).order_by(Posts.viewers_count.desc())[:5]
        
    recommendeds.remove(post)
    return render_template("blog.html",  post=post, user=user, next_post=next_post, prev_post=prev_post, recommendeds=recommendeds)

@app.route('/blog-writer/edit/<string:sno>', methods=["GET", "POST"])
@login_required
def handleBlogWriter(sno):
    form = BlogWriter()
    post = Posts.query.filter_by(sno=sno).first()
    if (post == None or post.writer_id != current_user.sno) and sno != "0" and not current_user.is_admin:
        return redirect("/blog-writer/edit/0")
    
    if form.validate_on_submit():
        slug = string_to_slug(form.title.data)
        if sno == "0":
            post = Posts(title=form.title.data, body=form.body.data, tag=form.tag.data, slug=slug, writer_id=current_user.sno)
            db.session.add(post)
            db.session.commit()
            flash("Successfully posted the blog! Thanks for posting.", category="success")
            return redirect(f"/b/{current_user.username}/{slug}")
        else:
            post = Posts.query.filter_by(sno=sno).first()
            if current_user.sno == post.writer_id:
                post.title = form.title.data
                post.body = form.body.data
                post.tag = form.tag.data
                post.slug = slug
                db.session.commit()
                flash(f"Successfully apply the updates on '{post.title}' post", category="success")
                return redirect(f"/b/{current_user.username}/{post.slug}")
            else:
                abort(404)
    flash_form_error_messages(form)
    return render_template("blogWriter.html",  post=post, sno=sno, form=form)

@app.route("/delete/<string:keyword>/<string:sno>")
@login_required
def handleDeletes(keyword,sno):
    if keyword == "b":
        post = Posts.query.filter_by(sno=sno).first()
        if post.writer_id == current_user.sno or current_user.is_admin:
            db.session.delete(post)
            db.session.commit()
            if current_user.is_admin:
                return redirect(url_for("adminDashboard"))
            else:
                return redirect(url_for("userDashboard"))
                    
    elif keyword == "p":
        if current_user.is_admin:
            user = Users.query.filter_by(sno=sno).first()
            posts = Posts.query.filter_by(userid=user.userid).all()
            for post in posts:
                db.session.delete(post)
                db.session.commit()
                
            db.session.delete(user)
            db.session.commit()
            return redirect(url_for("adminDashboard"))
        else:
            return redirect("/")
        
    elif keyword == "n":
        if current_user.is_admin:
            notice = Notices.query.filter_by(sno=sno).first()
            db.session.delete(notice)
            db.session.commit()
            return redirect(url_for("adminDashboard"))
    else:
        abort(404)

@app.route("/admin/dashboard")
@login_required
def adminDashboard():
    if current_user.is_admin:
        users = Users.query.all()
        posts = Posts.query.all()
        notices = Notices.query.all()
        form = NoticeForm()
        return render_template('adminPanel.html',posts=posts, users=users, notices=notices, form=form)
    else:
        abort(404)

@app.route("/dashboard")
@login_required
def userDashboard():
    posts = current_user.posts.all()
    total_views = total_viewers(posts)
    return render_template("dashboard.html",  posts=posts, total_views=total_views)

@app.route("/search", methods=["GET"])
def search():
    try:
        page = int(request.args.get("page"))
    except:
        page = 1
    q = request.args.get("q")
    searchType = request.args.get("type")
    if searchType == "tag":
        posts = Posts.query.msearch(q, fields=["tag"]).paginate(page=page, per_page=3)
    else:
        posts = Posts.query.msearch(q, fields=["title", "tag"]).paginate(page=page, per_page=3)
    return render_template("search.html",  posts=posts, q=q, searchType=searchType, url=request.url)


@app.route("/notices/create", methods=["GET", "POST"])
@login_required
def handleNotices():
    form = NoticeForm()
    if form.validate_on_submit():
        title = request.form.get("title")
        desc = request.form.get("desc")
        notice = Notices(title=title, desc=desc)
        db.session.add(notice)
        db.session.add(notice)
        db.session.commit()
        return redirect(url_for("adminDashboard"))
    return redirect("/")

@app.route("/usedUsernames")
def apiUsernames():
    users = Users.query.all()
    usedUsernames = {"usernames": []}
    for user in users:
        usedUsernames["usernames"].append(user.username)
    return jsonify(usedUsernames)

@app.route('/google-login')
def googleLogin():
    redirect_uri = url_for('authorize', _external=True)
    google = oauth.create_client('google')
    return google.authorize_redirect(redirect_uri)

@app.route('/authorize')
def authorize():
    token = oauth.google.authorize_access_token()

    user = token['userinfo']
    getUser = Users.query.filter_by(email=user.get('email')).first() 
    if not Users.query.filter_by(email=user.get('email')).first():
        userid = generateId(30)
        firstname = user.get('given_name')
        lastname = user.get('family_name')
        email = user.get('email')
        username = user.get('name')
        picture = user.get('picture')
        if email == params["admin_email"]:
            is_admin = True
        else:
            is_admin = False
        user = Users.query.filter_by(username=username.data).first()
        while user:
            if user != None and user.username != current_user.username:
                username= generateId(5)
            user = Users.query.filter_by(username=username.data).first()
        newUser = Users(firstname=firstname,picture=picture, lastname=lastname, userid=userid, email=email, username=string_to_slug(username), is_admin=is_admin, password=generateId(20))
        db.session.add(newUser)
        db.session.commit()
    else:
        getUser.picture = user.get('picture')
        db.session.commit()
        login_user(getUser)
    # print(profile)
    # do something with the token and profile
    return redirect('/')
