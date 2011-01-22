# -*- coding: utf-8 -*-
from blockdiag.noderenderer import install_renderer
from blockdiag.utils import renderer
from blockdiag.utils.renderer import shift_point
from blockdiag.utils.XY import XY


def render_node(drawer, format, node, metrix, **kwargs):
    outline = kwargs.get('outline')
    font = kwargs.get('font')
    fill = kwargs.get('fill')
    badgeFill = kwargs.get('badgeFill')

    m = metrix.cell(node)
    r = metrix.cellSize
    center = shift_point(m.top(), 0, metrix.nodeHeight / 2)
    diamond = (shift_point(center, 0, -r),
               shift_point(center, -r, 0),
               shift_point(center, 0, r),
               shift_point(center, r, 0),
               shift_point(center, 0, -r))
    drawer.polygon(diamond, outline=outline,
                   fill=node.color, style=node.style)

    textbox = (m.top().x, m.top().y, m.right().x, m.right().y)
    drawer.textarea(textbox, node.label, fill=fill, halign="left",
                    font=font, fontsize=metrix.fontSize,
                    lineSpacing=metrix.lineSpacing)

    if node.numbered != None:
        xy = m.topLeft()
        r = metrix.cellSize

        box = (xy.x - r, xy.y - r, xy.x + r, xy.y + r)
        drawer.ellipse(box, outline=fill, fill=badgeFill)
        drawer.textarea(box, node.numbered, fill=fill,
                        font=font, fontsize=metrix.fontSize)


def render_shadow(drawer, format, node, metrix, fill):
    r = metrix.cellSize
    center = shift_point(metrix.cell(node).top(), 0, metrix.nodeHeight / 2)
    diamond = (shift_point(center, 0, -r),
               shift_point(center, -r, 0),
               shift_point(center, 0, r),
               shift_point(center, r, 0))
    shadow = renderer.shift_polygon(diamond, metrix.shadowOffsetX,
                                    metrix.shadowOffsetY)

    drawer.polygon(shadow, fill=fill, filter='transp-blur')


class NodeMetrix(object):
    def __init__(self, node, metrix):
        self.metrix = metrix
        self.center = shift_point(metrix.cell(node).top(), 0,
                                  metrix.nodeHeight / 2)

    def top(self):
        return shift_point(self.center, 0, - self.metrix.cellSize)

    def left(self):
        return shift_point(self.center, - self.metrix.cellSize, 0)

    def right(self):
        return shift_point(self.center, self.metrix.cellSize, 0)

    def bottom(self):
        return shift_point(self.center, 0, self.metrix.cellSize)


def setup(self):
    install_renderer('minidiamond', self)
