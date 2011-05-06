# -*- coding: utf-8 -*-
#  Copyright 2011 Takeshi KOMIYA
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.


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
