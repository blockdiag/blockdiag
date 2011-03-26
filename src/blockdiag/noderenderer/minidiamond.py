# -*- coding: utf-8 -*-
from blockdiag.noderenderer import NodeShape
from blockdiag.noderenderer import install_renderer
from blockdiag.utils.XY import XY


class MiniDiamond(NodeShape):
    def __init__(self, node, metrix=None):
        super(MiniDiamond, self).__init__(node, metrix)

        r = metrix.cellSize
        m = metrix.cell(node)
        c = m.center()
        self.connectors = (XY(c.x, c.y - r),
                           XY(c.x + r, c.y),
                           XY(c.x, c.y + r),
                           XY(c.x - r, c.y),
                           XY(c.x, c.y - r))
        self.textbox = (m.top().x, m.top().y, m.right().x, m.right().y)
        self.textalign = 'left'

    def render_shape(self, drawer, format, **kwargs):
        outline = kwargs.get('outline')
        fill = kwargs.get('fill')

        # draw outline
        if kwargs.get('shadow'):
            diamond = self.shift_shadow(self.connectors)
            drawer.polygon(diamond, fill=fill, outline=fill,
                             filter='transp-blur')
        else:
            drawer.polygon(self.connectors, fill=self.node.color,
                           outline=outline, style=self.node.style)


def setup(self):
    install_renderer('minidiamond', MiniDiamond)
