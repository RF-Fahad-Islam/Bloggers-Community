import random
from flask import flash
from .models import Users, Posts, Urlshortner
# URL Encoder
from urllib.parse import quote

# Create a slug from a string
def string_to_slug(string):
    string = string.strip().lower()
    string = string.replace("  ", " ") #Replace double spaces by single space
    string = string.replace(" ", "-")
    return quote(string)

def generateId(length):
    """Generate a unique ID for each user id

    Args:
        length (integer): Length of the id

    Returns:
        string: a unique id
    """
    id_=""
    charset = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz@#$&"
    for i in range(length):
        r = random.randint(0, length-1)
        id_+= charset[r]
    users = Users.query.all()
    usedIds = []
    for user in users:
        usedIds.append(user.userid)
    while id_ in usedIds:
        for i in range(length):
            r = random.randint(0, length)
            id_+= charset[r]
    return id_

def generate_pointer(length:int):
    """Generate a unique ID for each url

    Args:
        length (integer): Length of the id

    Returns:
        string: a unique id
    """
    id_:str=""
    charset:str = "ABCop-qDEF-MR-STUVmnrWXYZab-cde-GHlsIJ-KLfN-OPQg-hijktuvwxyz&-"
    for i in range(length):
        r = random.randint(0, length-1)
        id_+= charset[r]
    urlshorts = Urlshortner.query.all()
    usedpointers = []
    for urlshort in urlshorts:
        usedpointers.append(urlshort.pointer)
    while id_ in usedpointers:
        for i in range(length):
            r = random.randint(0, length)
            id_+= charset[r]
    return id_

def flash_form_error_messages(form):
    if form.errors != {}:
        for field, err_msg in form.errors.items():
            flash(f"{form[field].label()} : {','.join(err_msg)}", category="danger")
            
def all_tags():
    posts = Posts.query.all()
    tags_list = []
    tagsObj = {}
    for post in posts:
        tags = post.tag.split(' ') #Converted to list
        for tag in tags:
            if tag != "": tags_list.append(tag)
            
    tags_set = set(tags_list)
    for tag in tags_set:
        counted = tags_list.count(tag)
        tagsObj[tag] = counted
        
    tagsObj = dict(sorted(tagsObj.items(), key=lambda item: item[1], reverse=True))
    return tagsObj

def total_viewers(posts):
    total_viewers = 0
    if posts:
        for post in posts:
            total_viewers += post.viewers_count
            
    if total_viewers >= 1000000:
        total_viewers = "%.0f%s" % (total_viewers/1000000.00, 'M')
    elif total_viewers >= 1000:
        total_viewers = "%.0f%s" % (total_viewers/1000.0, 'k')
    return total_viewers
