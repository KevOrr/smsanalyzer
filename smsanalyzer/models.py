#!/usr/bin/env python3

import sqlite3

try:
    from smsanalyzer.config import config
except ImportError:
    config = {}

class TextraDatabase():
    def __init__(self, dbpath=None, is_uri=None, conf=None):
        if conf is None:
            conf = config
        if dbpath is None:
            if 'dbpath' in conf:
                dbpath = conf['dbpath']
            else:
                e = ValueError('Must supply dbpath in either the config or to the initiator')
                raise e
        if is_uri is None:
            is_uri = conf.get('is_uri', False)
        self.convos = {}
        self._conn = sqlite3.connect(dbpath, uri=is_uri)
        self.populate()

    def populate(self):
        res = self._conn.execute('select * from convos order by _id asc;')
        names = next(zip(*res.description))
        for convo_info in res:
            self.convos[convo_info[0]] = TextraConvo(dict(zip(names, convo_info)))
        res = self._conn.execute('select * from messages order by _id asc;')
        names = next(zip(*res.description))
        for i, msg_info in enumerate(res):
            msg = TextraMessage(dict(zip(names, msg_info)))
            self.convos[msg_info[1]].messages.append(msg)

class _TextraBase():
    def __getattr__(self, attr):
        if attr in self._info:
            return self._info[attr]
        else:
            raise AttributeError("'{}' object has no attribute '{}'".format(type(self).__name__, attr))

    def __dir__(self):
        attrs = dir(type(self)) + list(self.__dict__) + list(self._info)
        return sorted(set(attrs))

class TextraConvo(_TextraBase):
    def __init__(self, info):
        self._info = info
        # ['id', 'participants', 'lookup_key', 'display_name']
        self.messages = []

class TextraMessage(_TextraBase):
    def __init__(self, info):
        self._info = info
        # ['id', 'convo_id', 'text', 'timestamp', 'direction', 'failed', 'locked', 'delivered']

