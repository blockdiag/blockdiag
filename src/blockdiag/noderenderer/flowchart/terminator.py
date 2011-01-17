# -*- coding: utf-8 -*-
import math
from blockdiag.utils.XY import XY
from blockdiag.utils import renderer
from blockdiag.SVGdraw import pathdata


def render_node(drawer, format, node, metrix, **kwargs):
    if format == 'SVG':
        render_svg_node(drawer, node, metrix, **kwargs)
    else:
        render_image_node(drawer, node, metrix, **kwargs)


def render_shadow(drawer, format, node, metrix, fill):
    if format == 'SVG':
        render_svg_shadow(drawer, node, metrix, fill)
    else:
        render_image_shadow(drawer, node, metrix, fill)


def render_svg_node(drawer, node, metrix, **kwargs):
    outline = kwargs.get('outline')
    font = kwargs.get('font')
    fill = kwargs.get('fill')
    badgeFill = kwargs.get('badgeFill')

    m = metrix.node(node)
    r = metrix.cellSize * 2
    thick = metrix.scale_ratio

    box = (m.topLeft().x + r, m.topLeft().y,
           m.bottomRight().x - r, m.bottomRight().y)

    path = pathdata(box[0], box[1])
    path.line(box[2], box[1])
    path.ellarc(r, metrix.nodeHeight / 2, 0, 0, 1, box[2], box[3])
    path.line(box[0], box[3])
    path.ellarc(r, metrix.nodeHeight / 2, 0, 0, 1, box[0], box[1])

    if node.background:
        drawer.path(path, fill=node.color, style=node.style)
        drawer.loadImage(node.background, m.box())
        drawer.path(path, fill="none", outline=fill, style=node.style)
    else:
        drawer.path(path, fill=node.color, outline=fill, style=node.style)

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


def render_image_node(drawer, node, metrix, **kwargs):
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
        drawer.loadImage(node.background, box)

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


def render_svg_shadow(drawer, node, metrix, fill):
    m = metrix.node(node)
    r = metrix.cellSize * 2

    box = (m.topLeft().x + r, m.topLeft().y,
           m.bottomRight().x - r, m.bottomRight().y)
    shadow = renderer.shift_box(box, metrix.shadowOffsetX,
                                metrix.shadowOffsetY)

    path = pathdata(shadow[0], shadow[1])
    path.line(shadow[2], shadow[1])
    path.ellarc(r, metrix.nodeHeight / 2, 0, 0, 1, shadow[2], shadow[3])
    path.line(shadow[0], shadow[3])
    path.ellarc(r, metrix.nodeHeight / 2, 0, 0, 1, shadow[0], shadow[1])

    drawer.path(path, fill=fill, filter='transp-blur')


def render_image_shadow(drawer, node, metrix, fill):
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
