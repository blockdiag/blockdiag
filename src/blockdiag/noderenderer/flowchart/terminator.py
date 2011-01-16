# -*- coding: utf-8 -*-
import math
from blockdiag.utils.XY import XY


def render_node(drawer, node, metrix, **kwargs):
    outline = kwargs.get('outline')
    font = kwargs.get('font')
    fill = kwargs.get('fill')
    badgeFill = kwargs.get('badgeFill')

    m = metrix.node(node)
    r = metrix.cellSize * 2
    thick = metrix.scale_ratio

    if thick == 1:
        d = 0
    else:
        d = int(math.ceil(thick / 2.0))

    box = (m.topLeft().x, m.topLeft().y,
           m.bottomLeft().x + r * 2, m.bottomLeft().y)
    drawer.ellipse(box, fill=node.color, outline=outline, style=node.style)

    box = (m.topRight().x - r * 2, m.topRight().y,
           m.bottomRight().x, m.bottomRight().y)
    drawer.ellipse(box, fill=node.color, outline=outline, style=node.style)

    box = (m.topLeft().x + r, m.topLeft().y,
           m.bottomRight().x - r, m.bottomRight().y)
    drawer.rectangle(box, fill=node.color, outline=node.color)

    if node.background:
        drawer.loadImage(node.background, m.box())

    line = (XY(box[0], box[1]), XY(box[2], box[1]))
    drawer.line(line, fill=outline, width=thick, style=node.style)

    line = (XY(box[0], box[3]), XY(box[2], box[3]))
    drawer.line(line, fill=outline, width=thick, style=node.style)

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


def render_shadow(drawer, node, metrix, fill):
    m = metrix.node(node)
    r = metrix.cellSize * 2

    box = (m.topLeft().x, m.topLeft().y,
           m.bottomLeft().x + r * 2, m.bottomLeft().y)
    drawer.ellipse(box, fill=fill, filter='transp-blur')

    box = (m.topRight().x - r * 2, m.topRight().y,
           m.bottomRight().x, m.bottomRight().y)
    drawer.ellipse(box, fill=fill, filter='transp-blur')

    box = (m.topLeft().x + r, m.topLeft().y,
           m.bottomRight().x - r, m.bottomRight().y)
    drawer.rectangle(box, fill=fill, filter='transp-blur')
