#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import re
import sys
import copy
from utils import uuid
from utils.XY import XY


def unquote(string):
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
        if name in self.int_attrs:
            setattr(self, name, int(attr.value))
        elif hasattr(self, name) and not callable(getattr(self, name)):
            setattr(self, name, unquote(attr.value))
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

        if id not in cls.namespace:
            obj = cls(id)
            cls.namespace[id] = obj

        return cls.namespace[id]

    @classmethod
    def clear(cls):
        cls.namespace = {}

    def __init__(self, id):
        self.id = id
        self.label = ''
        self.xy = XY(0, 0)
        self.group = None
        self.drawable = False
        self.order = 0
        self.color = self.__class__.basecolor
        self.width = 1
        self.height = 1

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


class DiagramNode(Element):
    basecolor = (255, 255, 255)

    def __init__(self, id):
        super(DiagramNode, self).__init__(id)

        self.label = unquote(id) or ''
        self.style = None
        self.numbered = None
        self.background = None
        self.description = None
        self.drawable = True

    def set_attributes(self, attrs):
        for attr in attrs:
            value = unquote(attr.value)

            if attr.name == 'style':
                style = value.lower()
                if style in ('solid', 'dotted', 'dashed'):
                    self.style = style
                else:
                    msg = "WARNING: unknown edge style: %s\n" % style
                    sys.stderr.write(msg)
            elif attr.name == 'background':
                if os.path.isfile(value):
                    self.background = value
                else:
                    msg = "WARNING: background image not found: %s\n" % value
                    sys.stderr.write(msg)
            else:
                self.set_attribute(attr)


class NodeGroup(Element):
    basecolor = (243, 152, 0)

    def __init__(self, id):
        super(NodeGroup, self).__init__(id)

        self.href = None
        self.level = 0
        self.separated = False
        self.nodes = []
        self.edges = []

    def duplicate(self):
        copied = Element.duplicate(self)
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

                for subnode in node.traverse_nodes():
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


class Diagram(NodeGroup):
    int_attrs = ['width', 'height', 'fontsize',
                 'node_width', 'node_height', 'span_width', 'span_height']

    def __init__(self):
        super(Diagram, self).__init__(None)

        self.node_width = None
        self.node_height = None
        self.span_width = None
        self.span_height = None
        self.fontsize = None


class DiagramEdge(Base):
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
    def clear(cls):
        cls.namespace = {}

    def __init__(self, node1, node2):
        self.node1 = node1
        self.node2 = node2
        self.crosspoints = []
        self.skipped = 0

        self.label = None
        self.dir = 'forward'
        self.color = None
        self.style = None
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

    def set_attributes(self, attrs):
        for attr in attrs:
            value = unquote(attr.value)

            if attr.name == 'dir':
                dir = value.lower()
                if dir in ('back', 'both', 'none', 'forward'):
                    self.dir = dir
                elif dir == '->':
                    self.dir = 'forward'
                elif dir == '<-':
                    self.dir = 'back'
                elif dir == '<->':
                    self.dir = 'both'
                elif dir == '--':
                    self.dir = 'none'
                else:
                    msg = "WARNING: unknown edge dir: %s\n" % dir
                    sys.stderr.write(msg)
            elif attr.name == 'style':
                style = value.lower()
                if style in ('solid', 'dotted', 'dashed'):
                    self.style = style
                else:
                    msg = "WARNING: unknown edge style: %s\n" % style
                    sys.stderr.write(msg)
            elif attr.name == 'folded':
                self.folded = True
            elif attr.name == 'nofolded':
                self.folded = False
            else:
                self.set_attribute(attr)
