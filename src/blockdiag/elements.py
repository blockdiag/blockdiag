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

import os
import re
import sys
import copy
from utils.XY import XY
from utils import images, urlutil, uuid
import noderenderer


def unquote(string):
    """
    Remove quotas from string

    >>> unquote('"test"')
    'test'
    >>> unquote("'test'")
    'test'
    >>> unquote("'half quoted")
    "'half quoted"
    >>> unquote('"half quoted')
    '"half quoted'
    """
    if string:
        m = re.match('\A(?P<quote>"|\')((.|\s)*)(?P=quote)\Z', string, re.M)
        if m:
            return re.sub("\\\\" + m.group(1), m.group(1), m.group(2))
        else:
            return string
    else:
        return string


class Base(object):
    int_attrs = ['width', 'height']

    def duplicate(self):
        return copy.copy(self)

    def set_attribute(self, attr):
        name = attr.name
        value = unquote(attr.value)

        if hasattr(self, "set_%s" % name):
            getattr(self, "set_%s" % name)(value)
        elif name in self.int_attrs:
            setattr(self, name, int(value))
        elif hasattr(self, name) and not callable(getattr(self, name)):
            setattr(self, name, value)
        else:
            class_name = self.__class__.__name__
            msg = "Unknown attribute: %s.%s" % (class_name, attr.name)
            raise AttributeError(msg)

    def set_attributes(self, attrs):
        for attr in attrs:
            self.set_attribute(attr)


class Element(Base):
    basecolor = (255, 255, 255)
    namespace = {}

    @classmethod
    def get(cls, id):
        if not id:
            id = uuid.generate()

        unquote_id = unquote(id)
        if unquote_id not in cls.namespace:
            obj = cls(id)
            cls.namespace[unquote_id] = obj

        return cls.namespace[unquote_id]

    @classmethod
    def clear(cls):
        cls.namespace = {}

    def __init__(self, id):
        self.id = unquote(id)
        self.label = ''
        self.xy = XY(0, 0)
        self.group = None
        self.drawable = False
        self.order = 0
        self.color = self.basecolor
        self.width = 1
        self.height = 1
        self.stacked = False

    def __repr__(self):
        class_name = self.__class__.__name__
        nodeid = self.id
        xy = str(self.xy)
        width = self.width
        height = self.height
        addr = id(self)

        format = "<%(class_name)s '%(nodeid)s' %(xy)s " + \
                 "%(width)dx%(height)d at 0x%(addr)08x>"
        return format % locals()

    def set_color(self, color):
        self.color = images.color_to_rgb(color)


class DiagramNode(Element):
    basecolor = (255, 255, 255)
    default_shape = 'box'

    @classmethod
    def set_default_shape(cls, shape):
        cls.default_shape = shape

    @classmethod
    def set_default_color(cls, color):
        cls.basecolor = images.color_to_rgb(color)

    @classmethod
    def clear(cls):
        super(DiagramNode, cls).clear()
        cls.default_shape = 'box'
        cls.basecolor = (255, 255, 255)

    def __init__(self, id):
        super(DiagramNode, self).__init__(id)

        self.label = unquote(id) or ''
        self.shape = DiagramNode.default_shape
        self.color = DiagramNode.basecolor
        self.style = None
        self.numbered = None
        self.icon = None
        self.background = None
        self.description = None
        self.drawable = True

    def set_style(self, value):
        if value in ('solid', 'dotted', 'dashed'):
            self.style = value
        else:
            msg = "WARNING: unknown node style: %s\n" % value
            sys.stderr.write(msg)

    def set_shape(self, value):
        try:
            noderenderer.get(value)
            self.shape = value
        except:
            msg = "WARNING: unknown node shape: %s\n" % value
            raise RuntimeError(msg)

    def set_icon(self, value):
        if urlutil.isurl(value) or os.path.isfile(value):
            self.icon = value
        else:
            msg = "WARNING: icon image not found: %s\n" % value
            sys.stderr.write(msg)

    def set_background(self, value):
        if urlutil.isurl(value) or os.path.isfile(value):
            self.background = value
        else:
            msg = "WARNING: background image not found: %s\n" % value
            sys.stderr.write(msg)

    def set_stacked(self, value):
        self.stacked = True


class NodeGroup(Element):
    basecolor = (243, 152, 0)

    @classmethod
    def set_default_color(cls, color):
        cls.basecolor = images.color_to_rgb(color)

    @classmethod
    def clear(cls):
        super(NodeGroup, cls).clear()
        cls.basecolor = (243, 152, 0)

    def __init__(self, id):
        super(NodeGroup, self).__init__(id)

        self.href = None
        self.level = 0
        self.separated = False
        self.shape = 'box'
        self.color = NodeGroup.basecolor
        self.nodes = []
        self.edges = []
        self.orientation = 'landscape'

    def duplicate(self):
        copied = super(NodeGroup, self).duplicate()
        copied.nodes = []
        copied.edges = []

        return copied

    def parent(self, level=None):
        if level is None:
            return self.group
        else:
            if self.level < level:
                return None

            group = self
            while group.level != level:
                group = group.group

            return group

    def is_parent(self, other):
        parent = self.parent(other.level)
        return parent == other

    def traverse_nodes(self, preorder=False):
        for node in self.nodes:
            if isinstance(node, NodeGroup):
                if preorder:
                    yield node

                for subnode in node.traverse_nodes(preorder=preorder):
                    yield subnode

                if not preorder:
                    yield node
            else:
                yield node

    def traverse_groups(self, preorder=False):
        for node in self.traverse_nodes(preorder=preorder):
            if isinstance(node, NodeGroup):
                yield node

    def fixiate(self, fixiate_nodes=False):
        if self.separated:
            self.width = 1
            self.height = 1

            return
        elif len(self.nodes) > 0:
            self.width = max(x.xy.x + x.width for x in self.nodes)
            self.height = max(x.xy.y + x.height for x in self.nodes)

        for node in self.nodes:
            if fixiate_nodes:
                node.xy = XY(self.xy.x + node.xy.x,
                             self.xy.y + node.xy.y)

            if isinstance(node, NodeGroup):
                node.fixiate(fixiate_nodes)

    def update_order(self):
        for i, node in enumerate(self.nodes):
            node.order = i

    def set_orientation(self, value):
        value = value.lower()
        if value in ('landscape', 'portrait'):
            self.orientation = value
        else:
            msg = "WARNING: unknown diagram orientation: %s\n" % value
            sys.stderr.write(msg)


class Diagram(NodeGroup):
    linecolor = (0, 0, 0)
    int_attrs = ['width', 'height', 'fontsize',
                 'node_width', 'node_height', 'span_width', 'span_height']

    @classmethod
    def clear(cls):
        super(NodeGroup, cls).clear()
        cls.linecolor = (0, 0, 0)

    def __init__(self):
        super(Diagram, self).__init__(None)

        self.node_width = None
        self.node_height = None
        self.span_width = None
        self.span_height = None
        self.page_padding = None
        self.fontsize = None
        self.edge_layout = None

    def set_default_shape(self, value):
        try:
            noderenderer.get(value)
            DiagramNode.set_default_shape(value)
        except:
            msg = "WARNING: unknown node shape: %s\n" % value
            raise RuntimeError(msg)

    def set_default_node_color(self, color):
        color = images.color_to_rgb(color)
        DiagramNode.set_default_color(color)

    def set_default_line_color(self, color):
        self.linecolor = images.color_to_rgb(color)
        DiagramEdge.set_default_color(color)

    def set_default_group_color(self, color):
        color = images.color_to_rgb(color)
        NodeGroup.set_default_color(color)

    def set_shape_namespace(self, value):
        noderenderer.set_default_namespace(value)

    def set_edge_layout(self, value):
        value = value.lower()
        if value in ('normal', 'flowchart'):
            msg = "WARNING: edge_layout is very experimental feature!\n"
            sys.stderr.write(msg)

            self.edge_layout = value
        else:
            msg = "WARNING: unknown edge dir: %s\n" % value
            sys.stderr.write(msg)


class DiagramEdge(Base):
    basecolor = (0, 0, 0)
    namespace = {}

    @classmethod
    def get(cls, node1, node2):
        if node1 not in cls.namespace:
            cls.namespace[node1] = {}

        if node2 not in cls.namespace[node1]:
            obj = cls(node1, node2)
            cls.namespace[node1][node2] = obj

        return cls.namespace[node1][node2]

    @classmethod
    def find(cls, node1, node2=None):
        if node1 is None and node2 is None:
            return cls.find_all()
        elif isinstance(node1, NodeGroup):
            edges = cls.find(None, node2)
            edges = (e for e in edges if e.node1.group.is_parent(node1))
            return [e for e in edges if not e.node2.group.is_parent(node1)]
        elif isinstance(node2, NodeGroup):
            edges = cls.find(node1, None)
            edges = (e for e in edges if e.node2.group.is_parent(node2))
            return [e for e in edges if not e.node1.group.is_parent(node2)]
        elif node1 is None:
            return [e for e in cls.find_all() if e.node2 == node2]
        else:
            if node1 not in cls.namespace:
                return []

            if node2 is None:
                return cls.namespace[node1].values()

            if node2 not in cls.namespace[node1]:
                return []

        return cls.namespace[node1][node2]

    @classmethod
    def find_all(cls):
        for v1 in cls.namespace.values():
            for v2 in v1.values():
                yield v2

    @classmethod
    def find_by_level(cls, level):
        edges = []
        for e in cls.find_all():
            edge = e.duplicate()
            skips = 0

            if edge.node1.group.level < level:
                skips += 1
            else:
                while edge.node1.group.level != level:
                    edge.node1 = edge.node1.group

            if edge.node2.group.level < level:
                skips += 1
            else:
                while edge.node2.group.level != level:
                    edge.node2 = edge.node2.group

            if skips == 2:
                continue

            edges.append(edge)

        return edges

    @classmethod
    def set_default_color(cls, color):
        cls.basecolor = images.color_to_rgb(color)

    @classmethod
    def clear(cls):
        cls.namespace = {}
        cls.basecolor = (0, 0, 0)

    def __init__(self, node1, node2):
        self.node1 = node1
        self.node2 = node2
        self.crosspoints = []
        self.skipped = 0

        self.label = None
        self.dir = 'forward'
        self.color = DiagramEdge.basecolor
        self.style = None
        self.hstyle = None
        self.folded = None

    def __repr__(self):
        class_name = self.__class__.__name__
        node1_id = self.node1.id
        node1_xy = self.node1.xy
        node2_id = self.node2.id
        node2_xy = self.node2.xy
        addr = id(self)

        format = "<%(class_name)s '%(node1_id)s' %(node1_xy)s - " + \
                 "'%(node2_id)s' %(node2_xy)s, at 0x%(addr)08x>"
        return format % locals()

    def set_dir(self, value):
        value = value.lower()
        if value in ('back', 'both', 'none', 'forward'):
            self.dir = value
        elif value == '->':
            self.dir = 'forward'
        elif value == '<-':
            self.dir = 'back'
        elif value == '<->':
            self.dir = 'both'
        elif value == '--':
            self.dir = 'none'
        else:
            msg = "WARNING: unknown edge dir: %s\n" % value
            sys.stderr.write(msg)

    def set_color(self, color):
        self.color = images.color_to_rgb(color)

    def set_style(self, value):
        value = value.lower()
        if value in ('none', 'solid', 'dotted', 'dashed'):
            self.style = value
        else:
            msg = "WARNING: unknown edge style: %s\n" % value
            sys.stderr.write(msg)

    def set_hstyle(self, value):
        value = value.lower()
        if value in ('generalization', 'composition', 'aggregation'):
            self.hstyle = value
        else:
            msg = "WARNING: unknown edge hstyle: %s\n" % value
            sys.stderr.write(msg)

    def set_folded(self, value):
        self.folded = True

    def set_nofolded(self, value):
        self.folded = False
