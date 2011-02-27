# -*- coding: utf-8 -*-
from blockdiag.noderenderer import NodeShape
from blockdiag.noderenderer import install_renderer
from blockdiag.utils.XY import XY


class Note(NodeShape):
    def render_shape(self, drawer, format, **kwargs):
        outline = kwargs.get('outline')
        fill = kwargs.get('fill')

        m = self.metrix.cell(self.node)
        r = self.metrix.cellSize * 2

        tr = m.topRight()
        note = [m.topLeft(), XY(tr.x - r, tr.y), XY(tr.x, tr.y + r),
                m.bottomRight(), m.bottomLeft(), m.topLeft()]
        box = self.metrix.cell(self.node).box()

        # draw outline
        if kwargs.get('shadow'):
            note = self.shift_shadow(note)
            drawer.polygon(note, fill=fill, outline=fill,
                           filter='transp-blur')
        elif self.node.background:
            drawer.polygon(note, fill=self.node.color,
                             outline=self.node.color)
            drawer.loadImage(self.node.background, box)
            drawer.polygon(note, fill="none", outline=outline,
                           style=self.node.style)
        else:
            drawer.polygon(note, fill=self.node.color, outline=outline,
                           style=self.node.style)

        # draw folded
        if not kwargs.get('shadow'):
            folded = [XY(tr.x - r, tr.y),
                      XY(tr.x - r, tr.y + r),
                      XY(tr.x, tr.y + r)]
            drawer.line(folded, fill=fill, style=self.node.style)


def setup(self):
    install_renderer('note', Note)
