# utils.py - general use functions

import os
import jinja2
import webapp2
import json
import re
import hmac
from google.appengine.ext import ndb

from models import Post, Comment

from webapp2_extras import sessions

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)

secret = "TEST_ENV"


def make_secure_val(val):
    return '%s|%s' % (val, hmac.new(secret, val).hexdigest())


def check_secure_val(secure_val):
    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val


class BlogHandler(webapp2.RequestHandler):
    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)

        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        # Returns a session using the default cookie key.
        return self.session_store.get_session()

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        params['user'] = self.user
        params['flashes'] = self.session.get_flashes()
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def render_json(self, d):
        json_txt = json.dumps(d)
        self.response.headers[
            'Content-Type'] = 'application/json; charset=UTF-8'
        self.write(json_txt)

    def set_secure_cookie(self, name, val):
        cookie_val = make_secure_val(val)
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; Path=/' % (name, cookie_val))

    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)

    def login(self, user):
        self.set_secure_cookie('user_id', user.key.urlsafe())

    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        urlsafe_key = self.read_secure_cookie('user_id')
        self.user = urlsafe_key and ndb.Key(urlsafe=urlsafe_key).get()

        if self.request.url.endswith('.json'):
            self.format = 'json'
        else:
            self.format = 'html'

    def get_by_urlsafe(self, urlsafe_key, model):
        """Returns a datastore entity by urlsafe key"""
        try:
            key = ndb.Key(urlsafe=urlsafe_key)
        except Exception:
            self.abort(404)

        entity = key.get()
        if not entity:
            self.abort(404)
        if not isinstance(entity, model):
            self.abort(404)
        return entity

    def check_login(self):
        if not self.user:
            self.redirect('/login', abort=True)

    def get_authed_entity(self, urlsafe_key, model, need_author=True):
        self.check_login()
        entity = self.get_by_urlsafe(urlsafe_key, model)
        if need_author \
           and (model == Post and entity.key.parent() == self.user.key or
                model == Comment and entity.author == self.user.username):
            return entity
        elif not need_author \
            and (model == Post and entity.key.parent() != self.user.key or
                 model == Comment and entity.author != self.user.username):
            return entity
        else:
            self.abort(403)


USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
    return username and USER_RE.match(username)

PASS_RE = re.compile(r"^.{3,20}$")
def valid_password(password):
    return password and PASS_RE.match(password)

EMAIL_RE = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
def valid_email(email):
    return not email or EMAIL_RE.match(email)
