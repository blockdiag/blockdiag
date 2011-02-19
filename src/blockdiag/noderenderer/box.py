# -*- coding: utf-8 -*-
from blockdiag.noderenderer import NodeShape
from blockdiag.noderenderer import install_renderer
from blockdiag.utils.XY import XY


class Box(NodeShape):
    def render_shape(self, drawer, format, **kwargs):
        outline = kwargs.get('outline')
        fill = kwargs.get('fill')

        # draw outline
        box = self.metrix.cell(self.node).box()
        if kwargs.get('shadow'):
            box = self.shift_shadow(box)
            drawer.rectangle(box, fill=fill, outline=fill,
                             filter='transp-blur')
        elif self.node.background:
            drawer.rectangle(box, fill=self.node.color,
                             outline=self.node.color)
            drawer.loadImage(self.node.background, self.textbox)
            drawer.rectangle(box, outline=outline, style=self.node.style)
        else:
            drawer.rectangle(box, fill=self.node.color, outline=outline,
                             style=self.node.style)


def setup(self):
    install_renderer('box', Box)
