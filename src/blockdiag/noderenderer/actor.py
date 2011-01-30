# -*- coding: utf-8 -*-
from blockdiag.noderenderer import install_renderer
from blockdiag.utils.XY import XY
from blockdiag.utils import renderer


def head_circle(node, metrix):
    m = metrix.cell(node)
    r = (m.bottomLeft().y - m.topLeft().y) / 7  # head circle radius
    bodyC = XY(m.topCenter().x, m.leftCenter().y)  # Center of body
    return (bodyC.x - r, m.topLeft().y,
            bodyC.x + r, m.topLeft().y + r * 2)


def body_polygon(node, metrix):
    m = metrix.cell(node)

    r = (m.bottomLeft().y - m.topLeft().y) / 7  # head circle radius
    bodyC = XY(m.topCenter().x, m.leftCenter().y)  # Center of body
    neckWidth = 3  # neck size
    arm = (m.topRight().x - m.topLeft().x) / 6  # arm length
    armWidth = 5
    bodyWidth = 4  # half of body width
    bodyHeight = r
    legXout = 18  # toe outer position
    legYout = 20
    legXin = 10  # toe inner position
    legYin = 20

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
            XY(bodyC.x - neckWidth, m.topCenter().y + (r * 2))
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
    box = body_polygon(node, metrix)
    shadow = renderer.shift_polygon(box, metrix.shadowOffsetX,
                                metrix.shadowOffsetY)

    drawer.polygon(shadow, fill=fill, filter='transp-blur')


def setup(self):
    install_renderer('actor', self)
