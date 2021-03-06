# models.py - appengine datastore models

from google.appengine.ext import ndb
from string import letters
import hashlib
import random


def make_salt(length=5):
    return ''.join(random.choice(letters) for x in xrange(length))


def make_pw_hash(name, pw, salt=None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s,%s' % (salt, h)


def valid_pw(name, password, h):
    salt = h.split(',')[0]
    return h == make_pw_hash(name, password, salt)


class User(ndb.Model):
    username = ndb.StringProperty(required=True)
    pw_hash = ndb.StringProperty(required=True)
    email = ndb.StringProperty()
    liked_posts = ndb.KeyProperty(repeated=True)
    liked_comments = ndb.KeyProperty(repeated=True)

    @classmethod
    def register_user(cls, username, password, email):
        pw_hash = make_pw_hash(username, password)
        return User(username=username,
                    pw_hash=pw_hash,
                    email=email)

    @classmethod
    def user_by_name(cls, name):
        user = User.query(User.username == name).get()
        return user

    @classmethod
    def login(cls, name, password):
        user = cls.user_by_name(name)
        if user and valid_pw(name, password, user.pw_hash):
            return user


class Post(ndb.Model):
    """Blog post"""
    subject = ndb.StringProperty(required=True)
    content = ndb.TextProperty(required=True)
    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)
    likes = ndb.IntegerProperty(default=0, required=True)
    # TODO: tags = repeated string property

    @property
    def serialize(self):
        """Return object data in an easily serializable format."""
        return {
            'subject': self.subject,
            'content': self.content,
            'created:': str(self.created),
            'modified': str(self.modified),
            'likes': self.likes
        }


class Comment(ndb.Model):
    content = ndb.TextProperty(required=True)
    author = ndb.StringProperty(required=True)
    likes = ndb.IntegerProperty(default=0)
