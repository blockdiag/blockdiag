# -*- coding: utf-8 -*-
from blockdiag.noderenderer import NodeShape
from blockdiag.noderenderer import install_renderer
from blockdiag.utils.XY import XY


class TextBox(NodeShape):
    def render_shape(self, drawer, format, **kwargs):
        outline = kwargs.get('outline')
        fill = kwargs.get('fill')

        box = self.metrix.cell(self.node).box()
        if self.node.background:
            drawer.loadImage(self.node.background, self.textbox)


def setup(self):
    install_renderer('textbox', TextBox)
