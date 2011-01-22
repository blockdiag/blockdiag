# -*- coding: utf-8 -*-
from blockdiag.noderenderer import install_renderer
from blockdiag.utils import renderer
from blockdiag.utils.XY import XY


def render_node(drawer, format, node, metrix, **kwargs):
    outline = kwargs.get('outline')
    font = kwargs.get('font')
    fill = kwargs.get('fill')
    badgeFill = kwargs.get('badgeFill')

    m = metrix.cell(node)
    r = metrix.cellSize * 2

    box = (m.topLeft().x, m.topLeft().y + r,
           m.bottomRight().x, m.bottomRight().y)
    if node.background:
        drawer.rectangle(m.box(), fill=node.color, outline=node.color)
        drawer.loadImage(node.background, box)
        drawer.rectangle(m.box(), outline=outline, style=node.style)
    else:
        drawer.rectangle(m.box(), outline=outline,
                         fill=node.color, style=node.style)

    flap = [m.topLeft(), XY(m.top().x, m.top().y + r), m.topRight()]
    drawer.line(flap, fill=fill, style=node.style)

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
    box = metrix.cell(node).box()
    shadow = renderer.shift_box(box, metrix.shadowOffsetX,
                                metrix.shadowOffsetY)

    drawer.rectangle(shadow, fill=fill, filter='transp-blur')


def setup(self):
    install_renderer('mail', self)
