#!/usr/bin/env python3
# -*- coding:utf-8 -*
from functools import wraps

from tornado import web


class Permission(object):
    view = 0x01
    add = 0x02
    modify = 0x04
    delete = 0x08

    user = view
    manager = view | add | modify | delete
    admin = 0xff


class permission_required(object):
    """一个方法装饰器，作用于RequestHandler的HTTP方法上面
    这是一个必须接受参数的装饰器，在调用它的时候需要传入一个权限字符串
    """
    def __init__(self, permission):
        self.permission = getattr(Permission, permission)

    def __call__(self, f):
        f.permission = self.permission
        @wraps(f)
        @web.authenticated
        def _wrapped(self, *args, **kwargs):
            if self.current_user['role'] < f.permission:
                self.set_status(403)
                self.write_error(403)
            else:
                f(self, *args, **kwargs)
        return _wrapped


