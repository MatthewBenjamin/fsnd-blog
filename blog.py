# blog.py - appengine blog application
import webapp2

from utils import (
    BlogHandler,
    valid_username,
    valid_password,
    valid_email,
)

from google.appengine.ext import ndb
from models import Post, User, Comment


class MainPage(BlogHandler):
    def get(self):
        posts = Post.query().order(-Post.created).fetch(10)

        if self.format == 'html':
            self.render('blog.html', posts=posts)
        else:
            self.render_json(d=[post.serialize for post in posts])


class PostPage(BlogHandler):
    def get(self, post_urlsafe_key):
        post = self.get_by_urlsafe(post_urlsafe_key, Post)
        comments = Comment.query(ancestor=post.key).fetch()
        if self.format == 'html':
            self.render('post.html', post=post, comments=comments)
        else:
            self.render_json(d=post.serialize)


class EditPost(BlogHandler):
    def get(self, post_urlsafe_key):
        post_to_edit = self.get_authed_entity(post_urlsafe_key, Post)
        self.render('editpost.html', post=post_to_edit)

    def post(self, post_urlsafe_key):
        post_to_edit = self.get_authed_entity(post_urlsafe_key, Post)
        post_to_edit.subject = self.request.get('subject')
        post_to_edit.content = self.request.get('content')
        post_to_edit.put()
        self.redirect('/post/%s' % post_urlsafe_key)


class DeletePost(BlogHandler):
    def get(self, post_urlsafe_key):
        post_to_delete = self.get_authed_entity(post_urlsafe_key, Post)
        self.render('deleteitem.html', item=post_to_delete.subject)

    def post(self, post_urlsafe_key):
        post_to_delete = self.get_authed_entity(post_urlsafe_key, Post)
        post_to_delete.key.delete()
        # TODO: post still displays upon redirect
        # - need to refresh page after redirect
        self.session.add_flash("Post deleted")
        self.redirect('/')


class UserPosts(BlogHandler):
    def get(self, username):
        user = User.user_by_name(username)
        posts = Post.query(ancestor=user.key).order(-Post.created).fetch(10)
        if self.format == 'html':
            self.render('blog.html', posts=posts)
        else:
            self.render_json(d=[post.serialize for post in posts])


class NewPost(BlogHandler):
    def get(self):
        self.check_login()
        self.render('newpost.html')

    def post(self):
        self.check_login()

        subject = self.request.get('subject')
        content = self.request.get('content')

        if subject and content:
            post_id = ndb.Model.allocate_ids(size=1,
                                             parent=self.user.key)[0]
            post_key = ndb.Key('Post', post_id, parent=self.user.key)
            p = Post(subject=subject, content=content, key=post_key)
            p.put()
            self.session.add_flash("New post created")
            self.redirect("/post/%s" % p.key.urlsafe())


class TogglePostLike(BlogHandler):
    def post(self, post_urlsafe_key):
        post_to_like = self.get_authed_entity(
            post_urlsafe_key, Post, need_author=False)
        if post_to_like.key in self.user.liked_posts:
            self.user.liked_posts.pop(
                self.user.liked_posts.index(post_to_like.key))
            post_to_like.likes -= 1
        else:
            self.user.liked_posts.append(post_to_like.key)
            post_to_like.likes += 1
        self.user.put()
        post_to_like.put()
        self.redirect('/post/%s' % post_to_like.key.urlsafe())


class AddComment(BlogHandler):
    def post(self, post_urlsafe_key):
        self.check_login()
        post_to_comment = self.get_by_urlsafe(post_urlsafe_key, Post)
        new_comment = self.request.get('comment')
        comment_id = ndb.Model.allocate_ids(
            size=1,
            parent=post_to_comment.key)[0]
        comment_key = ndb.Key(
            'Comment',
            comment_id,
            parent=post_to_comment.key)
        Comment(
            content=new_comment,
            key=comment_key,
            author=self.user.username).put()
        self.redirect('/post/%s' % post_urlsafe_key)


class DeleteComment(BlogHandler):
    def get(self, comment_urlsafe_key):
        comment_to_delete = self.get_authed_entity(
            comment_urlsafe_key,
            Comment)
        self.render('deleteitem.html',
                    item="this comment",
                    comment=comment_to_delete.content)

    def post(self, comment_urlsafe_key):
        comment_to_delete = self.get_authed_entity(
            comment_urlsafe_key,
            Comment)
        comment_to_delete.key.delete()
        self.session.add_flash("Comment deleted")
        self.redirect('/post/%s' % comment_to_delete.key.parent().urlsafe())


class EditComment(BlogHandler):
    def get(self, comment_urlsafe_key):
        comment_to_edit = self.get_authed_entity(
            comment_urlsafe_key,
            Comment)
        self.render('editcomment.html',
                    comment=comment_to_edit)

    def post(self, comment_urlsafe_key):
        comment_to_edit = self.get_authed_entity(
            comment_urlsafe_key, Comment)
        comment_to_edit.content = self.request.get('comment')
        comment_to_edit.put()
        self.redirect('/post/%s' % comment_to_edit.key.parent().urlsafe())


class ToggleCommentLike(BlogHandler):
    def post(self, comment_urlsafe_key):
        comment_to_like = self.get_authed_entity(
            comment_urlsafe_key, Comment, need_author=False)
        if comment_to_like.key in self.user.liked_comments:
            self.user.liked_comments.pop(
                self.user.liked_comments.index(comment_to_like.key))
            comment_to_like.likes -= 1
        else:
            self.user.liked_comments.append(comment_to_like.key)
            comment_to_like.likes += 1
        self.user.put()
        comment_to_like.put()
        self.redirect('/post/%s' % comment_to_like.key.parent().urlsafe())


class Register(BlogHandler):
    def get(self):
        if self.user:
            self.session.add_flash("You are already logged in")
            self.redirect('/')
        else:
            self.render('registration.html')

    def post(self):
        if self.user:
            self.session.add_flash("You are already logged in")
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
                self.session.add_flash("Welcome, %s!" % user.username)
                self.redirect('/')


class Login(BlogHandler):
    def get(self):
        if self.user:
            self.session.add_flash("You are already logged in")
            self.redirect('/')
        else:
            self.render('login.html')

    def post(self):
        if self.user:
            self.session.add_flash("You are already logged in")
            self.redirect('/')
        else:
            username = self.request.get('username')
            password = self.request.get('password')

            user = User.login(username, password)
            if user:
                self.login(user)
                self.session.add_flash("Welcome, %s" % user.username)
                self.redirect('/')
            else:
                login_error = 'Invalid login'
                self.render('login.html', login_error=login_error)


class Logout(BlogHandler):
    def get(self):
        self.logout()
        self.session.add_flash("You have successfully logged out")
        self.redirect('/')

config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': 'some-secret-key',
}

app = webapp2.WSGIApplication(
    [
        ('/', MainPage),
        ('/?(?:.json)?', MainPage),
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
    debug=True, config=config)
