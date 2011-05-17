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

from blockdiag.noderenderer.box import Box
from blockdiag.noderenderer import install_renderer
from blockdiag.utils.XY import XY


class Boxes(Box):
    def __init__(self, node, metrix=None):
        super(Boxes, self).__init__(node, metrix)

        self.boxes = 3
        self.r = self.metrix.cellSize / 2

        r = (self.boxes - 1) * self.r
        self.connectors[1] = XY(self.connectors[1].x + r, self.connectors[1].y)
        self.connectors[2] = XY(self.connectors[2].x, self.connectors[2].y + r)

    def render_shape(self, drawer, format, **kwargs):
        outline = kwargs.get('outline')
        fill = kwargs.get('fill')

        # draw outline
        if kwargs.get('shadow'):
            for i in range(self.boxes - 1, 0, -1):
                r = i * self.r
                box = (self.textbox[0] + r, self.textbox[1] + r,
                       self.textbox[2] + r, self.textbox[3] + r)
                shadow = self.shift_shadow(box)
                drawer.rectangle(shadow, fill=fill, outline=fill,
                                 filter='transp-blur')
        else:
            for i in range(self.boxes - 1, 0, -1):
                r = i * self.r
                box = (self.textbox[0] + r, self.textbox[1] + r,
                       self.textbox[2] + r, self.textbox[3] + r)
                drawer.rectangle(box, fill=self.node.color, outline=outline,
                                 style=self.node.style)

        super(Boxes, self).render_shape(drawer, format, **kwargs)


def setup(self):
    install_renderer('boxes', Boxes)
