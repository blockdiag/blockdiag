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
import utils.LaterCall


class LineJumpDrawFilter(utils.LaterCall.LaterCall):
    def __init__(self, target, jump_radius):
        super(LineJumpDrawFilter, self).__init__(target)
        self.ytree = []
        self.cross = {}
        self.jump_radius = jump_radius

    def _run(self):
        line_method = self._find_method("line")
        for func, arg, kw in self.calls:
            if func == line_method:
                ((x1, y1), (x2, y2)) = arg[0]
                if y1 == y2:
                    y = y1
                    if x2 < x1:
                        x1, x2 = x2, x1

                    for x in sorted(self.cross.get(y, [])):
                        if x1 <= x and x <= x2:
                            r = self.jump_radius
                            self.target.line((XY(x1, y), XY(x - r, y)), **kw)
                            box = (x - r, y - r, x + r, y + r)
                            self.target.arc(box, 180, 0, **kw)
                            x1 = x + r

                    self.target.line((XY(x1, y), XY(x2, y)), **kw)
                    continue

            func(self.target, *arg, **kw)

    def line(self, xy, **kw):
        from bisect import insort
        for st, ed in zip(xy[:-1], xy[1:]):
            super(LineJumpDrawFilter, self)._add_call("line")((st, ed), **kw)
            if st.y == ed.y:    # horizonal
                insort(self.ytree, (st.y, 0, (st, ed)))
            elif st.x == ed.x:  # vertical
                insort(self.ytree, (max(st.y, ed.y), -1, (st, ed)))
                insort(self.ytree, (min(st.y, ed.y), +1, (st, ed)))

    def save(self, *arg, **kw):
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
        self.target.save(*arg, **kw)
