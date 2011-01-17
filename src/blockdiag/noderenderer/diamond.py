# -*- coding: utf-8 -*-
from blockdiag.utils import renderer
from blockdiag.utils.XY import XY


def render_node(drawer, format, node, metrix, **kwargs):
    outline = kwargs.get('outline')
    font = kwargs.get('font')
    fill = kwargs.get('fill')
    badgeFill = kwargs.get('badgeFill')

    m = metrix.node(node)
    diamond = (m.top(), m.left(), m.bottom(), m.right(), m.top())
    box = (m.topLeft().x + metrix.nodeWidth / 4,
           m.topLeft().y + metrix.nodeHeight / 4,
           m.bottomRight().x - metrix.nodeWidth / 4,
           m.bottomRight().y - metrix.nodeHeight / 4)

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
    m = metrix.node(node)
    points = (m.top(), m.left(), m.bottom(), m.right())
    shadow = renderer.shift_polygon(points, metrix.shadowOffsetX,
                                    metrix.shadowOffsetY)

    drawer.polygon(shadow, fill=fill, filter='transp-blur')
