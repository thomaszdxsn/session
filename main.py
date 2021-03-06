#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os

import redis
import pymongo

from tornado import web
from tornado import httpserver
from tornado import ioloop
from tornado import options
from tornado.options import define, options

from session import Session
from permission import permission_required

define('port', default=8000, type=int)


class Application(web.Application):
    def __init__(self):
        handlers = [
            (r'/', IndexHandler),
            (r'/logout', LogoutHandler),
            (r'/admin', AdminOnlyHandler),
            (r'/manager', ManagerHandler),
            (r'/user', UserHandler),
        ]
        settings = {
            'debug': True,
            'template_path': os.path.join(os.path.dirname(__file__), 'templates'),
            "cookie_secret": "sdafwerweqr1235",
            "session_expire": 60 * 60 * 24,
            'login_url': '/',
        }
        super(Application, self).__init__(handlers, **settings)
        self.db = pymongo.MongoClient()['auth']     # 取出mongoDB中的auth数据库
        self.redis = redis.StrictRedis()


class BaseHandler(web.RequestHandler):
    def prepare(self):
        """为每个链接建立一个session"""
        self.session = Session(self)
        print self.session._id, "prepare"
        super(BaseHandler, self).prepare()

    def get_current_user(self):
        session_id = self.get_secure_cookie("session_id", None)
        if not session_id:
            return
        username = self.application.redis.hget(session_id, 'username').decode()
        user = self.application.db.users.find_one({'username': username})
        return user

    def write_error(self, status_code, **kwargs):
        if status_code == 403:
            self.write("403: You don't have permission")


class IndexHandler(BaseHandler):
    def get(self):
        self.render("index.html")

    def post(self):
        if self.current_user is not None:
            # 如果已经登陆则跳转到首页
            self.redirect('/')
        username = self.get_argument("username")
        password = self.get_argument('password')
        result = self.application.db.users.find_one({"username": username,
                                                     "password": password})
        if result:
            self.session.username = result['username']
            next = self.get_argument('next', '/')
            self.redirect(next)


class LogoutHandler(BaseHandler):
    @web.authenticated
    def get(self):
        self.clear_cookie('session_id')
        self.redirect('/')


class AdminOnlyHandler(BaseHandler):
    @permission_required('admin')
    def get(self):
        self.write("hello, {}, this is admin page".format(self.current_user['username']))


class ManagerHandler(BaseHandler):
    @permission_required('manager')
    def get(self):
        self.write("hello, {}, this is manager page".format(self.current_user['username']))


class UserHandler(BaseHandler):
    @permission_required('user')
    def get(self):
        self.write("hello, {}, this is user page".format(self.current_user['username']))


if __name__ == '__main__':
    options.parse_command_line()
    http_server = httpserver.HTTPServer(Application())
    http_server.listen(8000)
    ioloop.IOLoop.current().start()


