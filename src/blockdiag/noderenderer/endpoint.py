# -*- coding: utf-8 -*-
from blockdiag.noderenderer import NodeShape
from blockdiag.noderenderer import install_renderer
from blockdiag.utils.XY import XY


class EndPoint(NodeShape):
    def __init__(self, node, metrix=None):
        super(EndPoint, self).__init__(node, metrix)

        self.radius = metrix.cellSize
        self.center = metrix.cell(node).center()

    def render_shape(self, drawer, format, **kwargs):
        outline = kwargs.get('outline')
        font = kwargs.get('font')
        fill = kwargs.get('fill')

        # draw outline
        r = self.radius
        box = (self.center.x - r, self.center.y - r,
               self.center.x + r, self.center.y + r)
        if kwargs.get('shadow'):
            box = self.shift_shadow(box)
            drawer.ellipse(box, fill=fill, outline=fill, filter='transp-blur')
        else:
            drawer.ellipse(box, fill=self.node.color, outline=outline,
                           style=self.node.style)

        # draw label
        if not kwargs.get('shadow'):
            m = self.metrix.cell(self.node)
            textbox = (m.top().x, m.top().y, m.right().x, m.right().y)
            drawer.textarea(textbox, self.node.label, fill=fill, halign="left",
                            font=font, fontsize=self.metrix.fontSize,
                            lineSpacing=self.metrix.lineSpacing)

    def top(self):
        return XY(self.center.x, self.center.y - self.radius)

    def left(self):
        return XY(self.center.x - self.radius, self.center.y)

    def right(self):
        return XY(self.center.x + self.radius, self.center.y)

    def bottom(self):
        return XY(self.center.x, self.center.y + self.radius)


def setup(self):
    install_renderer('endpoint', EndPoint)
