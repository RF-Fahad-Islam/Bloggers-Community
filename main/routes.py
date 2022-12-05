import json
from . import db, app, login_manager, search, oauth,htmx,mail
from flask import render_template, redirect, session, request, jsonify, url_for, flash, abort, send_from_directory
from .models import Users, Posts, Notices, Comment,Blogprofile, Readinglists, Urlshortner             
from .forms import RegisterForm, LoginForm, BlogWriter, SettingForm, NoticeForm, CommentForm
from .utilities import *
from flask_login import login_required, login_user, logout_user, current_user
import random
from datetime import datetime
params = {
    "page_title": "Blogsphere | Made By Fahad",
    "app_name": "Blogsphere",
    "url": "https://blogsphere.onrender.com",
    "github": "https://github.com/RF-Fahad-Islam/",
    "admin_email": "riyad9949@gmail.com",
    "admin_password": "$$01308388895$$@Rf",
    "admin_userid": "I_AM_THE_CREATOR_OF_THIS_WEBSITE_FAHAD"
}


# with app.app_context():
#     users = Users.query.all()
#     for user in users:
#         blogprofile = Blogprofile.query.filter_by(usersno=user.sno).first()
#         readinglist = Readinglists.query.filter_by(user=user).first()
#         if not blogprofile:
#             blogprofile = Blogprofile(usersno=user.sno)
#             db.session.add(blogprofile)
#             db.session.commit()
#         if not readinglist:
#             readinglist = Readinglists(user=user)
#             db.session.add(readinglist)
#             db.session.commit()

@app.route('/sitemap.xml')
def static_from_root():
    return send_from_directory(app.static_folder, 'sitemap.xml')

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
    random.shuffle(posts)
    return render_template('index.html', notices=notices,  posts=posts)

@app.route('/draft', methods=['POST'])
def draftpost():
    if request.method == "POST":
        title = request.form.get('title')
        content = request.form.get('content')
        if len(title)<3 or len(title)>100 or len(content)>500 or "<script" in content: 
            flash("(XSS Protection) : Detected scripting code!", category="danger")
            return redirect('/')
        post = Posts(title=title, body=content, public=False,writer_id=current_user.sno, slug=string_to_slug(title))
        db.session.add(post)
        db.session.commit()
        flash(f'Successfully Saved the Draft : {title}')
        return redirect(url_for('userDashboard'))

# Handle Other Urls


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    abort(404)

@app.route('/get-blogs', methods=["GET"])
def blogs():
    page =1
    try:
        page = int(request.args.get('p'))
    except:
        pass
    posts = Posts.query.paginate(page=page,per_page=2)
    return render_template('particles/blog.html', posts=posts, page=page, url="get-blogs", showend=True)



@app.route("/tags")
def handleTags():
    tags = all_tags()
    return render_template('tags.html', tags=tags)


@app.route("/p/<string:username>")
def userProfile(username):
    user = db.one_or_404(db.select(Users).filter_by(username=username))
    posts = user.posts.filter_by(public=True).order_by(Posts.pub_date.desc()).all()
    blogProfile = Blogprofile.query.filter_by(usersno=user.sno).first()
    if not current_user.is_anonymous:
        cnt = current_user.following.count(blogProfile)
    else:
        cnt = 0
    total_viewers_count = total_viewers(posts)
    return render_template("profile.html",  user=user, posts=posts, blogProfile=blogProfile, total_viewers=total_viewers_count, cnt=cnt)

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


atm = 0


@app.route('/login', methods=['GET', 'POST'])
def login():
    global atm
    form = LoginForm()
    if atm > 3:
        return redirect('/')
    if form.validate_on_submit() and atm > 3:
        user = Users.query.filter_by(email=form.email.data).first()
        if user != None and user.check_password(form.password.data):
            atm = 0
            login_user(user)
            return redirect(url_for("home"))
        else:
            atm += 1
            flash_form_error_messages(form)
            if atm > 3:
                return redirect('/')

    flash_form_error_messages(form)
    return render_template("login.html", form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect("/")


@app.route('/settings', methods=["GET", "POST"])
def settingProfile():
    form = SettingForm()
    blogProfile = Blogprofile.query.filter_by(usersno=current_user.sno).first()
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
    comments = Comment.query.filter_by(to=f"/b/{user.sno}/{post.sno}").all()
    form = CommentForm()
    if form.validate_on_submit():
        body = form.body.data
        to = form.to.data
        url = form.url.data
        comment = Comment(body=body, to=to, usersno=current_user.sno)
        db.session.add(comment)
        db.session.commit()
        return redirect(url+"#comment")

    if post is None:
        return abort(404)
    try:
        if current_user.sno == user.sno:
            pass
    except:
        post.viewers_count += 1
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
                                       "tag"]).order_by(Posts.viewers_count.desc())[:5]
    if not recommendeds and len(post.tags_list) > 1:
        recommendeds = Posts.query.filter_by(public=True).msearch(post.tags_list[1], fields=[
                                           "tag"]).order_by(Posts.viewers_count.desc())[:5]
    if not recommendeds:
        recommendeds = posts[:3]
    recommendeds.remove(post)
    blogProfile = Blogprofile.query.filter_by(usersno=user.sno).first()
    urlshort = Urlshortner.query.filter_by(point_to=f"/b/{user.username}/{post.slug}").first()
    if urlshort is None or not urlshort:
        urlshort = Urlshortner(point_to=f"/b/{user.username}/{post.slug}", pointer=generate_pointer(4))
        db.session.add(urlshort)
        db.session.commit()
    shorturl = f'{params["url"]}/l?p={urlshort.pointer}'
    return render_template("blog.html",  post=post, user=user, next_post=next_post, prev_post=prev_post, recommendeds=recommendeds,comments=comments, blogProfile=blogProfile, shorturl=shorturl, form=form)

@app.route('/comment', methods=["POST","GET"])
@login_required
def comment():
    if request.method == "POST":
        form = request.form
        body = form.get("body")
        to = form.get("to")
        uid = form.get('uid')
        user = Users.query.filter_by(userid=uid).first()
        if(len(body))>300: return "Too Long comment"
        comment = Comment(body=body, to=to, usersno=user.sno)
        db.session.add(comment)
        db.session.commit()
        comments = Comment.query.filter_by(to=to).all()
        return render_template('particles/comment.html', comments=comments)
    abort(404)


@app.route('/blog-writer/edit/<string:sno>', methods=["GET", "POST"])
@login_required
# codiga-disable
def handleBlogWriter(sno):
    if current_user.is_blocked:
        return abort(404)
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
        if sno == "0":
            post = Posts(title=form.title.data, summary=form.summary.data,
                         body=form.body.data, tag=tag, slug=slug, writer_id=current_user.sno, public = not draft )
            if not draft:
                urlshort = Urlshortner(point_to=f"/{current_user.username}/{slug}", pointer=generate_pointer(3))
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
            post = Posts.query.filter_by(sno=sno).first()
            prev_slug = post.slug
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
                urlshort = Urlshortner.query.filter_by(point_to=f"/b/{current_user.username}/{prev_slug}").first()
                if urlshort is not None:
                    urlshort.point_to = f"/b/{current_user.username}/{slug}" 
                    db.session.commit()
                else:
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
        if post.writer_id == current_user.sno or current_user.is_admin:
            for readinglist in post.reading_lists:
                readinglist.blogs.remove(post)
                db.session.commit()
            db.session.delete(post)
            db.session.commit()
            return redirect(url_for("userDashboard"))

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
            return redirect("/")

    elif keyword == "n":
        if current_user.is_admin:
            notice = Notices.query.filter_by(sno=sno).first()
            db.session.delete(notice)
            db.session.commit()
            return redirect(url_for("adminDashboard"))
    elif keyword == "r":
        if sno == "all":
            blogs = current_user.readinglist.blogs
            for blog in blogs:
                current_user.readinglist.blogs.remove(blog)
        else:
            post = Posts.query.filter_by(sno=sno).first()
            current_user.readinglist.blogs.remove(post)
        db.session.commit()
        return redirect(url_for('readinglist'))
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
        return render_template('adminPanel.html', posts=posts, users=users, notices=notices, form=form)
    else:
        abort(404)


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
    try:
        page = int(request.args.get("p"))
    except:
        page = 1
        
    #If it is a dynamic search page
    if q == "" and not htmx:
        return redirect('/search?t=dynamic&q=any')
    searchType = request.args.get("type")
    
    if searchType == "tag":
        #If search for tags
        posts = Posts.query.msearch(
            q, fields=["tag"]).paginate(page=page, per_page=8)
    else:
        #Else Default serach in title and tag
        posts = Posts.query.msearch(
            q, fields=["title", "tag"]).paginate(page=page, per_page=8)
        
    if type is not None:
        tags= all_tags()
        return render_template('searchPage.html', tags=tags)
    
    # If a AJAX Request via HTMX
    if htmx:
        if len(q)<=3 or len(posts.items)==0: return render_template('particles/searchnotfound.html') 
        return render_template('particles/blog.html', posts=posts,page=page,url="search",showend=False)
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
    if not getUser:
        userid = generateId(30)
        firstname = user.get('given_name')
        lastname = user.get('family_name')
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
            username = username+generateId(2)
            user = Users.query.filter_by(username=username).first()
        newUser = Users(firstname=firstname, picture=picture, lastname=lastname, userid=userid,
                        email=email, username=string_to_slug(username), is_admin=is_admin, password=generateId(20))
        db.session.add(newUser)
        db.session.commit()

        getUser = Users.query.filter_by(email=email).first()
        login_user(getUser)
        readinglist = Readinglists(user=getUser)
        db.session.add(readinglist)
        db.session.commit()
    else:
        getUser.picture = user.get('picture')
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
        user_sno = request.args.get('user_sno')
        if not sno and not url:
            abort(404)
        if not user_sno:
            user_sno = current_user.sno
        user = db.one_or_404(db.select(Users).filter_by(sno=current_user.sno))
        blogprofile = db.one_or_404(
            db.select(Blogprofile).filter_by(usersno=int(sno)))
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
    followingList = []
    for following in followings:
        userblog = Users.query.get(int(following.usersno))
        followingList.append(userblog)
    return render_template('following.html', user=user, followingList=followingList)


@app.route('/notifications')
@login_required
def notifications():
    followingList = []
    for following in current_user.following:
        followingList.append(following)
    posts = []
    for userBlog in followingList:
        posts.append(Posts.query.filter_by(
            writer_id=userBlog.usersno).order_by(Posts.pub_date.desc()).first())
    return render_template('notifications.html', posts=posts)


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