from bs4 import BeautifulSoup
import json
from sqlalchemy.sql.expression import func
from .settings import *
from . import db, app, login_manager, search, oauth,mail, socketio
from flask import render_template, redirect, session, request, jsonify, url_for, flash, abort, send_from_directory,make_response,Response
from .models import Users, Posts, Notices, Comments,Blogprofile, Readinglists, Urlshortner, Replies
from .forms import RegisterForm, LoginForm, BlogWriter, SettingForm, NoticeForm, CommentForm
from .utilities import *
from flask_login import login_required, login_user, logout_user, current_user
from .serializers import *
import random
from datetime import datetime
from werkzeug.security import generate_password_hash
# from flask_socketio import send, emit
import os
from werkzeug.utils import secure_filename
params = {
    "page_title": APP_TITLE,
    "app_name": APP_NAME,
    "url": APP_URL,
    "github": "https://github.com/RF-Fahad-Islam/",
    "admin_email": ADMIN_EMAIL,
    "admin_password": ADMIN_PASSWORD,
    "admin_userid": ADMIN_USERID
}
def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

with app.app_context():
    blogprofiles = Blogprofile.query.all()

# @socketio.on('message')
# def handle_message(data):
#     print('received message: ' + str(data))
    
# @socketio.on('connect')
# def handle_connect(data):
#     print('received message: ' + str(data))

@app.route('/rss.xml')
def rssgenerator():
    posts = Posts.query.all()
    with app.app_context():
        data = render_template('rss.xml', posts=posts)
        response = Response(
            data,
            mimetype='application/xml',
    #     headers={'Content-disposition': 'attachment; filename=data.pkl'})  
        )
        return response

@app.route('/sitemap.xml')
def sitemapgenerator():
    posts = Posts.query.all()
    with app.app_context():
        data = render_template('sitemap.xml', posts=posts)
        response = Response(
            data,
            mimetype='application/xml',
    #     headers={'Content-disposition': 'attachment; filename=data.pkl'})  
        )
        return response

# @app.route('/sitemap.xml')
# def static_from_root():
#     return send_from_directory(app.static_folder, 'sitemap.xml')

# @app.route('/manifest.json')
# def send_manifest_json():
#     return send_from_directory(app.static_folder, 'manifest.json')

# Set Login Manager and get user credentials as current_user
@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

# Global Variables for templates
@app.context_processor
def context_processor():
    return dict(params=params)


async def simple_send():
    await mail.send_message("HELLO", sender='riyad9949@gmail.com', recipients=['riyad9949@gmail.com'],body='HELLO THIS IS')


@app.route("/")
def home():
    posts = Posts.query.filter_by(public=True).all()
    notices = Notices.query.all()
    notices.reverse()
    return render_template('index.html', notices=notices,  posts=posts, tags=all_tags())

@app.route('/privacy-policy')
def privacy_policy():
    term = Posts.query.filter(Posts.tag == "privacy policy").first()
    return render_template('privacypolicy.html', term=term)

@app.route('/terms-and-conditions')
def termsandconditions():
    term = Posts.query.filter(Posts.tag == "terms conditons").first()
    return render_template('termsandconditions.html',term=term)

@app.route('/draft', methods=['POST'])
def draftpost():
    if request.method == "POST":
        title = request.form.get('title')
        content = request.form.get('content')
        tag = ""
        if len(title)<3 or len(title)>100 or len(content)>500 or "<script" in content: 
            flash("(XSS Protection) : Detected scripting code!", category="danger")
            return redirect('/')
        post = Posts(title=title, body=content, public=False,writer_id=current_user.sno, slug=string_to_slug(title),tag=tag)
        db.session.add(post)
        db.session.commit()
        flash(f'Successfully Saved the Draft : {title}')
        return redirect(url_for('userDashboard'))

# Handle Other Urls


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    abort(404)

#! HTMX ROUTES
@app.route('/get-blogs', methods=["GET"])
def blogs():
    if not request.headers.get('HX-Request'): abort(404)
    page = 1
    try:
        page = int(request.args.get('p'))
    except:
        page = 1
    posts = Posts.query.filter_by(public=True).order_by(Posts.pub_date.desc()).paginate(page=page,per_page=POSTS_PER_PAGE)
    return render_template('particles/blog.html', posts=posts, page=page, url="get-blogs?p=", showend=True)

@app.route('/get-recommendations', methods=["GET"])
def recommendations():
    if not request.headers.get('HX-Request'): abort(404)
    tag1 = request.args.get('t1')
    tag2 = request.args.get('t2')
    recommendeds = Posts.query.filter_by(public=True).msearch(tag1, fields=[
                                        "tag"]).order_by(Posts.viewers_count.desc()).limit(5).all()
    if not recommendeds and tag2:
        recommendeds = Posts.query.filter_by(public=True).msearch(tag2, fields=[
                                            "tag"]).order_by(Posts.viewers_count.desc()).limit(5).all()
    return render_template('particles/recommendation.html', recommendeds=recommendeds)

@app.route("/tags")
def handleTags():
    tags = all_tags()
    return render_template('tags.html', tags=tags)


@app.route("/@<string:username>")
def user(username):
    user = db.one_or_404(db.select(Users).filter_by(username=username))
    posts = user.posts.filter_by(public=True).order_by(Posts.pub_date.desc()).all()
    blogProfile = Blogprofile.query.filter_by(usersno=user.sno).first()
    if not current_user.is_anonymous:
        cnt = current_user.following.count(blogProfile)      
    else:
        cnt = 0
    total_viewers_count = total_viewers(posts)
    return render_template("profile.html",  user=user, posts=posts, blogProfile=blogProfile, total_viewers=total_viewers_count, cnt=cnt)

@app.route('/p/<string:username>')
def userProfile(username):
    return redirect('/@'+username)

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


# !Login System
# atm = 0


# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     global atm
#     form = LoginForm()
#     if atm > 3:
#         return redirect('/')
#     if form.validate_on_submit() and atm > 3:
#         user = Users.query.filter_by(email=form.email.data).first()
#         if user != None and user.check_password(form.password.data):
#             atm = 0
#             login_user(user)
#             return redirect(url_for("home"))
#         else:
#             atm += 1
#             flash_form_error_messages(form)
#             if atm > 3:
#                 return redirect('/')

#     flash_form_error_messages(form)
#     return render_template("login.html", form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect("/")


@app.route('/settings', methods=["GET", "POST"])
def settingProfile():
    form = SettingForm()
    try: blogProfile = Blogprofile.query.filter_by(usersno=current_user.sno).first()
    except: return redirect('googleLogin')
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
        # Update the values on Database
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

    return render_template("setting.html",  form=form, blogProfile=blogProfile)


@app.route('/b/<string:username>/<string:postSlug>', methods=["POST", "GET"])
def handleUsersPosts(username, postSlug):
    user = db.one_or_404(db.select(Users).filter_by(username=username))
    post = Posts.query.filter_by(slug=postSlug).first()
    if post is None: return abort(404)
    comments = Comments.query.filter_by(post_id=post.sno).order_by(Comments.create_date.desc()).all()
    #* Add viewers count
    try:
        if current_user.sno == user.sno:
            pass
    except:
        if session.get('viewed') is None:
            post.viewers_count += 1
            session['viewed'] = post.sno
    
    #TODO: Retrive the next blog and previous blog
    posts = user.posts.all()
    pos = posts.index(post)
    next_post = None
    prev_post = None
    if len(posts) > 3:
        # IF position of the post is in the middle
        if pos > 0 and pos < len(posts)-1:
            next_post = posts[pos+1]  # Next position
            prev_post = posts[pos-1]
        elif pos == 0 and posts[pos+1] != None:
            next_post = posts[pos+1]
        else:
            prev_post = posts[pos-1]
    
    recommendeds = Posts.query.filter_by(public=True).msearch(post.tags_list[0], fields=[
                                       "tag"]).order_by(Posts.viewers_count.desc()).limit(5).all()
    if not recommendeds and len(post.tags_list) > 1:
        recommendeds = Posts.query.filter_by(public=True).msearch(post.tags_list[1], fields=[
                                           "tag"]).order_by(Posts.viewers_count.desc()).limit(5).all()
    if not recommendeds:
        recommendeds = posts[:3]
    if post in recommendeds:
        recommendeds.remove(post)
        
    blogProfile = Blogprofile.query.filter_by(usersno=user.sno).first()
    urlshort = Urlshortner.query.filter_by(point_to=f"/b/{user.username}/{post.slug}").first()
    if urlshort is None or not urlshort:
        urlshort = Urlshortner(point_to=f"/b/{user.username}/{post.slug}", pointer=generate_pointer(4))
        db.session.add(urlshort)
        db.session.commit()
    shorturl = f'{params["url"]}/l?p={urlshort.pointer}'
    soup = BeautifulSoup(post.body, 'html.parser')
    if soup.find('img'): thumbnail = soup.find('img').get('src') or ""
    else: thumbnail = ""
    summary = post.summary
    if not summary or summary == "": soup.find('p').getText()[:144]
    return render_template("blog.html",  post=post, user=user, next_post=next_post, prev_post=prev_post, recommendeds=recommendeds
                           , blogProfile=blogProfile, shorturl=shorturl, thumbnail=thumbnail, summary=summary, comments=comments)



@app.route('/comment', methods=["POST","GET","DELETE","PUT"])
@login_required
def comment():
    if request.method == "PUT":
        form = request.form
        comsno = form.get('comsno')
        body = form.get('body')
        comment = Comments.query.filter_by(sno=comsno).first()
        comment.body = body
        db.session.commit()
        return comment.body
    if request.method == "DELETE":
        form = request.form
        comsno = form.get('comsno')
        comment = Comments.query.filter_by(sno=comsno).first()
        for reply in comment.replies:
            db.session.delete(reply)
            db.session.commit()
        db.session.delete(comment)
        db.session.commit()
        return render_template('particles/alert.html', msg='Comment has been removed', category='light bg-light')
    if request.method == "POST":
        form = request.form
        comsno = form.get("comsno")          
        from markdown import markdown
        body = markdown(form.get("body"))
        post_id = form.get("post_id")
        user = current_user
        comments = Comments.query.filter_by(post_id=post_id).filter_by(commentor=current_user).all()
        if len(comments)>10: return render_template('particles/alert.html', msg="You have reached max comment limit for the post", category='danger')
        for comment in comments:
            if comment.create_date.strftime('%H %M,%d %y') == datetime.now().strftime('%H %M,%d %y'):
                return render_template('particles/alert.html', msg="Try after a minute. Can't submit many comments at a time.", category="warning")
            if body.strip() == comment.body.strip():
                return render_template('particles/alert.html', msg="Duplicate Comment", category="warning")
        if(len(body))>300: return render_template('particles/alert.html', msg="Too long comment", category="warning")
        if(len(body))<3: return render_template('particles/alert.html', msg="Too short comment", category="warning")
        if comsno is not None:
            comment = Replies(body=body,comsno=comsno,usersno=current_user.sno)
        else:
            comment = Comments(body=body, post_id=post_id, usersno=user.sno)
        db.session.add(comment)
        db.session.commit()
        return render_template('particles/comment.html', comment=comment)
    else:
        to = request.args.get('to')
    if request.method == "GET":
        sno = request.args.get('sno')
        comments = Comments.query.filter_by(post_id=sno).all()
        return redirect('particles/comment.html', comments=comments)
    abort(404)



@app.route('/blog-writer/edit/<string:sno>', methods=["GET", "POST"])
@login_required
# codiga-disable
def handleBlogWriter(sno):
    if current_user.is_blocked: return abort(404)
    form = BlogWriter()
    post = Posts.query.filter_by(sno=sno).first()
    if (post == None or post.writer_id != current_user.sno) and sno != "0" and not current_user.is_admin:
        return redirect("/blog-writer/edit/0")

    if form.validate_on_submit():
        slug = string_to_slug(form.title.data)
        tag: str = form.tag.data
        tag = tag.strip().lower()
        draft = bool(form.draft.data)
        body = form.body.data
        body = body.replace('<scipt ', "XSS").replace('<script/>', "XSS")
        soup = BeautifulSoup(body, 'html.parser')
        summary = form.summary.data
        if not summary and soup.find('p'):
            summary = soup.find('p').text[:144]
        if sno == "0":
            post = Posts(title=form.title.data, summary=summary,
                         body=form.body.data, tag=tag, slug=slug, writer_id=current_user.sno, public = not draft)
            if not draft:
                urlshort = Urlshortner(point_to=f"/b/{current_user.username}/{slug}", pointer=generate_pointer(3))
                db.session.add(urlshort)
                db.session.commit()
            # If the user doesn't have any post then create blogprofile while saving first post
            if not current_user.posts or Blogprofile.query.filter_by(usersno=current_user.sno).first() is None:
                getUser = current_user
                blog_profile = Blogprofile(usersno=getUser.sno)
                db.session.add(blog_profile)
                db.session.commit()
            db.session.add(post)
            db.session.commit()
            if draft: return redirect(url_for('userDashboard'))
            flash("Successfully posted the blog! Thanks for posting.",
                  category="success")
            return redirect(f"/b/{current_user.username}/{slug}")
        else:
            post = Posts.query.get(int(sno))
            if current_user.sno == post.writer_id:
                post.title = form.title.data
                post.body = form.body.data
                post.tag = form.tag.data
                post.slug = slug
                db.session.commit()
                if draft:
                    return redirect(url_for('userDashboard'))
                else:
                    post.public = True
                    db.session.commit()
                if post.slug is not None: urlshort = Urlshortner.query.filter_by(point_to=f"/b/{current_user.username}/{post.slug}").first()
                if urlshort is not None: #*Update the short url location
                    urlshort.point_to = f"/b/{current_user.username}/{slug}" 
                    db.session.commit()
                else: #Generate a short URL
                    urlshort = Urlshortner(point_to=f"/b/{current_user.username}/{slug}",pointer=generate_pointer(3))
                    db.session.add(urlshort)
                    db.session.commit()
                flash(
                    f"Successfully apply the updates on '{post.title}' post", category="success")
                return redirect(f"{urlshort.point_to}")
            else:
                abort(404)
    flash_form_error_messages(form)
    return render_template("blogWriter.html",  post=post, sno=sno, form=form)


@app.route("/delete/<string:keyword>/<string:sno>")
@login_required
def handleDeletes(keyword, sno):
    if keyword == "b":
        post = Posts.query.filter_by(sno=sno).first()
        title = post.title
        if post.writer_id == current_user.sno or current_user.is_admin:
            for readinglist in post.reading_lists:
                readinglist.blogs.remove(post)
                db.session.commit()
            db.session.delete(post)
            db.session.commit()
            flash(f"Deleted post : {title}")
            return redirect(url_for("userDashboard"))
        return abort(404)

    elif keyword == "p":
        if current_user.is_admin:
            user = Users.query.filter_by(sno=sno).first()
            posts = Posts.query.filter_by(writer_id=user.sno).all()
            blogProfile = Blogprofile.query.filter_by(usersno=user.sno).first()
            readinglist = Readinglists.query.filter_by(
                usersno=user.sno).first()
            for blog in readinglist.blogs:
                blog.reading_lists.remove(readinglist)
                db.session.commit()
            if not posts:
                for post in posts:
                    db.session.delete(post)
                    db.session.commit()
            db.session.delete(user)
            if blogProfile:
                db.session.delete(blogProfile)
            if readinglist:
                db.session.delete(readinglist)
            db.session.commit()

            return redirect(url_for("adminDashboard"))
        else:
            return abort(404)

    elif keyword == "n":
        if current_user.is_admin:
            notice = Notices.query.filter_by(sno=sno).first()
            db.session.delete(notice)
            db.session.commit()
            return redirect(url_for("adminDashboard"))
        return abort(404)
    
    elif keyword == "r":
        if sno == "all":
            blogs = current_user.readinglist.blogs
            for blog in blogs:
                current_user.readinglist.blogs.remove(blog)
        else:
            post = Posts.query.filter_by(sno=sno).first()
            current_user.readinglist.blogs.remove(post)
        db.session.commit()
        if request.headers.get('HX-Request'):
            posts = current_user.readinglist.blogs
            return redirect('particles/bookmark.html', posts=posts)
        return redirect(url_for('readinglist'))
    else:
        return abort(404)


@app.route("/admin/dashboard")
@login_required
def adminDashboard():
    if current_user.is_admin:
        users = Users.query.all()
        posts = Posts.query.all()
        notices = Notices.query.all()
        form = NoticeForm()
        return render_template('adminPanel.html', posts=posts, users=users, notices=notices, form=form)
    else:
        abort(404)

@app.route('/admin/data/<string:ftype>')
def datagenerator(ftype):
    if not current_user.is_admin: abort(404)
    users = Users.query.order_by(Users.sno).all()
    data = []
    if ftype == "json":
        for user in users:
            profile = Blogprofile.query.filter_by(usersno=user.sno).first()
            if profile:
                followers:int = len(profile.followers)
            else: followers = 0
            data.append({'user':{
                'email':user.email,
                'username':user.username,
                'picture':user.picture,
                'joined_date':str(user.joined_date),
                'profile':{
                'following':len(user.following),
                'followers':followers
                },
                'posts':{
                    'count':len(user.posts.all())
                    },
                'info':{
                'userid':user.userid,
                'firstname': user.firstname,
                'lastname':user.lastname,
                'bio':user.bio,
                'age':user.age,
                'work':user.work,
                'country':user.country,
                'hobbies':user.hobbies,
                'brand_color':user.brand_color,
                },
                "status":{
                    'is_admin':user.is_admin,
                    'is_verified':user.is_verified,
                    'is_blocked':user.is_blocked
                }
            }})
        response = Response(
            json.dumps(data),
            mimetype='application/json',
            headers={'Content-disposition': 'attachment; filename=usersdata.json'})
        return response
    else:
        for user in users:
            profile = Blogprofile.query.filter_by(usersno=user.sno).first()
            if profile:
                followers:int = len(profile.followers)
            else: followers = 0
            data.append({
                'name':f"{user.firstname} {user.lastname}",
                'username':user.username,
                'email':user.email,
                'followers': str(followers),
                'posts': str(len(user.posts.all())),
                'joined_date': user.joined_date.strftime("%m/%d/%Y, %H:%M:%S")
            })
        fields = ['name','username','email','followers','posts',"joined_date"]
        csvfile = newcsv(data, fields, fields)
        response = Response(
        csvfile.getvalue(),
        mimetype='text/csv',
        headers={'Content-disposition': 'attachment; filename=data.csv'})
        return response
        
@app.route('/admin/data')
@login_required
def datacsv():
    if not current_user.is_admin: abort(404)
    

@app.route("/dashboard")
@login_required
def userDashboard():
    posts = current_user.posts.order_by(Posts.pub_date.desc()).all()
    blogProfile = Blogprofile.query.filter_by(usersno=current_user.sno).first()
    total_views = total_viewers(posts)
    return render_template("dashboard.html", user=current_user,  posts=posts, total_views=total_views, blogProfile=blogProfile)


@app.route("/search", methods=["GET"])
def search():
    type = request.args.get('t')
    q = request.args.get("q")
    users = False
    posts = []
    try:
        page = int(request.args.get("p"))
    except:
        page = 1
        
    #If it is a dynamic search page
    if q == "" and not request.headers.get('HX-Request'):
        return redirect('/search?t=dynamic&q=any')
    searchType = request.args.get("type")
    
    if q.startswith("@"):
        users = Users.query.filter(Users.username.startswith(q[1:])).paginate(page=page, per_page=8)
    else:
        
        if searchType == "tag":
            #If search for tags
            posts = Posts.query.msearch(q, fields=["tag"]).paginate(page=page, per_page=8)
        else:
            #Else Default serach in title and tag
            posts = Posts.query.msearch(
                q, fields=["title", "tag", "summary"]).paginate(page=page, per_page=8)
    if type is not None: return render_template('searchPage.html')
    # If a AJAX Request via HTMX
    if request.headers.get('HX-Request'):
        #IF search for user
        if users and q.startswith("@") and len(q)>1: return render_template("particles/profile_card.html", userList=users,page=page,url=f"search?q={q}&p=")
        #If search doesn't match
        if len(q)<=3 or len(posts.items)==0: return render_template('particles/searchnotfound.html') 
        return render_template('particles/blog.html', posts=posts,page=page,url=f"search?q={q}&p=",showend=False)
    
    return render_template("search.html",  posts=posts, q=q, searchType=searchType, url=request.url,userList=users)



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
        # socketio.emit('notice', {'title':notice.title, 'desc':notice.desc}, broadcast=True)
        return redirect(url_for("adminDashboard"))
    return abort(404)


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
    if not getUser:
        userid = generateId(15)
        firstname = user.get('given_name')
        lastname = user.get('family_name') or ""
        email = user.get('email')
        username = user.get('given_name')
        picture = user.get('picture')
        if email == params["admin_email"]:
            is_admin = True
        else:
            is_admin = False

        # If finds the username exists, it will generate username until it's unique
        user = Users.query.filter_by(username=username).first()
        while user:
            username = username+generator(2)
            user = Users.query.filter_by(username=username).first()
        newUser = Users(firstname=firstname, picture=picture, lastname=lastname, userid=userid,
                        email=email, username=string_to_slug(username), is_admin=is_admin, password_hash=generate_password_hash(generator(20)))
        db.session.add(newUser)
        db.session.commit()

        getUser = Users.query.filter_by(email=email).first()
        login_user(getUser)
        readinglist = Readinglists(user=getUser)
        db.session.add(readinglist)
        db.session.commit()
    else:
        blogprofile = Blogprofile.query.filter_by(usersno=getUser.sno).first()
        readinglist = Readinglists.query.filter_by(user=getUser).first()
        if not blogprofile:
            blogprofile = Blogprofile(usersno=getUser.sno)
            db.session.add(blogprofile)
            db.session.commit()
        if not readinglist:
            readinglist = Readinglists(user=getUser)
            db.session.add(readinglist)
            db.session.commit()
        login_user(getUser)
    # print(profile)
    # do something with the token and profile
    return redirect('/')


@app.route('/follow', methods=['GET', 'POST'])
def follow():
    import json
    if request.method == "GET":
        sno = request.args.get("sno")
        url = request.args.get('url')
        if not sno and not url:
            abort(404)
        user = current_user
        blogprofile = Blogprofile.query.filter_by(usersno=int(sno)).first()
        if blogprofile in user.following:
            user.following.remove(blogprofile)
            is_follow = False
        else:
            user.following.append(blogprofile)
            is_follow = True
        db.session.commit()
        if url:
            return redirect(url)
        return json.dumps({
            "status": 200,
            "success": True,
            "user": user.username,
            "followCount": len(blogprofile.followers),
            "is_follow": is_follow
        })
    abort(404)


@app.route('/followers/<string:username>')
def getFollowers(username):
    user = db.one_or_404(db.select(Users).filter_by(username=username))
    blogProfile = Blogprofile.query.filter_by(usersno=user.sno).first()
    followers = blogProfile.followers
    followers = followers[::-1]
    cnt = 0
    if not current_user.is_anonymous:
        cnt = current_user.following.count(blogProfile)
    return render_template('followers.html', user=user, followers=followers, blogProfile=blogProfile, cnt=cnt)


@app.route('/following-list/<string:username>')
def getFollowing(username):
    user = db.one_or_404(db.select(Users).filter_by(username=username))
    followings = user.following
    following_list = []
    for following in followings:
        userblog = Users.query.get(int(following.usersno))
        following_list.append(userblog)
    return render_template('following.html', user=user, following_list=following_list)


@app.route('/notifications', methods=['GET'])
@login_required
def notifications():
    following_list = []
    for following in current_user.following:
        following_list.append(following)
    posts = []
    for userBlog in following_list:
        user = Users.query.filter_by(sno=userBlog.usersno).first()
        if user is not None and len(user.posts.all())>0:
            posts.append(user.posts.first())
    comments_count = 0
    for post in current_user.posts:
        comments_count+=post.comments.count()
    # if request.headers.get('HX-Request'):
    #     ncount =comments_count + len(posts)
    #     session['notifications'] = str(comments_count + len(posts)) 
    #     return str(ncount)
            
    return render_template('notifications.html', posts=posts, comments_count=comments_count)


@app.route('/bookmark', methods=["GET"])
@login_required
def bookmark():
    if request.method == "GET":
        blogsno = request.args.get('blogsno')
        user = Users.query.get(int(current_user.sno))
        if not user.readinglist:
            readinglist = Readinglists(user=user)
            db.session.add(readinglist)
            db.session.commit()
        blog = Posts.query.get(int(blogsno))
        readinglist = user.readinglist.blogs
        if blog in readinglist:
            user.readinglist.blogs.remove(blog)
        else:
            user.readinglist.blogs.append(blog)
        db.session.commit()
        return json.dumps({
            "success": True,
            "blogsno": blogsno,
            "username": user.username,
            "bookmarkCount": len(current_user.readinglist.blogs)
        })
    return abort(404)


@app.route('/readinglist/u')
@login_required
def readinglist():
    posts = current_user.readinglist.blogs
    return render_template('readinglist.html', posts=posts)

@app.route('/l')
def shorturl():
    pointer = request.args.get('p')
    urlshort = Urlshortner.query.filter_by(pointer=pointer).first()
    if urlshort is None or not pointer: return abort(404)
    return redirect(urlshort.point_to)

@app.route('/export-data', methods=["GET"])
@login_required
def exportdata():
    format = request.args.get('format')
    posts = []
    user_posts = current_user.posts.all()
    from markdownify import markdownify
    for post in user_posts:
        posts.append({
            "title":post.title,
            "tags": post.tag,
            "summary":post.summary,
            "content":post.body,
            "contentMarkdown":markdownify(post.body),
            "public":post.public,
            "dateAdded":str(post.pub_date)
            
        })
    data = {
        "uid":current_user.userid,
        'email':current_user.email,
        "total_posts":len(posts),
        "posts":posts,
        }
    if format == "json":
        data = json.dumps(data)
        response = Response(
        data,
        mimetype='text/json',
        headers={'Content-disposition': 'attachment; filename=data.json'})
        return response
        
    elif format == 'csv':
        fields = ['title','tags','summary','content','content_markdown','public',"dateAdded"]
        csvfile = newcsv(data['posts'], fields, fields)
        response = Response(
        csvfile.getvalue(),
        mimetype='text/csv',
        headers={'Content-disposition': 'attachment; filename=data.csv'})
        return response
    elif format == "txt":
        txt = ''''''
        posts = current_user.posts.all()
        for post in posts:
            soup = BeautifulSoup(post.body, 'html.parser')
            txt += f'''
            -----------------------------------------------------------------------------------------
            |Title : {post.title}
            -----------------------------------------------------------------------------------------
            |Date : {post.pub_date.strftime("%m/%d/%Y, %H:%M:%S")}
            |Tags : {post.tag}
            |Summary : {post.summary}
            -----------------------------------------------------------------------------------------
            {soup.get_text()}
            ---X-----------------------------------X----------------------------------------X------
            ---X-----------------------------------X----------------------------------------X------
            
            '''
        response = Response(
        txt,
        mimetype='text/plain',
        headers={'Content-disposition': 'attachment; filename=posts.txt'})
        return response
    abort(404)
    
@app.route('/login')
def login():
    return redirect(url_for('googleLogin'))
    
@app.route('/import/post/markdown', methods=['POST'])
@login_required
def post_importer():
    from markdown import markdown
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            if allowed_file(filename, {'md'}):
                filestream = file.stream.read()
                data = markdown(filestream.decode('utf-8'))
                soup = BeautifulSoup(data, 'html.parser')
                headings = ('h1','h2','h3','h4')
                h = None
                for heading in headings:
                    if not soup.find(heading): continue
                    if not h or h == "":
                        h = soup.find(heading).text.strip()
                form = BlogWriter()
                return render_template('particles/postuploader.html', content=data, form=form,h=h)
            else:
                return render_template('particles/alert.html', msg="File type is not supported for markdown" ,category="danger")
                

@app.route('/download/b/<string:ftype>/<string:pid>')
@login_required
def download_blog(ftype,pid):
    from markdownify import markdownify
    try:post = Posts.query.filter_by(sno=int(pid)).first()
    except: abort(404)
    if not post.writer_id == current_user.sno: abort(404)
    if ftype == "markdown":
        try:
            md = markdownify(post.body)
        except: abort(500)
        if not post.writer.sno == current_user.sno: abort(404)
        response = Response(
            md,
            mimetype='text/plain',
            headers={'Content-disposition': 'attachment; filename=post.md'}
        )
        return response
    elif ftype == "txt":
        soup = BeautifulSoup(post.body, 'html.parser')
        txt = soup.get_text(strip=False)
        response = Response(
            txt,
            mimetype='text/plain',
            headers={'Content-disposition': 'attachment; filename=post.txt'}
        )
        return response
    elif ftype == "html":
        with app.app_context():
            try:
                body = post.body
                data = render_template('output.html', post=post, body=body)
                response = Response(
                    data,
                    mimetype='application/html',
                headers={'Content-disposition': f'attachment; filename={post.title}.html'})
                return response
            except:
                abort(500)

@app.route('/export/user/data/<string:ftype>')
@login_required
def user_data_export(ftype):
    user = current_user
    data = []
    if ftype == "json":
        profile = Blogprofile.query.filter_by(usersno=user.sno).first()
        if profile:
            followers:int = len(profile.followers)
        else: followers = 0
        data.append({'Data':{
            'email':user.email,
            'username':user.username,
            'picture':user.picture,
            'joined_date':str(user.joined_date),
            'profile':{
            'following':len(user.following),
            'followers':followers
            },
            'posts':{
                'count':len(user.posts.all())
                },
            'info':{
            'firstname': user.firstname,
            'lastname':user.lastname,
            'bio':user.bio,
            'age':user.age,
            'work':user.work,
            'country':user.country,
            'hobbies':user.hobbies,
            'brand_color':user.brand_color,
            },
            "status":{
                'is_verified':user.is_verified,
            }
        }})
        response = Response(
            json.dumps(data),
            mimetype='application/json',
            headers={'Content-disposition': 'attachment; filename=usersdata.json'})
        return response
    else:
        profile = Blogprofile.query.filter_by(usersno=user.sno).first()
        if profile:
            followers:int = len(profile.followers)
        else: followers = 0
        data.append({
            'name':f"{user.firstname} {user.lastname}",
            'username':user.username,
            'email':user.email,
            'followers': str(followers),
            'posts': str(len(user.posts.all())),
            'joined_date': user.joined_date.strftime("%m/%d/%Y, %H:%M:%S")
        })
        fields = ['name','username','email','followers','posts',"joined_date"]
        csvfile = newcsv(data, fields, fields)
        response = Response(
        csvfile.getvalue(),
        mimetype='text/csv',
        headers={'Content-disposition': f'attachment; filename={user.username}.csv'})
        return response

@app.route('/import', methods=['POST'])
@login_required
def importdata():
    from markdown import markdown
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            if allowed_file(filename,{'json','csv'}):
                try:
                    filestream = file.stream.read()
                    data = json.loads(filestream)
                    uid = data.get('uid')
                    user = Users.query.filter_by(userid=uid).first()
                    if not current_user.userid == user.userid or not current_user.email == user.email or not user or user is None: 
                        return render_template('particles/alert.html', msg="The file is not validated. We are unable to validate the file that it really belongs to you", category="danger")

                    posts = data['posts']
                    if len(posts) == 0: 
                        return render_template('particles/alert.html', msg="File containes no posts. Noting to upload.", category="warning")

                except:
                    return render_template('particles/alert.html', msg="<b>We are unable to retrieve posts from the file</b>.File is not in a right format or might be changed! try with another file", category="warning")
                titles = []
                user_posts = current_user.posts.all()
                for post in user_posts:
                    titles.append(post.title)
                err_posts = []
                #HERE will upload all posts
                try:
                    for post in posts:
                        title = post['title']
                        if title in titles:
                            err_posts.append(title)
                            continue
                        summary = post['summary']
                        body =  markdown(post['contentMarkdown'])
                        tag =  post['tags']
                        draft = not bool(post['public'])
                        slug = string_to_slug(title)
                        newpost = Posts(title=title, summary=summary,
                                body=body, tag=tag, slug=slug, writer_id=current_user.sno, public = not draft)
                        if not draft:
                            urlshort = Urlshortner(point_to=f"/b/{current_user.username}/{slug}", pointer=generate_pointer(3))
                            db.session.add(urlshort)
                            db.session.commit()
                        # If the user doesn't have any post then create blogprofile while saving first post
                        if not current_user.posts or Blogprofile.query.filter_by(usersno=current_user.sno).first() is None:
                            getUser = current_user
                            blog_profile = Blogprofile(usersno=getUser.sno)
                            db.session.add(blog_profile)
                            db.session.commit()
                        try:
                            db.session.add(newpost)
                            db.session.commit()
                        except:
                            err_posts.append(post['title'] or "Error")
                    if err_posts:
                        return render_template('particles/alert.html', msg=f"<b>There are {len(posts)} posts in the file</b>. But {len(err_posts)-len(posts)} posts are uploaded becuase of some error. (Looks like the posts must be duplicated or not in a right format)", category="danger") 
                    else:
                        return render_template('particles/alert.html', msg="Uploaded all files successfully!", category="success")
                except:
                    return render_template('particles/alert.html', msg="Some error occured! Posts object doesn't provide all of the data for uploading posts.", category="danger")
            else:
                return render_template('particles/alert.html', msg="File type not supported! supported files (.json)", category="danger")
        else:
            return render_template('particles/alert.html', msg="No file selected", category="danger")
        
@app.route('/comments/<string:username>')
def user_comments(username):
    user = Users.query.filter_by(username=username).first()
    if user is None: abort(404)
    return render_template('comments.html', user=user)

@app.route('/comment/<string:username>/<int:comsno>', methods=["GET"])
def user_comment(username,comsno):
    edit = request.args.get('edit')
    comment = Comments.query.filter_by(sno=comsno).first()
    return render_template('comment.html', comment=comment, edit=edit)
    
