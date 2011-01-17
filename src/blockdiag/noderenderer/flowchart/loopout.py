# -*- coding: utf-8 -*-
import math
from blockdiag.utils.XY import XY
from blockdiag.utils import renderer


def render_node(drawer, format, node, metrix, **kwargs):
    outline = kwargs.get('outline')
    font = kwargs.get('font')
    fill = kwargs.get('fill')
    badgeFill = kwargs.get('badgeFill')

    m = metrix.node(node)
    thick = metrix.scale_ratio

    if thick == 1:
        d = 0
    else:
        d = int(math.ceil(thick / 2.0))

    xdiff = metrix.nodeWidth / 4
    ydiff = metrix.nodeHeight / 4

    poly = [XY(m.topLeft().x, m.topLeft().y),
            XY(m.topRight().x, m.topRight().y),
            XY(m.bottomRight().x, m.bottomRight().y - ydiff),
            XY(m.bottomRight().x - xdiff, m.bottomRight().y),
            XY(m.bottomLeft().x + xdiff, m.bottomLeft().y),
            XY(m.bottomLeft().x, m.bottomLeft().y - ydiff),
            XY(m.topLeft().x, m.topLeft().y)]

    box = (m.topLeft().x, m.topLeft().y,
           m.bottomRight().x, m.bottomRight().y - ydiff)
    if node.background:
        drawer.polygon(poly, fill=node.color)
        drawer.loadImage(node.background, box)
        drawer.polygon(poly, fill="none", outline=outline,
                       style=node.style)
    else:
        drawer.polygon(poly, fill=node.color, outline=outline)

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

    xdiff = (m.topRight().x - m.topLeft().x) / 4
    ydiff = (m.topRight().y - m.bottomLeft().y) / 4

    poly = [XY(m.topLeft().x, m.topLeft().y),
            XY(m.topRight().x, m.topRight().y),
            XY(m.bottomRight().x, m.bottomRight().y + ydiff),
            XY(m.bottomRight().x - xdiff, m.bottomRight().y),
            XY(m.bottomLeft().x + xdiff, m.bottomLeft().y),
            XY(m.bottomLeft().x, m.bottomLeft().y + ydiff)]
    shadow = renderer.shift_polygon(poly, metrix.shadowOffsetX,
                                    metrix.shadowOffsetY)
    drawer.polygon(shadow, fill=fill, filter='transp-blur')
