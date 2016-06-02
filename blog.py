# blog.py - appengine blog application

#######################################
#
# TODO:
#   -flash messages
#   - REFACTOR auth checks (esp. checking authors) -- lots of repetition!!
#   - comments: likes
#
#######################################


import webapp2

from utils import (
    BlogHandler,
    valid_username,
    valid_password,
    valid_email,
    get_by_urlsafe
)

from google.appengine.ext import ndb
from models import Post, User, Comment

# TODO: implement global message for html pages (in header -- or main?)


class MainPage(BlogHandler):
    def get(self):
        # Move queries to utils or class func?
        posts = Post.query().order(-Post.created).fetch(10)
        self.render('blog.html', posts=posts)


class PostPage(BlogHandler):
    def get(self, post_urlsafe_key):
        try:
            post = get_by_urlsafe(post_urlsafe_key, Post)
            comments = Comment.query(ancestor=post.key).fetch()
            self.render('post.html', post=post, comments=comments)
        except Exception, e:
            print e
            self.redirect('/')


class EditPost(BlogHandler):
    def get(self, post_urlsafe_key):
        if not self.user:
            self.redirect('/login')
        else:
            try:
                post_to_edit = get_by_urlsafe(post_urlsafe_key, Post)
                if post_to_edit.key.parent() != self.user.key:
                    # TODO: add global msg to main.html
                    error = "You can only edit your own posts."
                    self.redirect('/')
                else:
                    self.render('editpost.html', post=post_to_edit)
            except Exception, e:
                print e
                self.redirect('/')

    def post(self, post_urlsafe_key):
        if not self.user:
            self.redirect('/login')
        else:
            try:
                post_to_edit = get_by_urlsafe(post_urlsafe_key, Post)
                if post_to_edit.key.parent() != self.user.key:
                    # TODO: add global msg to main.html
                    error = "You can only edit your own posts."
                    self.redirect('/')
                else:
                    post_to_edit.subject = self.request.get('subject')
                    post_to_edit.content = self.request.get('content')
                    post_to_edit.put()
                    self.redirect('/post/%s' % post_urlsafe_key)
            except Exception, e:
                print e
                self.redirect('/')


class DeletePost(BlogHandler):
    def get(self, post_urlsafe_key):
        # TODO helper func to check author
        if not self.user:
            self.redirect('/login')
        else:
            try:
                post_to_delete = get_by_urlsafe(post_urlsafe_key, Post)
                if post_to_delete.key.parent() != self.user.key:
                    # TODO: add global msg to main.html
                    error = "You can only delete your own posts."
                    self.redirect('/')
                else:
                    self.render('deleteitem.html', post=post_to_delete)
            except Exception, e:
                print e
                self.redirect('/')


    def post(self, post_urlsafe_key):
        if not self.user:
            self.redirect('/login')
        else:
            try:
                post_to_delete = get_by_urlsafe(post_urlsafe_key, Post)
                if post_to_delete.key.parent() != self.user.key:
                    # TODO: add global msg to main.html
                    error = "You can only delete your own posts."
                    self.redirect('/')
                else:
                    post_to_delete.key.delete()
                    # TODO: post still displays upon redirect
                    # - need to refresh page after redirect
                    self.redirect('/')
            except Exception, e:
                print e
                self.redirect('/')


class UserPosts(BlogHandler):
    def get(self, username):
        user = User.user_by_name(username)
        posts = Post.query(ancestor=user.key).order(-Post.created).fetch(10)
        self.render('blog.html', posts=posts)


class NewPost(BlogHandler):
    def get(self):
        if self.user:
            self.render('newpost.html')
        else:
            self.redirect('/login')

    def post(self):
        if not self.user:
            self.redirect('/login')
        else:
            subject = self.request.get('subject')
            content = self.request.get('content')

            if subject and content:
                post_id = ndb.Model.allocate_ids(size=1,
                                                 parent=self.user.key)[0]
                post_key = ndb.Key('Post', post_id, parent=self.user.key)
                p = Post(subject=subject, content=content, key=post_key)
                p.put()
                self.redirect("/post/%s" % p.key.urlsafe())


class TogglePostLike(BlogHandler):
    def post(self, post_urlsafe_key):
        if not self.user:
            self.redirect('/login')
        else:
            try:
                post_to_like = get_by_urlsafe(post_urlsafe_key, Post)
                if self.user.key == post_to_like.key.parent():
                    self.redirect('/post/%s' % post_to_like.key.urlsafe())
                elif post_to_like.key in self.user.liked_posts:
                    self.user.liked_posts.pop(
                        self.user.liked_posts.index(post_to_like.key))
                    post_to_like.likes -= 1
                else:
                    self.user.liked_posts.append(post_to_like.key)
                    post_to_like.likes += 1
                self.user.put()
                post_to_like.put()
                self.redirect('/post/%s' % post_to_like.key.urlsafe())
            except Exception, e:
                print e
                self.redirect('/')


class AddComment(BlogHandler):
    def post(self, post_urlsafe_key):
        if not self.user:
            self.redirect('/login')
        else:
            try:
                post_to_comment = get_by_urlsafe(post_urlsafe_key, Post)
                new_comment = self.request.get('comment')
                comment_id = ndb.Model.allocate_ids(
                    size=1,
                    parent=ndb.Key(urlsafe=post_urlsafe_key))[0]
                comment_key = ndb.Key(
                    'Comment',
                    comment_id,
                    parent=ndb.Key(urlsafe=post_urlsafe_key))
                Comment(
                    content=new_comment,
                    key=comment_key,
                    author=self.user.username).put()
                self.redirect('/post/%s' % post_urlsafe_key)
            except Exception, e:
                print e
                self.redirect('/')


class DeleteComment(BlogHandler):
    def get(self, comment_urlsafe_key):
        if not self.user:
            self.redirect('/login')
        else:
            try:
                comment_to_delete = get_by_urlsafe(
                    comment_urlsafe_key,
                    Comment)
                if comment_to_delete.author != self.user.username:
                    self.redirect('/')
                else:
                    self.render('deleteitem.html',
                                item="this comment",
                                comment=comment_to_delete.content)
            except Exception, e:
                print e
                self.redirect('/')

    def post(self, comment_urlsafe_key):
        if not self.user:
            self.redirect('/login')
        else:
            try:
                comment_to_delete = get_by_urlsafe(
                    comment_urlsafe_key,
                    Comment)
                if comment_to_delete.author != self.user.username:
                    self.redirect('/')
                else:
                    comment_to_delete.key.delete()
                    self.redirect('/')
            except Exception, e:
                print e
                self.redirect('/')


class EditComment(BlogHandler):
    def get(self, comment_urlsafe_key):
        if not self.user:
            self.redirect('/login')
        else:
            try:
                comment_to_edit = get_by_urlsafe(
                    comment_urlsafe_key,
                    Comment)
                if comment_to_edit.author != self.user.username:
                    self.redirect('/')
                else:
                    self.render('editcomment.html',
                                comment=comment_to_edit)
            except Exception, e:
                print e
                self.redirect('/')

    def post(self, comment_urlsafe_key):
        if not self.user:
            self.redirect('/login')
        else:
            try:
                comment_to_edit = get_by_urlsafe(
                    comment_urlsafe_key,
                    Comment)
                if comment_to_edit.author != self.user.username:
                    self.redirect('/')
                else:
                    comment_to_edit.content = self.request.get('comment')
                    comment_to_edit.put()
                    self.redirect('/')
            except Exception, e:
                print e
                self.redirect('/')


class ToggleCommentLike(BlogHandler):
    def post(self, comment_urlsafe_key):
        if not self.user:
            self.redirect('/login')
        else:
            try:
                comment_to_like = get_by_urlsafe(comment_urlsafe_key, Comment)
                if self.user.username == comment_to_like.author:
                    self.redirect('/post/%s' % comment_to_like.key.parent().urlsafe())
                elif comment_to_like.key in self.user.liked_comments:
                    self.user.liked_comments.pop(
                        self.user.liked_comments.index(comment_to_like.key))
                    comment_to_like.likes -= 1
                else:
                    self.user.liked_comments.append(comment_to_like.key)
                    comment_to_like.likes += 1
                self.user.put()
                comment_to_like.put()
                self.redirect('/post/%s' % comment_to_like.key.parent().urlsafe())
            except Exception, e:
                print e
                self.redirect('/')


class Register(BlogHandler):
    def get(self):
        if not self.user:
            self.render('registration.html')
        else:
            # TODO: add msg "You are already logged in"
            self.redirect('/')

    def post(self):
        if self.user:
            # TODO: add msg "You are already logged in"
            self.redirect('/')
        else:
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
        if not self.user:
            self.render('login.html')
        else:
            # TODO: redirect w msg "You are already logged in"
            self.redirect('/')

    def post(self):
        if self.user:
            self.redirect('/')
        else:
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
                               ('/post/([a-zA-Z0-9-_]+)(?:.json)?', PostPage),
                               ('/user/([a-zA-Z0-9-_]+)(?:.json)?', UserPosts),
                               ('/edit/([a-zA-Z0-9-_]+)/?', EditPost),
                               ('/delete/([a-zA-Z0-9-_]+)/?', DeletePost),
                               ('/post/([a-zA-Z0-9-_]+)/like/?', TogglePostLike),
                               ('/comment/([a-zA-Z0-9-_]+)/?', AddComment),
                               ('/comment/([a-zA-Z0-9-_]+)/delete/?', DeleteComment),
                               ('/comment/([a-zA-Z0-9-_]+)/edit/?', EditComment),
                               ('/comment/([a-zA-Z0-9-_]+)/like/?', ToggleCommentLike),
                               ],
                              debug=True)
