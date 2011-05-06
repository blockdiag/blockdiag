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


class Ellipse(NodeShape):
    def __init__(self, node, metrix=None):
        super(Ellipse, self).__init__(node, metrix)

        r = metrix.cellSize
        box = metrix.cell(node).box()
        self.textbox = (box[0] + r, box[1] + r, box[2] - r, box[3] - r)

    def render_shape(self, drawer, format, **kwargs):
        outline = kwargs.get('outline')
        fill = kwargs.get('fill')

        # draw outline
        box = self.metrix.cell(self.node).box()
        if kwargs.get('shadow'):
            box = self.shift_shadow(box)
            drawer.ellipse(box, fill=fill, outline=fill,
                           filter='transp-blur')
        elif self.node.background:
            drawer.ellipse(box, fill=self.node.color,
                             outline=self.node.color)
            drawer.loadImage(self.node.background, self.textbox)
            drawer.ellipse(box, fill="none", outline=outline,
                           style=self.node.style)
        else:
            drawer.ellipse(box, fill=self.node.color, outline=outline,
                           style=self.node.style)


def setup(self):
    install_renderer('ellipse', Ellipse)
