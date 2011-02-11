# -*- coding: utf-8 -*-
from blockdiag.noderenderer import NodeShape
from blockdiag.noderenderer import install_renderer
from blockdiag.utils.XY import XY


class Mail(NodeShape):
    def render_shape(self, drawer, format, **kwargs):
        outline = kwargs.get('outline')
        font = kwargs.get('font')
        fill = kwargs.get('fill')

        m = self.metrix.cell(self.node)
        r = self.metrix.cellSize * 2
        textbox = (m.topLeft().x, m.topLeft().y + r,
                   m.bottomRight().x, m.bottomRight().y)

        # draw outline
        box = self.metrix.cell(self.node).box()
        if kwargs.get('shadow'):
            box = self.shift_shadow(box)
            drawer.rectangle(box, fill=fill, outline=fill,
                             filter='transp-blur')
        elif self.node.background:
            drawer.rectangle(box, fill=self.node.color,
                             outline=self.node.color)
            drawer.loadImage(self.node.background, textbox)
            drawer.rectangle(box, outline=outline, style=self.node.style)
        else:
            drawer.rectangle(box, fill=self.node.color, outline=outline,
                             style=self.node.style)

        # draw flap
        if not kwargs.get('shadow'):
            flap = [m.topLeft(), XY(m.top().x, m.top().y + r), m.topRight()]
            drawer.line(flap, fill=fill, style=self.node.style)

        # draw label
        if not kwargs.get('shadow'):
            drawer.textarea(textbox, self.node.label, fill=fill,
                            font=font, fontsize=self.metrix.fontSize,
                            lineSpacing=self.metrix.lineSpacing)


def setup(self):
    install_renderer('mail', Mail)
