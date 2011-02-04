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
    diamond = (m.top(), m.left(), m.bottom(), m.right(), m.top())
    diamond = (shift_point(m.top(), 0, -r),
               shift_point(m.left(), -r, 0),
               shift_point(m.bottom(), 0, r),
               shift_point(m.right(), r, 0),
               shift_point(m.top(), 0, -r))
    box = (m.topLeft().x + metrix.nodeWidth / 4 - r / 2,
           m.topLeft().y + metrix.nodeHeight / 4 - r / 2,
           m.bottomRight().x - metrix.nodeWidth / 4 + r / 2,
           m.bottomRight().y - metrix.nodeHeight / 4 + r / 2)

    if node.background:
        drawer.polygon(diamond, fill=node.color)
        drawer.loadImage(node.background, box)
        drawer.polygon(diamond, fill="none", outline=outline, style=node.style)
    else:
        drawer.polygon(diamond, outline=outline,
                       fill=node.color, style=node.style)

    drawer.textarea(box, node.label, fill=fill,
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
    m = metrix.cell(node)
    points = (m.top(), m.left(), m.bottom(), m.right())
    shadow = renderer.shift_polygon(points, metrix.shadowOffsetX,
                                    metrix.shadowOffsetY)

    drawer.polygon(shadow, fill=fill, filter='transp-blur')


class NodeMetrix(object):
    def __init__(self, node, metrix):
        self.metrix = metrix
        self.node_metrix = metrix.cell(node)

    def top(self):
        return shift_point(self.node_metrix.top(), 0, - self.metrix.cellSize)

    def left(self):
        return shift_point(self.node_metrix.left(), - self.metrix.cellSize, 0)

    def right(self):
        return shift_point(self.node_metrix.right(), self.metrix.cellSize, 0)

    def bottom(self):
        return shift_point(self.node_metrix.bottom(), 0, self.metrix.cellSize)


def setup(self):
    install_renderer('diamond', self)
    install_renderer('flowchart.condition', self)
