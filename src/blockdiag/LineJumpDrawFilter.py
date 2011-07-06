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

from utils.XY import XY


class LazyReciever(object):
    def __init__(self, target):
        self.target = target
        self.calls = []

    def __getattr__(self, name):
        return self.get_lazy_method(name)

    def get_lazy_method(self, name):
        method = self._find_method(name)

        def _(*args, **kwargs):
            self.calls.append((method, args, kwargs))
            return self

        return _

    def _find_method(self, name):
        for p in self.target.__class__.__mro__:
            if name in p.__dict__:
                return p.__dict__[name]

        raise AttributeError("%s instance has no attribute '%s'"
            % (self.target.__class__.__name__, name))

    def _run(self):
        for method, args, kwargs in self.calls:
            method(self.target, *args, **kwargs)


class LineJumpDrawFilter(LazyReciever):
    def __init__(self, target, jump_radius):
        super(LineJumpDrawFilter, self).__init__(target)
        self.ytree = []
        self.cross = {}
        self.jump_radius = jump_radius

    def _run(self):
        line_method = self._find_method("line")
        for method, args, kwargs in self.calls:
            if method == line_method:
                ((x1, y1), (x2, y2)) = args[0]
                if y1 == y2:
                    y = y1
                    if x2 < x1:
                        x1, x2 = x2, x1

                    for x in sorted(self.cross.get(y, [])):
                        if x1 <= x and x <= x2:
                            r = self.jump_radius
                            self.target.line((XY(x1, y), XY(x - r, y)), **kwargs)
                            box = (x - r, y - r, x + r, y + r)
                            self.target.arc(box, 180, 0, **kwargs)
                            x1 = x + r

                    self.target.line((XY(x1, y), XY(x2, y)), **kwargs)
                    continue

            method(self.target, *args, **kwargs)

    def line(self, xy, **kwargs):
        from bisect import insort
        for st, ed in zip(xy[:-1], xy[1:]):
            super(LineJumpDrawFilter, self).get_lazy_method("line")((st, ed), **kwargs)
            if st.y == ed.y:    # horizonal
                insort(self.ytree, (st.y, 0, (st, ed)))
            elif st.x == ed.x:  # vertical
                insort(self.ytree, (max(st.y, ed.y), -1, (st, ed)))
                insort(self.ytree, (min(st.y, ed.y), +1, (st, ed)))

    def save(self, *args, **kwargs):
        # Search crosspoints
        from bisect import insort, bisect_left, bisect_right
        xtree = []
        for y, _, ((x1, y1), (x2, y2)) in self.ytree:
            if x2 < x1:
                x1, x2 = x2, x1
            if y2 < y1:
                y1, y2 = y2, y1

            if y == y1:
                insort(xtree, x1)

            if y == y2:
                del xtree[bisect_left(xtree, x1)]
                for x in xtree[bisect_right(xtree, x1):bisect_left(xtree, x2)]:
                    self.cross.setdefault(y, set()).add(x)

        self._run()
        self.target.save(*args, **kwargs)
