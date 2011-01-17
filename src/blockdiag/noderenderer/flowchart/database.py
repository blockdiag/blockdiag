# -*- coding: utf-8 -*-
import math
from blockdiag.SVGdraw import pathdata
from blockdiag.utils.XY import XY
from blockdiag.utils import renderer


def render_node(drawer, format, node, metrix, **kwargs):
    if format == 'SVG':
        render_svg_node(drawer, node, metrix, **kwargs)
    else:
        render_image_node(drawer, node, metrix, **kwargs)


def render_svg_node(drawer, node, metrix, **kwargs):
    outline = kwargs.get('outline')
    font = kwargs.get('font')
    fill = kwargs.get('fill')
    badgeFill = kwargs.get('badgeFill')

    m = metrix.node(node)
    r = metrix.cellSize

    box = (m.topLeft().x, m.topLeft().y + r,
           m.bottomRight().x, m.bottomRight().y - r)

    path = pathdata(box[0], box[1])
    path.ellarc(metrix.nodeWidth / 2, r, 0, 0, 1, box[2], box[1])
    path.line(box[2], box[3])
    path.ellarc(metrix.nodeWidth / 2, r, 0, 0, 1, box[0], box[3])
    path.line(box[0], box[1])

    if node.background:
        drawer.path(path, fill=node.color, style=node.style)
        drawer.loadImage(node.background, m.box())
        drawer.path(path, fill="none", outline=fill, style=node.style)
    else:
        drawer.path(path, fill=node.color, outline=fill, style=node.style)

    path = pathdata(box[2], box[1])
    path.ellarc(metrix.nodeWidth / 2, r, 0, 0, 1, box[0], box[1])
    drawer.path(path, fill=node.color, outline=fill, style=node.style)

    box = (m.topLeft().x, m.topLeft().y + int(r * 1.5),
           m.bottomRight().x, m.bottomRight().y - int(r * 0.5))
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
    r = metrix.cellSize
    thick = metrix.scale_ratio

    if thick == 1:
        d = 0
    else:
        d = int(math.ceil(thick / 2.0))

    # bottom ellipse
    box = (m.bottomLeft().x, m.bottomLeft().y - r * 2,
           m.bottomRight().x, m.bottomRight().y)
    drawer.ellipse(box, fill=node.color, outline=outline, style=node.style)

    # center rectangle but not outlined
    box = (m.topLeft().x, m.topLeft().y + r,
           m.bottomRight().x, m.bottomRight().y - r)
    drawer.rectangle(box, fill=node.color, outline=node.color)

    # top ellipse
    box = (m.topLeft().x, m.topLeft().y,
           m.bottomRight().x, m.topRight().y + r * 2)
    drawer.ellipse(box, fill=node.color, outline=outline, style=node.style)

    # line both side
    line = (XY(m.topLeft().x, m.topLeft().y + r),
            XY(m.bottomLeft().x, m.bottomLeft().y - r))
    drawer.line(line, fill=outline, width=thick, style=node.style)
    line = (XY(m.topRight().x, m.topRight().y + r),
            XY(m.bottomRight().x, m.bottomRight().y - r))
    drawer.line(line, fill=outline, width=thick, style=node.style)

    if node.background:
        drawer.loadImage(node.background, m.box())

    box = (m.topLeft().x, m.topLeft().y + int(r * 1.5),
           m.bottomRight().x, m.bottomRight().y - int(r * 0.5))
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
    if format == 'SVG':
        render_svg_shadow(drawer, node, metrix, fill)
    else:
        render_image_shadow(drawer, node, metrix, fill)


def render_svg_shadow(drawer, node, metrix, fill):
    m = metrix.node(node)
    r = metrix.cellSize

    box = (m.topLeft().x, m.topLeft().y + r,
           m.bottomRight().x, m.bottomRight().y - r)
    shadow = renderer.shift_box(box, metrix.shadowOffsetX,
                                metrix.shadowOffsetY)

    path = pathdata(shadow[0], shadow[1])
    path.ellarc(metrix.nodeWidth / 2, r, 0, 0, 1, shadow[2], shadow[1])
    path.line(shadow[2], shadow[3])
    path.ellarc(metrix.nodeWidth / 2, r, 0, 0, 1, shadow[0], shadow[3])
    path.line(shadow[0], shadow[1])

    drawer.path(path, fill=fill, filter='transp-blur')


def render_image_shadow(drawer, node, metrix, fill):
    m = metrix.node(node)
    r = metrix.cellSize

    box = (m.bottomLeft().x, m.bottomLeft().y - r * 2,
           m.bottomRight().x, m.bottomRight().y)
    shadow = renderer.shift_box(box, metrix.shadowOffsetX,
                                metrix.shadowOffsetY)
    drawer.ellipse(shadow, fill=fill, filter='transp-blur')

    box = (m.topLeft().x, m.topLeft().y,
           m.bottomRight().x, m.topRight().y + r * 2)
    shadow = renderer.shift_box(box, metrix.shadowOffsetX,
                                metrix.shadowOffsetY)
    drawer.ellipse(shadow, fill=fill, filter='transp-blur')

    box = (m.topLeft().x, m.topLeft().y + r,
           m.bottomRight().x, m.bottomRight().y - r)
    shadow = renderer.shift_box(box, metrix.shadowOffsetX,
                                metrix.shadowOffsetY)
    drawer.rectangle(shadow, fill=fill, filter='transp-blur')
