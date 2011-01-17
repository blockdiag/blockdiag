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

    tr = m.topRight()
    note = [m.topLeft(), XY(tr.x - w, tr.y), XY(tr.x, tr.y + w),
            m.bottomRight(), m.bottomLeft(), m.topLeft()]

    if node.background:
        drawer.polygon(note, fill=node.color)
        drawer.loadImage(node.background, m.box())
        drawer.polygon(note, fill="none", outline=outline,
                       style=node.style)
    else:
        drawer.polygon(note, fill=node.color, outline=outline)

    folded = [XY(tr.x - w, tr.y), XY(tr.x - w, tr.y + w),
              XY(tr.x, tr.y + w)]
    drawer.line(folded, fill=fill, style=node.style)

    drawer.textarea(m.box(), node.label, fill=fill,
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
    w = metrix.cellSize

    tr = m.topRight()
    note = [m.topLeft(), XY(tr.x - w, tr.y), XY(tr.x, tr.y + w),
            m.bottomRight(), m.bottomLeft(), m.topLeft()]
    shadow = renderer.shift_polygon(note, metrix.shadowOffsetX,
                                    metrix.shadowOffsetY)
    drawer.polygon(shadow, fill=fill, filter='transp-blur')
