# -*- coding: utf-8 -*-
from blockdiag.noderenderer import install_renderer
from blockdiag.utils import renderer
from blockdiag.utils.XY import XY
import blockdiag.DiagramMetrix


def render_node(drawer, format, node, metrix, **kwargs):
    outline = kwargs.get('outline')
    font = kwargs.get('font')
    fill = kwargs.get('fill')
    badgeFill = kwargs.get('badgeFill')

    m = metrix.cell(node)
    r = metrix.cellSize
    box = (m.top().x - r, m.top().y + metrix.nodeHeight / 2 - r,
           m.top().x + r, m.top().y + metrix.nodeHeight / 2 + r)

    drawer.ellipse(box, outline=outline,
                   fill=node.color, style=node.style)

    textbox = (m.top().x, m.top().y, m.right().x, m.right().y)
    drawer.textarea(textbox, node.label, fill=fill, halign="left",
                    font=font, fontsize=metrix.fontSize,
                    lineSpacing=metrix.lineSpacing)


def render_shadow(drawer, format, node, metrix, fill):
    m = metrix.cell(node)
    r = metrix.cellSize
    box = (m.top().x - r, m.top().y + metrix.nodeHeight / 2 - r,
           m.top().x + r, m.top().y + metrix.nodeHeight / 2 + r)

    shadow = renderer.shift_box(box, metrix.shadowOffsetX,
                                metrix.shadowOffsetY)

    drawer.ellipse(shadow, fill=fill, filter='transp-blur')


class NodeMetrix(object):
    def __init__(self, node, metrix):
        self.metrix = metrix
        top = metrix.cell(node).top()

        self.radius = self.metrix.cellSize
        self.center = XY(top.x, top.y + metrix.nodeHeight / 2)

    def top(self):
        return XY(self.center.x, self.center.y - self.radius)

    def left(self):
        return XY(self.center.x - self.radius, self.center.y)

    def right(self):
        return XY(self.center.x + self.radius, self.center.y)

    def bottom(self):
        return XY(self.center.x, self.center.y + self.radius)


def setup(self):
    install_renderer('endpoint', self)
