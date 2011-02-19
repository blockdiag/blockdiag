# -*- coding: utf-8 -*-
from blockdiag.noderenderer import NodeShape
from blockdiag.noderenderer import install_renderer
from blockdiag.utils.XY import XY


class Diamond(NodeShape):
    def __init__(self, node, metrix=None):
        super(Diamond, self).__init__(node, metrix)

        r = metrix.cellSize
        m = metrix.cell(node)
        self.connectors = [XY(m.top().x, m.top().y - r),
                           XY(m.right().x + r, m.right().y),
                           XY(m.bottom().x, m.bottom().y + r),
                           XY(m.left().x - r, m.left().y),
                           XY(m.top().x, m.top().y - r)]
        self.textbox = ((self.connectors[0].x + self.connectors[3].x) / 2,
                        (self.connectors[0].y + self.connectors[3].y) / 2,
                        (self.connectors[1].x + self.connectors[2].x) / 2,
                        (self.connectors[1].y + self.connectors[2].y) / 2)

    def render_shape(self, drawer, format, **kwargs):
        outline = kwargs.get('outline')
        fill = kwargs.get('fill')

        # draw outline
        if kwargs.get('shadow'):
            diamond = self.shift_shadow(self.connectors)
            drawer.polygon(diamond, fill=fill, outline=fill,
                             filter='transp-blur')
        elif self.node.background:
            drawer.polygon(self.connectors, fill=self.node.color,
                           outline=self.node.color)
            drawer.loadImage(self.node.background, self.texbox)
            drawer.polygon(self.connectors, fill="none", outline=outline,
                           style=self.node.style)
        else:
            drawer.polygon(self.connectors, fill=self.node.color,
                           outline=outline, style=self.node.style)


def setup(self):
    install_renderer('diamond', Diamond)
    install_renderer('flowchart.condition', Diamond)
