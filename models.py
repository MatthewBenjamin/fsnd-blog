# models.py - appengine datastore models

from google.appengine.ext import ndb


class User(ndb.Model):
    username = ndb.StringProperty(required=True)
#    pw_hash
#    email
#    post_likes = repeated key property
#    comment_likes = repeated key property
# models to add:
# - blog post
# - user
# - comment


class Post(ndb.Model):
    """Blog post"""
    subject = ndb.StringProperty(required=True)
    content = ndb.TextProperty(required=True)
    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)
    likes = ndb.IntegerProperty(default=0, required=True)
#    tags = repeated string property

# class User(ndb.Model):
#    username
#    pw_hash
#    email
#    post_likes = repeated key property
#    comment_likes = repeated key property

# class Comment(ndb.Model):
#    child of Post
#    user key = KeyProperty
#    content = Text property ?
#    likes = integer property, default=0
