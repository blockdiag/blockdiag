# -*- coding: utf-8 -*-
from blockdiag.noderenderer import NodeShape
from blockdiag.noderenderer import install_renderer
from blockdiag.utils.XY import XY


class LoopIn(NodeShape):
    def __init__(self, node, metrix=None):
        super(LoopIn, self).__init__(node, metrix)

        m = self.metrix.cell(self.node)
        xdiff = self.metrix.nodeWidth / 4
        ydiff = self.metrix.nodeHeight / 4

        textbox = (m.topLeft().x, m.topLeft().y + ydiff,
                   m.bottomRight().x, m.bottomRight().y)

    def render_shape(self, drawer, format, **kwargs):
        outline = kwargs.get('outline')
        fill = kwargs.get('fill')

        m = self.metrix.cell(self.node)
        xdiff = self.metrix.nodeWidth / 4
        ydiff = self.metrix.nodeHeight / 4

        shape = [XY(m.topLeft().x + xdiff, m.topLeft().y),
                 XY(m.topRight().x - xdiff, m.topLeft().y),
                 XY(m.topRight().x, m.topRight().y + ydiff),
                 XY(m.topRight().x, m.bottomRight().y),
                 XY(m.topLeft().x, m.bottomLeft().y),
                 XY(m.topLeft().x, m.topLeft().y + ydiff),
                 XY(m.topLeft().x + xdiff, m.topLeft().y)]

        # draw outline
        if kwargs.get('shadow'):
            shape = self.shift_shadow(shape)
            drawer.polygon(shape, fill=fill, outline=fill,
                           filter='transp-blur')
        elif self.node.background:
            drawer.polygon(shape, fill=self.node.color,
                             outline=self.node.color)
            drawer.loadImage(self.node.background, self.textbox)
            drawer.polygon(shape, fill="none", outline=outline,
                           style=self.node.style)
        else:
            drawer.polygon(shape, fill=self.node.color, outline=outline,
                           style=self.node.style)


def setup(self):
    install_renderer('flowchart.loopin', LoopIn)
