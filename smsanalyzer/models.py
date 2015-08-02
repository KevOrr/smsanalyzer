class _Base():
    def __getattr__(self, attr):
        if attr in self._info:
            return self._info[attr]
        else:
            raise AttributeError("'{}' object has no attribute '{}'".format(type(self).__name__, attr))

    def __dir__(self):
        attrs = dir(type(self)) + list(self.__dict__) + list(self._info)
        return sorted(set(attrs))

class Convo(_Base):
    def __init__(self, info):
        self._info = info
        # ['id', 'participants', 'lookup_key', 'display_name']
        self.messages = []

class Message(_Base):
    def __init__(self, info):
        self._info = info
        # ['id', 'convo_id', 'text', 'timestamp', 'direction', 'failed', 'locked', 'delivered']
