# -*- coding: utf-8 -*-
from blockdiag.noderenderer import NodeShape
from blockdiag.noderenderer import install_renderer
from blockdiag.utils.XY import XY
from blockdiag.SVGdraw import pathdata


class Terminator(NodeShape):
    def render_shape(self, drawer, format, **kwargs):
        font = kwargs.get('font')
        fill = kwargs.get('fill')

        m = self.metrix.cell(self.node)
        r = self.metrix.cellSize * 2
        textbox = (m.topLeft().x + r, m.topLeft().y,
                   m.bottomRight().x - r, m.bottomRight().y)

        # draw background
        self.render_shape_background(drawer, format, **kwargs)

        # draw outline
        box = self.metrix.cell(self.node).box()
        if not kwargs.get('shadow') and self.node.background:
            drawer.loadImage(self.node.background, textbox)

        # draw label
        if not kwargs.get('shadow'):
            drawer.textarea(textbox, self.node.label, fill=fill,
                            font=font, fontsize=self.metrix.fontSize,
                            lineSpacing=self.metrix.lineSpacing)

    def render_shape_background(self, drawer, format, **kwargs):
        outline = kwargs.get('outline')
        fill = kwargs.get('fill')

        m = self.metrix.cell(self.node)
        r = self.metrix.cellSize * 2

        box = m.box()
        ellipses = [(box[0], box[1], box[0] + r * 2, box[3]),
                    (box[2] - r * 2, box[1], box[2], box[3])]

        for e in ellipses:
            if kwargs.get('shadow'):
                e = self.shift_shadow(e)
                drawer.ellipse(e, fill=fill, outline=fill,
                               filter='transp-blur')
            else:
                drawer.ellipse(e, fill=self.node.color, outline=fill,
                               style=self.node.style)

        rect = (box[0] + r, box[1], box[2] - r, box[3])
        if kwargs.get('shadow'):
            rect = self.shift_shadow(rect)
            drawer.rectangle(rect, fill=fill, outline=fill,
                             filter='transp-blur')
        else:
            drawer.rectangle(rect, fill=self.node.color,
                             outline=self.node.color)

        lines = [(XY(box[0] + r, box[1]), XY(box[2] - r, box[1])),
                 (XY(box[0] + r, box[3]), XY(box[2] - r, box[3]))]
        for line in lines:
            if not kwargs.get('shadow'):
                drawer.line(line, fill=outline, style=self.node.style)

    def render_vector_shape(self, drawer, format, **kwargs):
        outline = kwargs.get('outline')
        font = kwargs.get('font')
        fill = kwargs.get('fill')

        # create pathdata
        m = self.metrix.cell(self.node)
        r = self.metrix.cellSize * 2
        height = self.metrix.nodeHeight

        box = (m.topLeft().x + r, m.topLeft().y,
               m.bottomRight().x - r, m.bottomRight().y)
        if kwargs.get('shadow'):
            box = self.shift_shadow(box)

        path = pathdata(box[0], box[1])
        path.line(box[2], box[1])
        path.ellarc(r, height / 2, 0, 0, 1, box[2], box[3])
        path.line(box[0], box[3])
        path.ellarc(r, height / 2, 0, 0, 1, box[0], box[1])

        textbox = (m.topLeft().x + r, m.topLeft().y,
                   m.bottomRight().x - r, m.bottomRight().y)

        # draw outline
        if kwargs.get('shadow'):
            drawer.path(path, fill=fill, outline=fill,
                        filter='transp-blur')
        elif self.node.background:
            drawer.path(path, fill=self.node.color, outline=self.node.color)
            drawer.loadImage(self.node.background, textbox)
            drawer.path(path, fill="none", outline=fill,
                        style=self.node.style)
        else:
            drawer.path(path, fill=self.node.color, outline=fill,
                        style=self.node.style)

        # draw label
        if not kwargs.get('shadow'):
            drawer.textarea(textbox, self.node.label, fill=fill,
                            font=font, fontsize=self.metrix.fontSize,
                            lineSpacing=self.metrix.lineSpacing)


def setup(self):
    install_renderer('flowchart.terminator', Terminator)
