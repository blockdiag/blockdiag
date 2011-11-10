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


class Diamond(NodeShape):
    def __init__(self, node, metrics=None):
        super(Diamond, self).__init__(node, metrics)

        r = metrics.cellsize
        m = metrics.cell(node)
        self.connectors = [XY(m.top.x, m.top.y - r),
                           XY(m.right.x + r, m.right.y),
                           XY(m.bottom.x, m.bottom.y + r),
                           XY(m.left.x - r, m.left.y),
                           XY(m.top.x, m.top.y - r)]
        self.textbox = Box((self.connectors[0].x + self.connectors[3].x) / 2,
                           (self.connectors[0].y + self.connectors[3].y) / 2,
                           (self.connectors[1].x + self.connectors[2].x) / 2,
                           (self.connectors[1].y + self.connectors[2].y) / 2)

    def render_shape(self, drawer, format, **kwargs):
        fill = kwargs.get('fill')

        # draw outline
        if kwargs.get('shadow'):
            diamond = self.shift_shadow(self.connectors)
            drawer.polygon(diamond, fill=fill, outline=fill,
                             filter='transp-blur')
        elif self.node.background:
            drawer.polygon(self.connectors, fill=self.node.color,
                           outline=self.node.color)
            drawer.loadImage(self.node.background, self.textbox)
            drawer.polygon(self.connectors, fill="none",
                           outline=self.node.linecolor, style=self.node.style)
        else:
            drawer.polygon(self.connectors, fill=self.node.color,
                           outline=self.node.linecolor, style=self.node.style)


def setup(self):
    install_renderer('diamond', Diamond)
    install_renderer('flowchart.condition', Diamond)
