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

    box = (m.topCenter(), m.rightCenter(),
	   m.bottomCenter(), m.leftCenter(),
	   m.topCenter() # return to start postion
	   )
    drawer.polygon(box, fill=node.color, outline=outline)

    if node.background:
	drawer.polygon(box, fill=node.color)
        drawer.loadImage(node.background, m.box())
	drawer.polygon(box, fill="none", outline=outline,
		       style=node.style)
    else:
        drawer.polygon(box, fill=node.color, outline=outline)


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

    box = (m.topCenter(), m.rightCenter(),
	   m.bottomCenter(), m.leftCenter())
    shadow = renderer.shift_polygon(box, metrix.shadowOffsetX,
				    metrix.shadowOffsetY)
    drawer.polygon(shadow, fill=fill)
