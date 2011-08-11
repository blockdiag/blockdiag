# -*- coding: utf-8 -*-
#  Copyright 2011 Takeshi KOMIYA
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import pkg_resources
from blockdiag.utils.XY import XY
from blockdiag.utils import images

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
        self.textalign = 'center'
        self.connectors = [m.top(), m.right(), m.bottom(), m.left()]

        if node.icon is None:
            self.iconbox = None
            self.textbox = m.box()
        else:
            image_size = images.get_image_size(node.icon)
            if image_size is None:
                iconsize = (0, 0)
            else:
                boundedbox = [metrix.nodeWidth / 2, metrix.nodeHeight]
                iconsize = images.calc_image_size(image_size, boundedbox)

            vmargin = (metrix.nodeHeight - iconsize[1]) / 2
            self.iconbox = (m.topLeft().x,
                            m.topLeft().y + vmargin,
                            m.topLeft().x + iconsize[0],
                            m.topLeft().y + vmargin + iconsize[1])

            self.textbox = (self.iconbox[2], m.top().y,
                            m.bottomRight().x, m.bottomRight().y)

    def render(self, drawer, format, **kwargs):
        if self.node.stacked and not kwargs.get('stacked'):
            node = self.node.duplicate()
            node.label = ""
            node.background = ""
            for i in range(2, 0, -1):
                r = self.metrix.cellSize / 2 * i
                metrix = self.metrix.shiftedMetrix(r, 0, 0, r)

                self.__class__(node, metrix).render(drawer, format,
                                                    stacked=True, **kwargs)

        if hasattr(self, 'render_vector_shape') and format == 'SVG':
            self.render_vector_shape(drawer, format, **kwargs)
        else:
            self.render_shape(drawer, format, **kwargs)

        self.render_icon(drawer, **kwargs)
        self.render_label(drawer, **kwargs)
        self.render_number_badge(drawer, **kwargs)

    def render_icon(self, drawer, **kwargs):
        if self.node.icon != None and kwargs.get('shadow') != True:
            drawer.loadImage(self.node.icon, self.iconbox)

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
            r = self.metrix.cellSize * 3 / 2

            box = (xy.x - r, xy.y - r, xy.x + r, xy.y + r)
            drawer.ellipse(box, outline=fill, fill=badgeFill)
            drawer.textarea(box, self.node.numbered, fill=fill,
                            font=font, fontsize=self.metrix.fontSize)

    def top(self):
        return self.connectors[0]

    def left(self):
        return self.connectors[3]

    def right(self):
        point = self.connectors[1]
        if self.node.stacked:
            point = XY(point.x + self.metrix.cellSize, point.y)
        return point

    def bottom(self):
        point = self.connectors[2]
        if self.node.stacked:
            point = XY(point.x, point.y + self.metrix.cellSize)
        return point

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
