# -*- coding: utf-8 -*-
import pkg_resources
from blockdiag.utils.XY import XY

renderers = {}
searchpath = []


def init_renderers():
    for plugin in pkg_resources.iter_entry_points('blockdiag_noderenderer'):
        module = plugin.load()
        if hasattr(module, 'setup'):
            module.setup(module)


def install_renderer(name, renderer):
    renderers[name] = renderer


def set_default_namespace(path):
    searchpath[:] = []
    for path in path.split(','):
        searchpath.append(path)


def get(shape):
    if not renderers:
        init_renderers()

    for path in searchpath:
        name = "%s.%s" % (path, shape)
        if name in renderers:
            return renderers[name]

    return renderers[shape]


class NodeShape(object):
    def __init__(self, node, metrix=None):
        self.node = node
        self.metrix = metrix

        m = self.metrix.cell(self.node)
        self.textbox = m.box()
        self.textalign = 'center'
        self.connectors = [m.top(), m.right(), m.bottom(), m.left()]

    def render(self, drawer, format, **kwargs):
        if hasattr(self, 'render_vector_shape') and format == 'SVG':
            self.render_vector_shape(drawer, format, **kwargs)
        else:
            self.render_shape(drawer, format, **kwargs)

        self.render_label(drawer, **kwargs)
        self.render_number_badge(drawer, **kwargs)

    def render_shape(self, drawer, format, **kwargs):
        pass

    def render_label(self, drawer, **kwargs):
        font = kwargs.get('font')
        fill = kwargs.get('fill')

        if not kwargs.get('shadow'):
            drawer.textarea(self.textbox, self.node.label,
                            fill=fill, halign=self.textalign,
                            font=font, fontsize=self.metrix.fontSize,
                            lineSpacing=self.metrix.lineSpacing)

    def render_number_badge(self, drawer, **kwargs):
        if self.node.numbered != None and kwargs.get('shadow') != True:
            font = kwargs.get('font')
            fill = kwargs.get('fill')
            badgeFill = kwargs.get('badgeFill')

            xy = self.metrix.cell(self.node).topLeft()
            r = self.metrix.cellSize

            box = (xy.x - r, xy.y - r, xy.x + r, xy.y + r)
            drawer.ellipse(box, outline=fill, fill=badgeFill)
            drawer.textarea(box, self.node.numbered, fill=fill,
                            font=font, fontsize=self.metrix.fontSize)

    def top(self):
        return self.connectors[0]

    def left(self):
        return self.connectors[3]

    def right(self):
        return self.connectors[1]

    def bottom(self):
        return self.connectors[2]

    def shift_shadow(self, value):
        xdiff = self.metrix.shadowOffsetX
        ydiff = self.metrix.shadowOffsetY

        if isinstance(value, XY):
            ret = XY(value.x + xdiff, value.y + ydiff)
        elif isinstance(value, (list, tuple)):
            if isinstance(value[0], (XY, list)):
                ret = [self.shift_shadow(x) for x in value]
            else:
                ret = []
                for i, x in enumerate(value):
                    if i % 2 == 0:
                        ret.append(x + xdiff)
                    else:
                        ret.append(x + ydiff)

        return ret
