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

        m = self.metrix.cell(self.node)
        self.span = m.metrix.nodeHeight / 10
        self.box = (m.topLeft().x,
                    m.topLeft().y,
                    m.bottomRight().x - self.span * 2,
                    m.bottomRight().y - self.span * 2)

    def render_shape(self, drawer, format, **kwargs):
        self.outline = kwargs.get('outline')
        self.drawer = drawer
        self.fill = kwargs.get('fill')

        for i in range(0, 3):
            if kwargs.get('shadow'):
                self.draw_shadow(self.box)
            self.draw_box(self.box)
            self.box = (self.box[0] + self.span,
                        self.box[1] + self.span,
                        self.box[2] + self.span,
                        self.box[3] + self.span)

        # draw background only once, after draw rect
        if self.node.background:
            self.draw_background(self.box)

    def draw_shadow(self, box):
        box = self.shift_shadow(box)
        self.drawer.rectangle(box, fill=self.fill,
                              outline=self.fill,
                              filter='transp-blur')

    def draw_background(self, box):
        self.drawer.rectangle(box,
                              fill=self.node.color,
                              outline=self.node.color)
        self.drawer.loadImage(self.node.background,
                              self.box)
        self.drawer.rectangle(box,
                              outline=self.outline,
                              style=self.node.style)

    def draw_box(self, box):
        # draw outline
        self.drawer.rectangle(box,
                              fill=self.node.color,
                              outline=self.outline,
                              style=self.node.style)


def setup(self):
    install_renderer('boxset', BoxSet)
