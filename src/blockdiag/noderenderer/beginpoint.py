# -*- coding: utf-8 -*-
from blockdiag.noderenderer import NodeShape
from blockdiag.noderenderer import install_renderer
from blockdiag.utils.XY import XY


class BeginPoint(NodeShape):
    def __init__(self, node, metrix=None):
        super(BeginPoint, self).__init__(node, metrix)

        m = metrix.cell(node)

        self.radius = metrix.cellSize
        self.center = m.center()
        self.textbox = [m.top().x, m.top().y, m.right().x, m.right().y]
        self.textalign = 'left'
        self.connectors = [XY(self.center.x, self.center.y - self.radius),
                           XY(self.center.x + self.radius, self.center.y),
                           XY(self.center.x, self.center.y + self.radius),
                           XY(self.center.x - self.radius, self.center.y)]

    def render_shape(self, drawer, format, **kwargs):
        outline = kwargs.get('outline')
        fill = kwargs.get('fill')

        # draw outer circle
        r = self.radius
        box = (self.center.x - r, self.center.y - r,
               self.center.x + r, self.center.y + r)
        if kwargs.get('shadow'):
            box = self.shift_shadow(box)
            drawer.ellipse(box, fill=fill, outline=fill, filter='transp-blur')
        else:
            drawer.ellipse(box, fill='white', outline=outline,
                           style=self.node.style)

        # draw inner circle
        box = (self.center.x - r / 2, self.center.y - r / 2,
               self.center.x + r / 2, self.center.y + r / 2)
        if not kwargs.get('shadow'):
            drawer.ellipse(box, fill=self.node.color, outline=outline,
                           style=self.node.style)


def setup(self):
    install_renderer('beginpoint', BeginPoint)
