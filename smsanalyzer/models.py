class Convo():
    def __init__(self, info):
        self._info = info
        self.messages = []

    def __getattr__(self, attr):
        # ['id', 'participants', 'lookup_key', 'display_name']
        if attr in self._info:
            return self._info[attr]
        else:
            return object.__getattr__(self, attr)
            # raise AttributeError('{} has no attribute {}'.format(type(self), attr))

class Message():
    def __init__(self, info):
        self._info = info

    def __getattr__(self, attr):
        # ['id', 'convo_id', 'text', 'timestamp', 'direction', 'failed', 'locked', 'delivered']
        if attr in self._info:
            return self._info[attr]
        else:
            return object.__getattr__(self, attr)
            # raise AttributeError('{} has no attribute {}'.format(type(self), attr))
