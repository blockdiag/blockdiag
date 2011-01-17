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
    w = metrix.cellSize * 2
    thick = metrix.scale_ratio

    if thick == 1:
        d = 0
    else:
        d = int(math.ceil(thick / 2.0))

    parallel = [XY(m.topLeft().x + w,  m.topLeft().y),
                XY(m.topRight().x + w, m.topRight().y),
                XY(m.bottomRight().x - w, m.bottomRight().y),
                XY(m.bottomLeft().x - w,  m.bottomLeft().y),
                XY(m.topLeft().x + w,  m.topLeft().y)]

    box = (m.topLeft().x + w, m.topLeft().y,
           m.bottomRight().x - w, m.bottomRight().y)
    if node.background:
        drawer.polygon(parallel, fill=node.color)
        drawer.loadImage(node.background, box)
        drawer.polygon(parallel, fill="none", outline=outline,
                       style=node.style)
    else:
        drawer.polygon(parallel, fill=node.color, outline=outline)

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
    w = metrix.cellSize * 2

    parallel = [(m.topLeft().x + w,  m.topLeft().y),
                (m.topRight().x + w, m.topRight().y),
                (m.bottomRight().x - w, m.bottomRight().y),
                (m.bottomLeft().x - w,  m.bottomLeft().y),
                (m.topLeft().x + w,  m.topLeft().y)]
    shadow = renderer.shift_polygon(parallel, metrix.shadowOffsetX,
                                    metrix.shadowOffsetY)
    drawer.polygon(shadow, fill=fill, filter='transp-blur')
