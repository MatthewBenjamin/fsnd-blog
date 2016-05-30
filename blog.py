# blog.py - appengine blog application
import webapp2
from utils import (
    BlogHandler,
    valid_username,
    valid_password,
    valid_email,
    make_secure_val
)

from google.appengine.ext import ndb
from models import Post, User


class MainPage(BlogHandler):
    def get(self):
        # Move queries to utils or class func?
        posts = Post.query().order(-Post.created).fetch(10)
        self.render('blog.html', posts=posts)


class PostPage(BlogHandler):
    def get(self, post_urlsafe_key):
        # TODO: add getbyurlsafe util
        post = ndb.Key(urlsafe=post_urlsafe_key).get()
        #print post
        self.render('post.html', post=post)


class NewPost(BlogHandler):
    def get(self):
        self.render('newpost.html')

    def post(self):
        subject = self.request.get('subject')
        content = self.request.get('content')

        if subject and content:
            p = Post(subject=subject, content=content)
            p.put()
            self.redirect("/%s" % p.key.urlsafe())


class Register(BlogHandler):
    def get(self):
        self.render('registration.html')

    def post(self):
        self.username = self.request.get('username')
        self.password = self.request.get('password')
        self.confirm = self.request.get('confirm')
        self.email = self.request.get('email')

        params = dict(username=self.username,
                      email=self.email)
        have_error = False
        if not valid_username(self.username):
            params['error_username'] = 'Invalid username'
            have_error = True
        elif User.user_by_name(self.username):
            params['error_username'] = 'User with that name already exists'
            have_error = True
        if not valid_password(self.password):
            params['error_password'] = 'Invalid password'
            have_error = True
        elif self.password != self.confirm:
            params['error_confirm'] = 'Passwords do not match'
            have_error = True
        if not valid_email(self.email):
            params['error_email'] = 'Invalid email'
            have_error = True

        if have_error:
            self.render('registration.html', **params)
        else:
            user = User.register_user(username=self.username,
                                      password=self.password,
                                      email=self.email)
            user.put()
            self.login(user)
            self.redirect('/')


class Login(BlogHandler):
    def get(self):
        self.render('login.html')

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')

        user = User.login(username, password)
        if user:
            self.login(user)
            self.redirect('/')
        else:
            login_error = 'Invalid login'
            self.render('login.html', login_error=login_error)


class Logout(BlogHandler):
    def get(self):
        self.logout()
        self.redirect('/')

app = webapp2.WSGIApplication([('/', MainPage),  # what to put on MainPage?
#                              ('/?(?:.json)?', BlogFront),  TODO: is this needed? what about JSON?
                               ('/newpost/?', NewPost),
                               ('/signup/?', Register),
                               ('/login/?', Login),
                               ('/logout/?', Logout),
                               ('/([a-zA-Z0-9-_]+)(?:.json)?', PostPage),
                               ],
                              debug=True)
