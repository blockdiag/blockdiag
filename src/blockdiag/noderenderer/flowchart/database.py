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
    r = metrix.cellSize * 2
    thick = metrix.scale_ratio

    if thick == 1:
        d = 0
    else:
        d = int(math.ceil(thick / 2.0))

    # bottom ellipse
    box = (m.bottomLeft().x, m.bottomLeft().y - r,
           m.bottomRight().x, m.bottomRight().y);
    drawer.ellipse(box, fill=node.color, outline=outline, style=node.style)
    # center rectangle but not outlined
    box = (m.topLeft().x, m.topLeft().y + (r/2),
           m.bottomRight().x, m.bottomRight().y - (r/2))
    drawer.rectangle(box, fill=node.color, outline=node.color)
    # top ellipse
    box = (m.topLeft().x, m.topLeft().y,
           m.bottomRight().x, m.topRight().y + r)
    drawer.ellipse(box, fill=node.color, outline=outline, style=node.style)
    # line both side
    line = (XY(m.topLeft().x,m.topLeft().y+(r/2)),
	    XY(m.bottomLeft().x,m.bottomLeft().y-(r/2)))
    drawer.line(line, fill=outline, width=thick, style=node.style)
    line = (XY(m.topRight().x,m.topRight().y+(r/2)),
	    XY(m.bottomRight().x,m.bottomRight().y-(r/2)))
    drawer.line(line, fill=outline, width=thick, style=node.style)

    if node.background:
        drawer.loadImage(node.background, m.box())

    box = (m.topLeft().x + r, m.topLeft().y + (r/2),
	   m.bottomRight().x - r, m.bottomRight().y)
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

    #
    box = (m.bottomLeft().x, m.bottomLeft().y - r,
           m.bottomRight().x, m.bottomRight().y);
    shadow = renderer.shift_box(box, metrix.shadowOffsetX,
                                metrix.shadowOffsetY)
    drawer.ellipse(shadow, fill=fill, filter='transp-blur')

    box = (m.topLeft().x, m.topLeft().y,
           m.bottomRight().x, m.topRight().y + r)
    shadow = renderer.shift_box(box, metrix.shadowOffsetX,
                                metrix.shadowOffsetY)
    drawer.ellipse(shadow, fill=fill, filter='transp-blur')

    box = (m.topLeft().x, m.topLeft().y + (r/2),
           m.bottomRight().x, m.bottomRight().y - (r/2))
    shadow = renderer.shift_box(box, metrix.shadowOffsetX,
                                metrix.shadowOffsetY)
    drawer.rectangle(shadow, fill=fill, filter='transp-blur')
