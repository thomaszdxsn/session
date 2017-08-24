#!/usr/bin/env python3
from functools import wraps

from tornado.httpclient import HTTPError


class permission_required(object):

    def __init__(self, permission):
        self.permission = permission

    def __call__(self, f):
        f.permission = self.permission
        @wraps(f)
        def _wrapped(self, *args, **kwargs):
            if not self.current_user or self.current_user['role'] != f.permission:
                self.set_status(403)
                self.write_error(403)
            else:
                f(self, *args, **kwargs)
        return _wrapped


