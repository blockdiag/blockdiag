# -*- coding: utf-8 -*-
from blockdiag.noderenderer import install_renderer
from blockdiag.utils.XY import XY
from blockdiag.utils import renderer


def head_circle(node, metrix):
    m = metrix.cell(node)
    r = metrix.nodeHeight / 8  # radius of actor's head
    top = m.top()
    return (top.x - r, top.y, top.x + r, top.y + r * 2)


def body_polygon(node, metrix):
    m = metrix.cell(node)

    r = metrix.nodeHeight / 8  # radius of actor's head
    bodyC = m.center()
    neckWidth = r * 2 / 3  # neck size
    arm = r * 4  # arm length
    armWidth = r
    bodyWidth = r * 2 / 3  # half of body width
    bodyHeight = r
    legXout = r * 7 / 2  # toe outer position
    legYout = bodyHeight + r * 3
    legXin = r * 2  # toe inner position
    legYin = bodyHeight + r * 3

    return [XY(bodyC.x + neckWidth, m.topCenter().y + r),
            XY(bodyC.x + neckWidth, bodyC.y - armWidth),  # neck end
            XY(bodyC.x + arm, bodyC.y - armWidth),
            XY(bodyC.x + arm, bodyC.y),  # right arm end
            XY(bodyC.x + bodyWidth, bodyC.y),   # right body end
            XY(bodyC.x + bodyWidth, bodyC.y + bodyHeight),
            XY(bodyC.x + legXout, bodyC.y + legYout),
            XY(bodyC.x + legXin, bodyC.y + legYin),

            XY(bodyC.x, bodyC.y + (bodyHeight * 2)),  # body bottom center

            XY(bodyC.x - legXin, bodyC.y + legYin),
            XY(bodyC.x - legXout, bodyC.y + legYout),
            XY(bodyC.x - bodyWidth, bodyC.y + bodyHeight),
            XY(bodyC.x - bodyWidth, bodyC.y),  # left body end
            XY(bodyC.x - arm, bodyC.y),
            XY(bodyC.x - arm, bodyC.y - armWidth),
            XY(bodyC.x - neckWidth, bodyC.y - armWidth),  # left arm end
            XY(bodyC.x - neckWidth, m.topCenter().y + r)
            ]


def render_node(drawer, format, node, metrix, **kwargs):
    outline = kwargs.get('outline')
    font = kwargs.get('font')
    fill = kwargs.get('fill')
    badgeFill = kwargs.get('badgeFill')

    # Actor does not support
    #  - background image
    #  - textarea

    # draw body
    body = body_polygon(node, metrix)
    drawer.polygon(body, fill=node.color, outline=outline)

    # draw head part
    head = head_circle(node, metrix)
    drawer.ellipse(head, fill=node.color, outline=outline, style=node.style)

    if node.numbered != None:
        xy = m.topLeft()
        r = metrix.cellSize

        box = (xy.x - r, xy.y - r, xy.x + r, xy.y + r)
        drawer.ellipse(box, outline=fill, fill=badgeFill)
        drawer.textarea(box, node.numbered, fill=fill,
                        font=font, fontsize=metrix.fontSize)


def render_shadow(drawer, format, node, metrix, fill):
    head = head_circle(node, metrix)
    shadow = renderer.shift_box(head, metrix.shadowOffsetX,
                                metrix.shadowOffsetY)
    drawer.ellipse(shadow, fill=fill, outline=fill, filter='transp-blur')

    box = body_polygon(node, metrix)
    shadow = renderer.shift_polygon(box, metrix.shadowOffsetX,
                                metrix.shadowOffsetY)

    drawer.polygon(shadow, fill=fill, filter='transp-blur')


def setup(self):
    install_renderer('actor', self)
