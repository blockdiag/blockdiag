# -*- coding: utf-8 -*-
import math
from blockdiag.noderenderer import install_renderer
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

    m = metrix.cell(node)
    r = metrix.cellSize
    thick = metrix.scale_ratio

    box = (m.topLeft().x, m.topLeft().y,
           m.bottomRight().x, m.bottomRight().y)

    path = pathdata(box[0] + r, box[1])
    path.line(box[2] - r, box[1])
    path.ellarc(r, r, 0, 0, 1, box[2], box[1] + r)
    path.line(box[2], box[3] - r)
    path.ellarc(r, r, 0, 0, 1, box[2] - r, box[3])
    path.line(box[0] + r, box[3])
    path.ellarc(r, r, 0, 0, 1, box[0], box[3] - r)
    path.line(box[0], box[1] + r)
    path.ellarc(r, r, 0, 0, 1, box[0] + r, box[1])

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

    m = metrix.cell(node)
    r = metrix.cellSize
    thick = metrix.scale_ratio

    if thick == 1:
        d = 0
    else:
        d = int(math.ceil(thick / 2.0))

    render_image_background(drawer, node, metrix,
                            fill=node.color, outline=node.color)

    box = m.box()
    if node.background:
        drawer.loadImage(node.background, box)

    line = (XY(box[0] + r, box[1]), XY(box[2] - r, box[1]))
    drawer.line(line, fill=outline, width=thick, style=node.style)

    line = (XY(box[2], box[1] + r), XY(box[2], box[3] - r))
    drawer.line(line, fill=outline, width=thick, style=node.style)

    line = (XY(box[0] + r, box[3]), XY(box[2] - r, box[3]))
    drawer.line(line, fill=outline, width=thick, style=node.style)

    line = (XY(box[0], box[1] + r), XY(box[0], box[3] - r))
    drawer.line(line, fill=outline, width=thick, style=node.style)

    arc = (box[0], box[1], box[0] + r * 2, box[1] + r * 2)
    drawer.arc(arc, 180, 270, fill=fill, style=node.style)

    arc = (box[2] - r * 2, box[1], box[2], box[1] + r * 2)
    drawer.arc(arc, 270, 360, fill=fill, style=node.style)

    arc = (box[2] - r * 2, box[3] - r * 2, box[2], box[3])
    drawer.arc(arc, 0, 90, fill=fill, style=node.style)

    arc = (box[0], box[3] - r * 2, box[0] + r * 2, box[3])
    drawer.arc(arc, 90, 180, fill=fill, style=node.style)

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
    m = metrix.cell(node)
    r = metrix.cellSize

    box = (m.topLeft().x, m.topLeft().y,
           m.bottomRight().x, m.bottomRight().y)
    shadow = renderer.shift_box(box, metrix.shadowOffsetX,
                                metrix.shadowOffsetY)

    path = pathdata(shadow[0] + r, shadow[1])
    path.line(shadow[2] - r, shadow[1])
    path.ellarc(r, r, 0, 0, 1, shadow[2], shadow[1] + r)
    path.line(shadow[2], shadow[3] - r)
    path.ellarc(r, r, 0, 0, 1, shadow[2] - r, shadow[3])
    path.line(shadow[0] + r, shadow[3])
    path.ellarc(r, r, 0, 0, 1, shadow[0], shadow[3] - r)
    path.line(shadow[0], shadow[1] + r)
    path.ellarc(r, r, 0, 0, 1, shadow[0] + r, shadow[1])

    drawer.path(path, fill=fill, filter='transp-blur')


def render_image_shadow(drawer, node, metrix, fill):
    render_image_background(drawer, node, metrix, fill=fill,
                            outline=fill, shadow=True)


def render_image_background(drawer, node, metrix, **kwargs):
    outline = kwargs.get('outline')
    fill = kwargs.get('fill')
    shadow = kwargs.get('shadow')

    m = metrix.cell(node)
    r = metrix.cellSize

    box = (m.topLeft().x, m.topLeft().y,
           m.topLeft().x + r * 2, m.topLeft().y + r * 2)
    if shadow:
        box = renderer.shift_box(box, metrix.shadowOffsetX,
                                 metrix.shadowOffsetY)
    drawer.ellipse(box, fill=fill, filter='transp-blur')

    box = (m.topRight().x - r * 2, m.topRight().y,
           m.topRight().x, m.topRight().y + r * 2)
    if shadow:
        box = renderer.shift_box(box, metrix.shadowOffsetX,
                                 metrix.shadowOffsetY)
    drawer.ellipse(box, fill=fill, filter='transp-blur')

    box = (m.bottomLeft().x, m.bottomLeft().y - r * 2,
           m.bottomLeft().x + r * 2, m.bottomLeft().y)
    if shadow:
        box = renderer.shift_box(box, metrix.shadowOffsetX,
                                 metrix.shadowOffsetY)
    drawer.ellipse(box, fill=fill, filter='transp-blur')

    box = (m.bottomRight().x - r * 2, m.bottomRight().y - r * 2,
           m.bottomRight().x, m.bottomRight().y)
    if shadow:
        box = renderer.shift_box(box, metrix.shadowOffsetX,
                                 metrix.shadowOffsetY)
    drawer.ellipse(box, fill=fill, filter='transp-blur')

    box = (m.topLeft().x + r, m.topLeft().y,
           m.bottomRight().x - r, m.bottomRight().y)
    if shadow:
        box = renderer.shift_box(box, metrix.shadowOffsetX,
                                 metrix.shadowOffsetY)
    drawer.rectangle(box, fill=fill, outline=outline, filter='transp-blur')

    box = (m.topLeft().x, m.topLeft().y + r,
           m.bottomRight().x, m.bottomRight().y - r)
    if shadow:
        box = renderer.shift_box(box, metrix.shadowOffsetX,
                                 metrix.shadowOffsetY)
    drawer.rectangle(box, fill=fill, outline=outline, filter='transp-blur')


def setup(self):
    install_renderer('roundedbox', self)
