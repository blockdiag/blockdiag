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


class Actor(NodeShape):
    def __init__(self, node, metrics=None):
        super(Actor, self).__init__(node, metrics)

        self.radius = metrics.node_height / 8  # radius of actor's head
        self.center = metrics.cell(node).center

        self.connectors[1] = XY(self.center.x + self.radius * 5, self.center.y)
        self.connectors[3] = XY(self.center.x - self.radius * 5, self.center.y)

    def head_part(self):
        r = self.radius
        top = self.metrics.cell(self.node).top
        return (top.x - r, top.y, top.x + r, top.y + r * 2)

    def body_part(self):
        r = self.radius
        m = self.metrics.cell(self.node)

        r = self.metrics.node_height / 8  # radius of actor's head
        bodyC = m.center
        neckWidth = r * 2 / 3  # neck size
        arm = r * 4  # arm length
        armWidth = r
        bodyWidth = r * 2 / 3  # half of body width
        bodyHeight = r
        legXout = r * 7 / 2  # toe outer position
        legYout = bodyHeight + r * 3
        legXin = r * 2  # toe inner position
        legYin = bodyHeight + r * 3

        return [XY(bodyC.x + neckWidth, m.top.y + r),
                XY(bodyC.x + neckWidth, bodyC.y - armWidth),  # neck end
                XY(bodyC.x + arm, bodyC.y - armWidth),
                XY(bodyC.x + arm, bodyC.y),  # right arm end
                XY(bodyC.x + bodyWidth, bodyC.y),   # right body end
                XY(bodyC.x + bodyWidth, bodyC.y + bodyHeight),
                XY(bodyC.x + legXout, bodyC.y + legYout),
                XY(bodyC.x + legXin, bodyC.y + legYin),

                XY(bodyC.x, bodyC.y + (bodyHeight * 2)),  # body bottom center

                XY(bodyC.x - legXin, bodyC.y + legYin),
                XY(bodyC.x - legXout, bodyC.y + legYout),
                XY(bodyC.x - bodyWidth, bodyC.y + bodyHeight),
                XY(bodyC.x - bodyWidth, bodyC.y),  # left body end
                XY(bodyC.x - arm, bodyC.y),
                XY(bodyC.x - arm, bodyC.y - armWidth),
                XY(bodyC.x - neckWidth, bodyC.y - armWidth),  # left arm end
                XY(bodyC.x - neckWidth, m.top.y + r)]

    def render_shape(self, drawer, format, **kwargs):
        outline = kwargs.get('outline')
        fill = kwargs.get('fill')

        # FIXME: Actor does not support
        #  - background image
        #  - textarea

        # draw body part
        body = self.body_part()
        if kwargs.get('shadow'):
            body = self.shift_shadow(body)
            drawer.polygon(body, fill=fill, filter='transp-blur')
        else:
            drawer.polygon(body, fill=self.node.color, outline=outline,
                           style=self.node.style)

        # draw head part
        head = self.head_part()
        if kwargs.get('shadow'):
            head = self.shift_shadow(head)
            drawer.ellipse(head, fill=fill, outline=fill, filter='transp-blur')
        else:
            drawer.ellipse(head, fill=self.node.color, outline=outline,
                           style=self.node.style)

    def render_label(self, drawer, **kwargs):
        pass


def setup(self):
    install_renderer('actor', Actor)
