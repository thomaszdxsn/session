#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import time
import hashlib


class Session(object):
    _prefix = '_session:'
    _id = None
    _skip = ['_redis', '_handler', '_id']

    def __init__(self, handler_instance):
        self._redis = handler_instance.application.redis
        self._handler = handler_instance
        _id = handler_instance.get_secure_cookie("session_id")
        if _id and self._redis.exists(_id):
            self._id = _id

    def init_session(self):
        if not self._id:
            self._id = self.generate_session_id()
            self._handler.set_secure_cookie("session_id", self._id)
        # 设置延期时间
        self._redis.hset(self._id, 'last_active', time.time())
        self._redis.expire(self._id, self._handler.settings['session_expire'])

    def generate_session_id(self):
        secret_key = self._handler.settings['cookie_secret']
        ip = self._handler.request.remote_ip
        while True:
            rand = os.urandom(16)
            now = time.time()
            result = "{!s}{!s}{!s}{!s}".format(rand, now, ip, secret_key).encode()

            session_id = hashlib.sha1(result)
            session_id = self._prefix + session_id.hexdigest()
            if not self._redis.exists(session_id):
                break
        return session_id

    def __getattr__(self, item):
        if self._id:
            return self._redis.hget(self._id, item)
        return super(Session, self).__getattribute__(item)

    def __setattr__(self, key, value):
        """在为session对象设置属性后，进行session的更新或创建"""
        if not key in self._skip:
            self.init_session()
            self._redis.hset(self._id, key, value)
        super(Session, self).__setattr__(key, value)

    def __delattr__(self, item):
        if not item in self._skip:
            return self._redis.hdel(self._id, item)
        super(Session, self).__delattr__(item)


class SessionMixin(object):
    def prepare(self):
        self.session = Session(self)
        super(SessionMixin, self).prepare()