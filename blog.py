# blog.py - appengine blog application
import webapp2
from utils import BlogHandler

from google.appengine.ext import ndb
from models import Post


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
        self.write("Display new user registration form")


class Login(BlogHandler):
    def get(self):
        self.login()
        self.write("You are logged in!")


class Logout(BlogHandler):
    def get(self):
        self.logout()
        self.write("You are logged out!")

app = webapp2.WSGIApplication([('/', MainPage),  # what to put on MainPage?
#                              ('/?(?:.json)?', BlogFront),  TODO: is this needed? what about JSON?
                               ('/newpost/?', NewPost),
                               ('/signup/?', Register),
                               ('/login/?', Login),
                               ('/logout/?', Logout),
                               ('/([a-zA-Z0-9-_]+)(?:.json)?', PostPage),
                               ],
                              debug=True)
