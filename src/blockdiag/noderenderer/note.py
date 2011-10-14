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

from blockdiag.noderenderer import NodeShape
from blockdiag.noderenderer import install_renderer
from blockdiag.utils.XY import XY


class Note(NodeShape):
    def render_shape(self, drawer, format, **kwargs):
        outline = kwargs.get('outline')
        fill = kwargs.get('fill')

        m = self.metrics.cell(self.node)
        r = self.metrics.cellsize * 2

        tr = m.topright
        note = [m.topleft, XY(tr.x - r, tr.y), XY(tr.x, tr.y + r),
                m.bottomright, m.bottomleft, m.topleft]
        box = self.metrics.cell(self.node).box

        # draw outline
        if kwargs.get('shadow'):
            note = self.shift_shadow(note)
            drawer.polygon(note, fill=fill, outline=fill,
                           filter='transp-blur')
        elif self.node.background:
            drawer.polygon(note, fill=self.node.color,
                           outline=self.node.color)
            drawer.loadImage(self.node.background, box)
            drawer.polygon(note, fill="none", outline=outline,
                           style=self.node.style)
        else:
            drawer.polygon(note, fill=self.node.color, outline=outline,
                           style=self.node.style)

        # draw folded
        if not kwargs.get('shadow'):
            folded = [XY(tr.x - r, tr.y),
                      XY(tr.x - r, tr.y + r),
                      XY(tr.x, tr.y + r)]
            drawer.line(folded, fill=outline, style=self.node.style)


def setup(self):
    install_renderer('note', Note)
