# -*- coding: utf-8 -*-
from blockdiag.noderenderer import NodeShape
from blockdiag.noderenderer import install_renderer
from blockdiag.utils.XY import XY
from blockdiag.SVGdraw import pathdata


class Database(NodeShape):
    def render_shape(self, drawer, format, **kwargs):
        outline = kwargs.get('outline')
        font = kwargs.get('font')
        fill = kwargs.get('fill')

        m = self.metrix.cell(self.node)
        r = self.metrix.cellSize
        textbox = (m.topLeft().x, m.topLeft().y + r * 2,
                   m.bottomRight().x, m.bottomRight().y)

        # draw background
        self.render_shape_background(drawer, format, **kwargs)

        # draw background image
        if self.node.background:
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
        r = self.metrix.cellSize
        box = m.box()

        ellipse = (box[0], box[3] - r * 2, box[2], box[3])
        if kwargs.get('shadow'):
            ellipse = self.shift_shadow(ellipse)
            drawer.ellipse(ellipse, fill=fill, outline=fill,
                           filter='transp-blur')
        else:
            drawer.ellipse(ellipse, fill=self.node.color, outline=outline,
                           style=self.node.style)

        rect = (box[0], box[1] + r, box[2], box[3] - r)
        if kwargs.get('shadow'):
            rect = self.shift_shadow(rect)
            drawer.rectangle(rect, fill=fill, outline=fill,
                             filter='transp-blur')
        else:
            drawer.rectangle(rect, fill=self.node.color,
                             outline=self.node.color)

        ellipse = (box[0], box[1], box[2], box[1] + r * 2)
        if kwargs.get('shadow'):
            ellipse = self.shift_shadow(ellipse)
            drawer.ellipse(ellipse, fill=fill, outline=fill,
                           filter='transp-blur')
        else:
            drawer.ellipse(ellipse, fill=self.node.color, outline=outline,
                           style=self.node.style)

        # line both side
        lines = [(XY(box[0], box[1] + r), XY(box[0], box[3] - r)),
                 (XY(box[2], box[1] + r), XY(box[2], box[3] - r))]
        for line in lines:
            if not kwargs.get('shadow'):
                drawer.line(line, fill=outline, style=self.node.style)

    def render_vector_shape(self, drawer, format, **kwargs):
        outline = kwargs.get('outline')
        font = kwargs.get('font')
        fill = kwargs.get('fill')

        m = self.metrix.cell(self.node)
        r = self.metrix.cellSize
        width = self.metrix.nodeWidth
        textbox = (m.topLeft().x, m.topLeft().y + r * 2,
                   m.bottomRight().x, m.bottomRight().y)

        box = m.box()
        if kwargs.get('shadow'):
            box = self.shift_shadow(box)

        path = pathdata(box[0], box[1] + r)
        path.ellarc(width / 2, r, 0, 0, 1, box[2], box[1] + r)
        path.line(box[2], box[3] - r)
        path.ellarc(width / 2, r, 0, 0, 1, box[0], box[3] - r)
        path.line(box[0], box[1] + r)

        textbox = (m.topLeft().x, m.topLeft().y + r * 3 / 2,
                   m.bottomRight().x, m.bottomRight().y - r / 2)

        # draw outline
        if kwargs.get('shadow'):
            drawer.path(path, fill=fill, outline=fill,
                        filter='transp-blur')
        elif self.node.background:
            drawer.path(path, fill=self.node.color,
                        outline=self.node.color)
            drawer.loadImage(self.node.background, textbox)
            drawer.path(path, fill="none", outline=outline,
                        style=self.node.style)
        else:
            drawer.path(path, fill=self.node.color, outline=outline,
                        style=self.node.style)

        # draw cap of cylinder
        if not kwargs.get('shadow'):
            path = pathdata(box[2], box[1] + r)
            path.ellarc(width / 2, r, 0, 0, 1, box[0], box[1] + r)
            drawer.path(path, fill=self.node.color, outline=fill,
                        style=self.node.style)

        # draw label
        if not kwargs.get('shadow'):
            drawer.textarea(textbox, self.node.label, fill=fill,
                            font=font, fontsize=self.metrix.fontSize,
                            lineSpacing=self.metrix.lineSpacing)


def setup(self):
    install_renderer('flowchart.database', Database)
