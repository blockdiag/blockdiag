# -*- coding: utf-8 -*-
import math
from blockdiag.noderenderer import install_renderer
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

    m = metrix.cell(node)

    pt = m.topLeft()
    rx = metrix.nodeWidth / 12
    ry = metrix.nodeHeight / 5

    box = (pt.x + rx * 2, pt.y + ry,
           pt.x + rx * 11, pt.y + ry * 4)

    path = pathdata(pt.x + rx * 2, pt.y + ry * 2)
    path.ellarc(rx * 2, ry, 0, 0, 1, pt.x + rx * 4, pt.y + ry)
    path.ellarc(rx * 2, ry * 3 / 4, 0, 0, 1, pt.x + rx * 9, pt.y + ry)
    path.ellarc(rx * 2, ry, 0, 0, 1, pt.x + rx * 11, pt.y + ry * 2)
    path.ellarc(rx * 2, ry, 0, 0, 1, pt.x + rx * 11, pt.y + ry * 4)
    path.ellarc(rx * 2, ry * 5 / 2, 0, 0, 1, pt.x + rx * 8, pt.y + ry * 4)
    path.ellarc(rx * 2, ry * 5 / 2, 0, 0, 1, pt.x + rx * 5, pt.y + ry * 4)
    path.ellarc(rx * 2, ry * 5 / 2, 0, 0, 1, pt.x + rx * 2, pt.y + ry * 4)
    path.ellarc(rx * 2, ry, 0, 0, 1, pt.x + rx * 2, pt.y + ry * 2)

    if node.background:
        drawer.path(path, fill=node.color, style=node.style)
        drawer.loadImage(node.background, box)
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

    pt = m.topLeft()
    rx = metrix.nodeWidth / 12
    ry = metrix.nodeHeight / 5

    ellipses = [(pt.x + rx * 2, pt.y + ry, pt.x + rx * 5, pt.y + ry * 3),
                (pt.x + rx * 4, pt.y, pt.x + rx * 9, pt.y + ry * 2),
                (pt.x + rx * 8, pt.y + ry, pt.x + rx * 11, pt.y + ry * 3),
                (pt.x + rx * 9, pt.y + ry * 2, pt.x + rx * 13, pt.y + ry * 4),
                (pt.x + rx * 8, pt.y + ry * 2, pt.x + rx * 11, pt.y + ry * 5),
                (pt.x + rx * 5, pt.y + ry * 2, pt.x + rx * 8, pt.y + ry * 5),
                (pt.x + rx * 2, pt.y + ry * 2, pt.x + rx * 5, pt.y + ry * 5),
                (pt.x + rx * 0, pt.y + ry * 2, pt.x + rx * 4, pt.y + ry * 4)]
    fillers = [(pt.x + rx * 2, pt.y + ry * 2, pt.x + rx * 11, pt.y + ry * 4),
               (pt.x + rx * 4, pt.y + ry, pt.x + rx * 9, pt.y + ry * 2)]

    for box in ellipses:
        drawer.ellipse(box, fill=node.color, outline=fill, style=node.style)

    for box in fillers:
        drawer.rectangle(box, fill=node.color, outline=node.color)

    box = (pt.x + rx * 3, pt.y + ry, pt.x + rx * 10, pt.y + ry * 4)
    if node.background:
        drawer.loadImage(node.background, box)

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
    rx = metrix.nodeWidth / 12
    ry = metrix.nodeHeight / 5

    box = (m.topLeft().x, m.topLeft().y,
           m.bottomRight().x, m.bottomRight().y)
    points = renderer.shift_polygon([m.topLeft()], metrix.shadowOffsetX,
                                    metrix.shadowOffsetY)
    shadow = renderer.shift_box(box, metrix.shadowOffsetX,
                                metrix.shadowOffsetY)

    pt = points[0]
    path = pathdata(pt.x + rx * 2, pt.y + ry * 2)
    path.ellarc(rx * 2, ry, 0, 0, 1, pt.x + rx * 4, pt.y + ry)
    path.ellarc(rx * 2, ry * 3 / 4, 0, 0, 1, pt.x + rx * 9, pt.y + ry)
    path.ellarc(rx * 2, ry, 0, 0, 1, pt.x + rx * 11, pt.y + ry * 2)
    path.ellarc(rx * 2, ry, 0, 0, 1, pt.x + rx * 11, pt.y + ry * 4)
    path.ellarc(rx * 2, ry * 5 / 2, 0, 0, 1, pt.x + rx * 8, pt.y + ry * 4)
    path.ellarc(rx * 2, ry * 5 / 2, 0, 0, 1, pt.x + rx * 5, pt.y + ry * 4)
    path.ellarc(rx * 2, ry * 5 / 2, 0, 0, 1, pt.x + rx * 2, pt.y + ry * 4)
    path.ellarc(rx * 2, ry, 0, 0, 1, pt.x + rx * 2, pt.y + ry * 2)

    drawer.path(path, fill=fill, filter='transp-blur')


def render_image_shadow(drawer, node, metrix, fill):
    m = metrix.node(node)

    points = renderer.shift_polygon([m.topLeft()], metrix.shadowOffsetX,
                                    metrix.shadowOffsetY)
    pt = points[0]
    rx = metrix.nodeWidth / 12
    ry = metrix.nodeHeight / 5

    ellipses = [(pt.x + rx * 2, pt.y + ry, pt.x + rx * 5, pt.y + ry * 3),
                (pt.x + rx * 4, pt.y, pt.x + rx * 9, pt.y + ry * 2),
                (pt.x + rx * 8, pt.y + ry, pt.x + rx * 11, pt.y + ry * 3),
                (pt.x + rx * 9, pt.y + ry * 2, pt.x + rx * 13, pt.y + ry * 4),
                (pt.x + rx * 8, pt.y + ry * 2, pt.x + rx * 11, pt.y + ry * 5),
                (pt.x + rx * 5, pt.y + ry * 2, pt.x + rx * 8, pt.y + ry * 5),
                (pt.x + rx * 2, pt.y + ry * 2, pt.x + rx * 5, pt.y + ry * 5),
                (pt.x + rx * 0, pt.y + ry * 2, pt.x + rx * 4, pt.y + ry * 4)]
    fillers = [(pt.x + rx * 2, pt.y + ry * 2, pt.x + rx * 11, pt.y + ry * 4),
               (pt.x + rx * 4, pt.y + ry, pt.x + rx * 9, pt.y + ry * 2)]

    for box in ellipses:
        drawer.ellipse(box, fill=fill, outline=fill)

    for box in fillers:
        drawer.rectangle(box, fill=fill, outline=fill)


def setup(self):
    install_renderer('cloud', self)
