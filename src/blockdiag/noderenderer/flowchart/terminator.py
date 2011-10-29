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
from blockdiag.utils import XY, Box
from blockdiag.imagedraw.simplesvg import pathdata


class Terminator(NodeShape):
    def __init__(self, node, metrics=None):
        super(Terminator, self).__init__(node, metrics)

        m = self.metrics.cell(self.node)
        r = self.metrics.cellsize * 2
        self.textbox = (m.topleft.x + r, m.topleft.y,
                        m.bottomright.x - r, m.bottomright.y)

    def render_shape(self, drawer, format, **kwargs):
        fill = kwargs.get('fill')

        # draw background
        self.render_shape_background(drawer, format, **kwargs)

        # draw outline
        box = self.metrics.cell(self.node).box
        if not kwargs.get('shadow') and self.node.background:
            drawer.loadImage(self.node.background, self.textbox)

    def render_shape_background(self, drawer, format, **kwargs):
        outline = kwargs.get('outline')
        fill = kwargs.get('fill')

        m = self.metrics.cell(self.node)
        r = self.metrics.cellsize * 2

        box = m.box
        ellipses = [Box(box[0], box[1], box[0] + r * 2, box[3]),
                    Box(box[2] - r * 2, box[1], box[2], box[3])]

        for e in ellipses:
            if kwargs.get('shadow'):
                e = self.shift_shadow(e)
                drawer.ellipse(e, fill=fill, outline=fill,
                               filter='transp-blur')
            else:
                drawer.ellipse(e, fill=self.node.color, outline=outline,
                               style=self.node.style)

        rect = Box(box[0] + r, box[1], box[2] - r, box[3])
        if kwargs.get('shadow'):
            rect = self.shift_shadow(rect)
            drawer.rectangle(rect, fill=fill, outline=fill,
                             filter='transp-blur')
        else:
            drawer.rectangle(rect, fill=self.node.color,
                             outline=self.node.color)

        lines = [(XY(box[0] + r, box[1]), XY(box[2] - r, box[1])),
                 (XY(box[0] + r, box[3]), XY(box[2] - r, box[3]))]
        for line in lines:
            if not kwargs.get('shadow'):
                drawer.line(line, fill=outline, style=self.node.style)

    def render_vector_shape(self, drawer, format, **kwargs):
        outline = kwargs.get('outline')
        fill = kwargs.get('fill')

        # create pathdata
        m = self.metrics.cell(self.node)
        r = self.metrics.cellsize * 2
        height = self.metrics.node_height

        box = Box(m.topleft.x + r, m.topleft.y,
                  m.bottomright.x - r, m.bottomright.y)
        if kwargs.get('shadow'):
            box = self.shift_shadow(box)

        path = pathdata(box[0], box[1])
        path.line(box[2], box[1])
        path.ellarc(r, height / 2, 0, 0, 1, box[2], box[3])
        path.line(box[0], box[3])
        path.ellarc(r, height / 2, 0, 0, 1, box[0], box[1])

        # draw outline
        if kwargs.get('shadow'):
            drawer.path(path, fill=fill, outline=fill,
                        filter='transp-blur')
        elif self.node.background:
            drawer.path(path, fill=self.node.color, outline=self.node.color)
            drawer.loadImage(self.node.background, self.textbox)
            drawer.path(path, fill="none", outline=outline,
                        style=self.node.style)
        else:
            drawer.path(path, fill=self.node.color, outline=outline,
                        style=self.node.style)


def setup(self):
    install_renderer('flowchart.terminator', Terminator)
