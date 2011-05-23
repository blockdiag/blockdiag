class LaterCall(object):
    def __init__(self, target):
        self.target = target
        self.calls = []

    def __getattr__(self, name):
        return self._add_call(name)

    def _add_call(self, name):
        m = self._find_method(name)

        def _(*arg, **kw):
            self.calls.append((m, arg, kw))
            return self

        return _

    def _find_method(self, name):
        for p in self.target.__class__.__mro__:
            if name in p.__dict__:
                return p.__dict__[name]

        raise AttributeError("%s instance has no attribute '%s'"
            % (self.target.__class__.__name__, name))

    def _run(self):
        for func, arg, kw in self.calls:
            func(self.target, *arg, **kw)
