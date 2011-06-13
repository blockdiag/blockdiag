# -*- coding: utf-8 -*-
from blockdiag.noderenderer import NodeShape
from blockdiag.noderenderer import install_renderer
from blockdiag.utils.XY import XY


class Dots(NodeShape):
    def render_label(self, drawer, **kwargs):
        pass

    def render_shape(self, drawer, format, **kwargs):
        if kwargs.get('shadow'):
            return

        m = self.metrix
        center = m.cell(self.node).center()
        dots = [center]
        if self.node.group.orientation == 'landscape':
            pt = XY(center.x, center.y - m.nodeHeight / 2)
            dots.append(pt)

            pt = XY(center.x, center.y + m.nodeHeight / 2)
            dots.append(pt)
        else:
            pt = XY(center.x - m.nodeWidth / 3, center.y)
            dots.append(pt)

            pt = XY(center.x + m.nodeWidth / 3, center.y)
            dots.append(pt)

        r = m.cellSize / 2
        for dot in dots:
            box = (dot.x - r, dot.y - r, dot.x + r, dot.y + r)
            drawer.ellipse(box, fill='black', outline='black')


def setup(self):
    install_renderer('dots', Dots)
