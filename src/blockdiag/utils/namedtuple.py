# -*- coding: utf-8 -*-


# Basic implementation of namedtuple for 2.1 < Python < 2.6
def namedtuple(name, fields):
    'Only space-delimited fields are supported.'
    def prop(i, name):
        return (name, property(lambda self: self[i]))
    methods = dict(prop(i, f) for i, f in enumerate(fields.split(' ')))
    methods.update({
        '__new__': lambda cls, *args: tuple.__new__(cls, args),
        '__repr__': lambda self: '%s(%s)' % (
            name,
            ', '.join('%s=%r' % (
                f, getattr(self, f)) for f in fields.split(' ')))})
    return type(name, (tuple,), methods)
