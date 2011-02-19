# -*- coding: utf-8 -*-
from blockdiag.noderenderer import NodeShape
from blockdiag.noderenderer import install_renderer
from blockdiag.utils.XY import XY


class Input(NodeShape):
    def __init__(self, node, metrix=None):
        super(Input, self).__init__(node, metrix)

        m = self.metrix.cell(self.node)
        r = self.metrix.cellSize * 2

        textbox = (m.topLeft().x + r, m.topLeft().y,
                   m.bottomRight().x - r, m.bottomRight().y)

    def render_shape(self, drawer, format, **kwargs):
        outline = kwargs.get('outline')
        fill = kwargs.get('fill')

        m = self.metrix.cell(self.node)
        r = self.metrix.cellSize * 2

        shape = [XY(m.topLeft().x + r,  m.topLeft().y),
                 XY(m.topRight().x + r, m.topRight().y),
                 XY(m.bottomRight().x - r, m.bottomRight().y),
                 XY(m.bottomLeft().x - r,  m.bottomLeft().y),
                 XY(m.topLeft().x + r,  m.topLeft().y)]

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
    install_renderer('flowchart.input', Input)
