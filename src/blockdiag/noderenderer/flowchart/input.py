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
from blockdiag.utils import Box, XY


class Input(NodeShape):
    def __init__(self, node, metrics=None):
        super(Input, self).__init__(node, metrics)

        m = self.metrics.cell(self.node)
        r = self.metrics.cellsize * 3

        self.textbox = Box(m.topleft.x + r, m.topleft.y,
                           m.bottomright.x - r, m.bottomright.y)

    def render_shape(self, drawer, _, **kwargs):
        fill = kwargs.get('fill')

        m = self.metrics.cell(self.node)
        r = self.metrics.cellsize * 3

        shape = [XY(m.topleft.x + r, m.topleft.y),
                 XY(m.topright.x, m.topright.y),
                 XY(m.bottomright.x - r, m.bottomright.y),
                 XY(m.bottomleft.x, m.bottomleft.y),
                 XY(m.topleft.x + r, m.topleft.y)]

        # draw outline
        if kwargs.get('shadow'):
            shape = self.shift_shadow(shape)
            if kwargs.get('style') == 'blur':
                drawer.polygon(shape, fill=fill, outline=fill,
                               filter='transp-blur')
            else:
                drawer.polygon(shape, fill=fill, outline=fill)
        elif self.node.background:
            drawer.polygon(shape, fill=self.node.color,
                           outline=self.node.color)
            drawer.image(self.textbox, self.node.background)
            drawer.polygon(shape, fill="none",
                           outline=self.node.linecolor, style=self.node.style)
        else:
            drawer.polygon(shape, fill=self.node.color,
                           outline=self.node.linecolor, style=self.node.style)


def setup(self):
    install_renderer('flowchart.input', Input)
