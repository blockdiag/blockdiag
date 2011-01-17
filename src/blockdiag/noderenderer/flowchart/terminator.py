# -*- coding: utf-8 -*-
import math
from utils.XY import XY
from utils import renderer


def render_node(drawer, format, node, metrix, **kwargs):
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
    if node.background:
        drawer.rectangle(box, fill=node.color)
        drawer.loadImage(node.background, box)
	drawer.polygon(box, fill="none", outline=outline,
		       style=node.style)
    else:
        drawer.rectangle(box, fill=node.color, outline=node.color)

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


def render_shadow(drawer, format, node, metrix, fill):
    m = metrix.node(node)
    r = metrix.cellSize * 2

    box = (m.topLeft().x, m.topLeft().y,
           m.bottomLeft().x + r * 2, m.bottomLeft().y)
    shadow = renderer.shift_box(box, metrix.shadowOffsetX,
                                metrix.shadowOffsetY)
    drawer.ellipse(shadow, fill=fill, filter='transp-blur')

    box = (m.topRight().x - r * 2, m.topRight().y,
           m.bottomRight().x, m.bottomRight().y)
    shadow = renderer.shift_box(box, metrix.shadowOffsetX,
                                metrix.shadowOffsetY)
    drawer.ellipse(shadow, fill=fill, filter='transp-blur')

    box = (m.topLeft().x + r, m.topLeft().y,
           m.bottomRight().x - r, m.bottomRight().y)
    shadow = renderer.shift_box(box, metrix.shadowOffsetX,
                                metrix.shadowOffsetY)
    drawer.rectangle(shadow, fill=fill, filter='transp-blur')
