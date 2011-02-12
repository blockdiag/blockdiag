# -*- coding: utf-8 -*-
from blockdiag.noderenderer import NodeShape
from blockdiag.noderenderer import install_renderer
from blockdiag.utils.XY import XY


class Diamond(NodeShape):
    def __init__(self, node, metrix=None):
        super(Diamond, self).__init__(node, metrix)

        r = metrix.cellSize
        m = metrix.cell(node)
        self.diamond = (XY(m.top().x, m.top().y - r),
                        XY(m.right().x + r, m.right().y),
                        XY(m.bottom().x, m.bottom().y + r),
                        XY(m.left().x - r, m.left().y),
                        XY(m.top().x, m.top().y - r))
        self.box = ((self.diamond[0].x + self.diamond[3].x) / 2,
                    (self.diamond[0].y + self.diamond[3].y) / 2,
                    (self.diamond[1].x + self.diamond[2].x) / 2,
                    (self.diamond[1].y + self.diamond[2].y) / 2)

    def render_shape(self, drawer, format, **kwargs):
        outline = kwargs.get('outline')
        font = kwargs.get('font')
        fill = kwargs.get('fill')

        # draw outline
        if kwargs.get('shadow'):
            diamond = self.shift_shadow(self.diamond)
            drawer.polygon(diamond, fill=fill, outline=fill,
                             filter='transp-blur')
        elif self.node.background:
            drawer.polygon(self.diamond, fill=self.node.color,
                           outline=self.node.color)
            drawer.loadImage(self.node.background, self.box)
            drawer.polygon(self.diamond, fill="none", outline=outline,
                           style=self.node.style)
        else:
            drawer.polygon(self.diamond, fill=self.node.color, outline=outline,
                           style=self.node.style)

        # draw label
        if not kwargs.get('shadow'):
            drawer.textarea(self.box, self.node.label, fill=fill,
                            font=font, fontsize=self.metrix.fontSize,
                            lineSpacing=self.metrix.lineSpacing)

    def top(self):
        return self.diamond[0]

    def left(self):
        return self.diamond[3]

    def right(self):
        return self.diamond[1]

    def bottom(self):
        return self.diamond[2]


def setup(self):
    install_renderer('diamond', Diamond)
    install_renderer('flowchart.condition', Diamond)
