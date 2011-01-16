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

    xdiff = (m.topRight().x - m.topLeft().x)/4
    ydiff = (m.topRight().y - m.bottomLeft().y)/4
    
    box = ((m.topLeft().x, m.topLeft().y),
	   (m.topRight().x , m.topRight().y),
	   (m.bottomRight().x , m.bottomRight().y + ydiff),
	   (m.bottomRight().x - xdiff, m.bottomRight().y),
	   (m.bottomLeft().x + xdiff, m.bottomLeft().y),
	   (m.bottomLeft().x , m.bottomLeft().y + ydiff))
    
    drawer.polygon(box, fill=node.color, outline=outline)

    if node.background:
        drawer.loadImage(node.background, m.box())

    box = (m.topLeft().x + r, m.topLeft().y,
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

    box = (m.topLeft().x + r, m.topLeft().y,
           m.bottomRight().x - r, m.bottomRight().y)
    shadow = renderer.shift_box(box, metrix.shadowOffsetX,
                                metrix.shadowOffsetY)
#    drawer.rectangle(shadow, fill=fill, filter='transp-blur')
