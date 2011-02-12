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
        self.diamond = (XY(c.x, c.y - r),
                        XY(c.x + r, c.y),
                        XY(c.x, c.y + r),
                        XY(c.x - r, c.y),
                        XY(c.x, c.y - r))

    def render_shape(self, drawer, format, **kwargs):
        outline = kwargs.get('outline')
        font = kwargs.get('font')
        fill = kwargs.get('fill')

        # draw outline
        if kwargs.get('shadow'):
            diamond = self.shift_shadow(self.diamond)
            drawer.polygon(diamond, fill=fill, outline=fill,
                             filter='transp-blur')
        else:
            drawer.polygon(self.diamond, fill=self.node.color, outline=outline,
                           style=self.node.style)

        # draw label
        if not kwargs.get('shadow'):
            m = self.metrix.cell(self.node)
            textbox = (m.top().x, m.top().y, m.right().x, m.right().y)
            drawer.textarea(textbox, self.node.label, fill=fill,
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
    install_renderer('minidiamond', MiniDiamond)
