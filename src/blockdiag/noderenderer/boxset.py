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


class BoxSet(NodeShape):
    def __init__(self, node, metrix=None):
        super(BoxSet, self).__init__(node, metrix)

        self.boxes = 3
        self.r = self.metrix.nodeHeight / 10

        box = self.textbox
        r = self.boxes * self.r
        self.textbox = (box[0] + r, box[1] + r, box[2], box[3])

    def render_shape(self, drawer, format, **kwargs):
        outline = kwargs.get('outline')
        drawer = drawer
        fill = kwargs.get('fill')

        # draw outline
        box = self.metrix.cell(self.node).box()
        if kwargs.get('shadow'):
            for i in range(self.boxes - 1, -1, -1):
                r = i * self.r
                box = (self.textbox[0] - r, self.textbox[1] - r,
                       self.textbox[2] - r, self.textbox[3] - r)
                shadow = self.shift_shadow(box)
                drawer.rectangle(shadow, fill=fill, outline=fill,
                                 filter='transp-blur')
        else:
            for i in range(self.boxes - 1, 0, -1):
                r = i * self.r
                box = (self.textbox[0] - r, self.textbox[1] - r,
                       self.textbox[2] - r, self.textbox[3] - r)
                drawer.rectangle(box, fill=self.node.color, outline=outline,
                                 style=self.node.style)

            box = self.textbox
            if self.node.background:
                drawer.rectangle(box, fill=self.node.color,
                                 outline=self.node.color)
                drawer.loadImage(self.node.background, self.textbox)
                drawer.rectangle(box, outline=outline, style=self.node.style)
            else:
                drawer.rectangle(box, fill=self.node.color, outline=outline,
                                 style=self.node.style)


def setup(self):
    install_renderer('boxset', BoxSet)
