import sqlite3

from smsanalyzer.models import Convo, Message
try:
    from config import config
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
        self.convos = []
        self._conn = sqlite3.connect(dbpath, uri=is_uri)
        self.populate()

    def populate(self):
        res = self._conn.execute('select * from convos order by _id asc;')
        names = next(zip(*res.description))
        for convo_info in res:
            self.convos.append(Convo(dict(zip(names, convo_info))))
        res = self._conn.execute('select * from messages order by _id asc;')
        names = next(zip(*res.description))
        for i, msg_info in enumerate(res):
            msg = Message(dict(zip(names, msg_info)))
            self.convos[msg_info[1]].messages.append(msg)

