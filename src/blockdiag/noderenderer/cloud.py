# -*- coding: utf-8 -*-
from blockdiag.noderenderer import NodeShape
from blockdiag.noderenderer import install_renderer
from blockdiag.utils.XY import XY
from blockdiag.SVGdraw import pathdata


class Cloud(NodeShape):
    def __init__(self, node, metrix=None):
        super(Cloud, self).__init__(node, metrix)

        r = metrix.cellSize
        pt = metrix.cell(node).topLeft()
        rx = self.metrix.nodeWidth / 12
        ry = self.metrix.nodeHeight / 5
        self.textbox = (pt.x + rx * 2, pt.y + ry,
                        pt.x + rx * 11, pt.y + ry * 4)

    def render_shape(self, drawer, format, **kwargs):
        fill = kwargs.get('fill')

        m = self.metrix.cell(self.node)
        pt = m.topLeft()
        rx = self.metrix.nodeWidth / 12
        ry = self.metrix.nodeHeight / 5
        textbox = (pt.x + rx * 3, pt.y + ry, pt.x + rx * 10, pt.y + ry * 4)

        # draw background
        self.render_shape_background(drawer, format, **kwargs)

        # draw outline
        if not kwargs.get('shadow') and self.node.background:
            drawer.loadImage(self.node.background, self.textbox)

    def render_shape_background(self, drawer, format, **kwargs):
        fill = kwargs.get('fill')

        m = self.metrix.cell(self.node)
        pt = m.topLeft()
        rx = self.metrix.nodeWidth / 12
        ry = self.metrix.nodeHeight / 5

        ellipses = [(pt.x + rx * 2, pt.y + ry,
                     pt.x + rx * 5, pt.y + ry * 3),
                    (pt.x + rx * 4, pt.y,
                     pt.x + rx * 9, pt.y + ry * 2),
                    (pt.x + rx * 8, pt.y + ry,
                     pt.x + rx * 11, pt.y + ry * 3),
                    (pt.x + rx * 9, pt.y + ry * 2,
                     pt.x + rx * 13, pt.y + ry * 4),
                    (pt.x + rx * 8, pt.y + ry * 2,
                     pt.x + rx * 11, pt.y + ry * 5),
                    (pt.x + rx * 5, pt.y + ry * 2,
                     pt.x + rx * 8, pt.y + ry * 5),
                    (pt.x + rx * 2, pt.y + ry * 2,
                     pt.x + rx * 5, pt.y + ry * 5),
                    (pt.x + rx * 0, pt.y + ry * 2,
                     pt.x + rx * 4, pt.y + ry * 4)]

        for e in ellipses:
            if kwargs.get('shadow'):
                e = self.shift_shadow(e)
                drawer.ellipse(e, fill=fill, outline=fill,
                               filter='transp-blur')
            else:
                drawer.ellipse(e, fill=self.node.color, outline=fill,
                               style=self.node.style)

        rects = [(pt.x + rx * 2, pt.y + ry * 2, pt.x + rx * 11, pt.y + ry * 4),
                 (pt.x + rx * 4, pt.y + ry, pt.x + rx * 9, pt.y + ry * 2)]
        for rect in rects:
            if kwargs.get('shadow'):
                rect = self.shift_shadow(rect)
                drawer.rectangle(rect, fill=fill, outline=fill,
                                 filter='transp-blur')
            else:
                drawer.rectangle(rect, fill=self.node.color,
                                 outline=self.node.color)

    def render_vector_shape(self, drawer, format, **kwargs):
        outline = kwargs.get('outline')
        fill = kwargs.get('fill')

        # create pathdata
        m = self.metrix.cell(self.node)
        rx = self.metrix.nodeWidth / 12
        ry = self.metrix.nodeHeight / 5

        pt = m.topLeft()
        if kwargs.get('shadow'):
            pt = self.shift_shadow(pt)

        path = pathdata(pt.x + rx * 2, pt.y + ry * 2)
        path.ellarc(rx * 2, ry, 0, 0, 1, pt.x + rx * 4, pt.y + ry)
        path.ellarc(rx * 2, ry * 3 / 4, 0, 0, 1, pt.x + rx * 9, pt.y + ry)
        path.ellarc(rx * 2, ry, 0, 0, 1, pt.x + rx * 11, pt.y + ry * 2)
        path.ellarc(rx * 2, ry, 0, 0, 1, pt.x + rx * 11, pt.y + ry * 4)
        path.ellarc(rx * 2, ry * 5 / 2, 0, 0, 1, pt.x + rx * 8, pt.y + ry * 4)
        path.ellarc(rx * 2, ry * 5 / 2, 0, 0, 1, pt.x + rx * 5, pt.y + ry * 4)
        path.ellarc(rx * 2, ry * 5 / 2, 0, 0, 1, pt.x + rx * 2, pt.y + ry * 4)
        path.ellarc(rx * 2, ry, 0, 0, 1, pt.x + rx * 2, pt.y + ry * 2)

        # draw outline
        if kwargs.get('shadow'):
            drawer.path(path, fill=fill, outline=fill,
                        filter='transp-blur')
        elif self.node.background:
            drawer.path(path, fill=self.node.color, outline=self.node.color)
            drawer.loadImage(self.node.background, self.textbox)
            drawer.path(path, fill="none", outline=fill,
                        style=self.node.style)
        else:
            drawer.path(path, fill=self.node.color, outline=fill,
                        style=self.node.style)


def setup(self):
    install_renderer('cloud', Cloud)
