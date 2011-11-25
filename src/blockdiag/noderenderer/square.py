# -*- coding: utf-8 -*-
from blockdiag.noderenderer import NodeShape
from blockdiag.noderenderer import install_renderer
from blockdiag.utils import Box, XY


class Square(NodeShape):
    def __init__(self, node, metrics=None):
        super(Square, self).__init__(node, metrics)

        r = min(metrics.node_width, metrics.node_height) / 2 + \
            metrics.cellsize / 2
        pt = metrics.cell(node).center
        self.connectors = [XY(pt.x, pt.y - r),  # top
                           XY(pt.x + r, pt.y),  # right
                           XY(pt.x, pt.y + r),  # bottom
                           XY(pt.x - r, pt.y)]  # left
        self.textbox = Box(pt.x - r, pt.y - r, pt.x + r, pt.y + r)

    def render_shape(self, drawer, format, **kwargs):
        outline = kwargs.get('outline')
        fill = kwargs.get('fill')

        # draw outline
        if kwargs.get('shadow'):
            box = self.shift_shadow(self.textbox)
            drawer.rectangle(box, fill=fill, outline=fill,
                             filter='transp-blur')
        elif self.node.background:
            drawer.rectangle(self.textbox, fill=self.node.color,
                             outline=self.node.color)
            drawer.loadImage(self.node.background, self.textbox)
            drawer.rectangle(self.textbox, fill="none",
                             outline=self.node.linecolor,
                             style=self.node.style)
        else:
            drawer.rectangle(self.textbox, fill=self.node.color,
                             outline=self.node.linecolor,
                             style=self.node.style)


def setup(self):
    install_renderer('square', Square)
