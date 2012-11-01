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

import math
from namedtuple import namedtuple


Size = namedtuple('Size', 'width height')


class XY(tuple):
    mapper = dict(x=0, y=1)

    def __new__(cls, x, y):
        return super(XY, cls).__new__(cls, (x, y))

    def __getattr__(self, name):
        return self[self.mapper[name]]

    def shift(self, x=0, y=0):
        return self.__class__(self.x + x, self.y + y)


class Box(list):
    mapper = dict(x1=0, y1=1, x2=2, y2=3)

    def __init__(self, x1, y1, x2, y2):
        super(Box, self).__init__((x1, y1, x2, y2))

    def __getattr__(self, name):
        return self[self.mapper[name]]

    def __repr__(self):
        _format = "<%s (%s, %s) %dx%d at 0x%08x>"
        params = (self.__class__.__name__, self.x1, self.y1,
                  self.width, self.height, id(self))
        return _format % params

    def shift(self, x=0, y=0):
        return self.__class__(self.x1 + x, self.y1 + y,
                              self.x2 + x, self.y2 + y)

    def get_padding_for(self, size, **kwargs):
        valign = kwargs.get('valign', 'center')
        halign = kwargs.get('halign', 'center')
        padding = kwargs.get('padding', 0)

        if halign == 'left':
            dx = padding
        elif halign == 'right':
            dx = self.size.width - size.width - padding
        else:
            dx = int(math.ceil((self.size.width - size.width) / 2.0))

        if valign == 'top':
            dy = padding
        elif valign == 'bottom':
            dy = self.size.height - size.height - padding
        else:
            dy = int(math.ceil((self.size.height - size.height) / 2.0))

        return dx, dy

    @property
    def size(self):
        return Size(self.width, self.height)

    @property
    def width(self):
        return self.x2 - self.x1

    @property
    def height(self):
        return self.y2 - self.y1

    @property
    def topleft(self):
        return XY(self.x1, self.y1)

    @property
    def top(self):
        return XY(self.x1 + self.width / 2, self.y1)

    @property
    def topright(self):
        return XY(self.x2, self.y1)

    @property
    def bottomleft(self):
        return XY(self.x1, self.y2)

    @property
    def bottom(self):
        return XY(self.x1 + self.width / 2, self.y2)

    @property
    def bottomright(self):
        return XY(self.x2, self.y2)

    @property
    def left(self):
        return XY(self.x1, self.y1 + self.height / 2)

    @property
    def right(self):
        return XY(self.x2, self.y1 + self.height / 2)

    @property
    def center(self):
        return XY(self.x1 + self.width / 2, self.y1 + self.height / 2)
