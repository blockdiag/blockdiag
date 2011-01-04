#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import re
import sys
import uuid
from utils.XY import XY


def unquote(string):
    if string:
        return re.sub('(\A"|"\Z)', '', string, re.M)
    else:
        return string


class Element:
    basecolor = (255, 255, 255)
    namespace = {}

    @classmethod
    def get(self, id):
        if not id:
            id = uuid.uuid1()

        if id not in self.namespace:
            obj = self(id)
            self.namespace[id] = obj

        return self.namespace[id]

    @classmethod
    def clear(self):
        self.namespace = {}

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

    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False
        elif isinstance(other, str):
            return self.id == other
        else:
            return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        class_name = self.__class__.__name__
        nodeid = self.id
        xy = str(self.xy)
        width = self.width
        height = self.height
        addr = id(self)

        format = "<%(class_name)s '%(nodeid)s' %(xy)s %(width)dx%(height)d at 0x%(addr)08x>"
        return format % locals()


class DiagramNode(Element):
    basecolor = (255, 255, 255)

    def __init__(self, id):
        Element.__init__(self, id)

        self.label = unquote(id) or ''
        self.style = None
        self.numbered = None
        self.background = None
        self.description = None
        self.drawable = True

    def copyAttributes(self, other):
        if other.xy:
            self.xy = other.xy
        if other.label and other.id != other.label:
            self.label = other.label
        if other.color and other.color != self.__class__.basecolor:
            self.color = other.color
        if other.style:
            self.style = other.style
        if other.numbered:
            self.numbered = other.numbered
        if other.background:
            self.background = other.background
        if other.description:
            self.description = other.description
        if other.width:
            self.width = other.width
        if other.height:
            self.height = other.height

    def setAttributes(self, attrs):
        for attr in attrs:
            value = unquote(attr.value)

            if attr.name == 'label':
                self.label = value
            elif attr.name == 'color':
                self.color = value
            elif attr.name == 'style':
                style = value.lower()
                if style in ('solid', 'dotted', 'dashed'):
                    self.style = style
                else:
                    msg = "WARNING: unknown edge style: %s\n" % style
                    sys.stderr.write(msg)
            elif attr.name == 'numbered':
                self.numbered = value
            elif attr.name == 'background':
                if os.path.isfile(value):
                    self.background = value
                else:
                    msg = "WARNING: background image not found: %s\n" % value
                    sys.stderr.write(msg)
            elif attr.name == 'description':
                self.description = value
            elif attr.name == 'width':
                self.width = int(value)
            elif attr.name == 'height':
                self.height = int(value)
            else:
                msg = "Unknown node attribute: %s.%s" % (self.id, attr.name)
                raise AttributeError(msg)


class NodeGroup(Element):
    basecolor = (243, 152, 0)

    def __init__(self, id):
        Element.__init__(self, id)

        self.href = None
        self.separated = False
        self.nodes = []
        self.edges = []

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

    def fixiate(self, fixiate_only_groups=False):
        if self.separated:
            self.width = 1
            self.height = 1

            return
        elif len(self.nodes) > 0:
            self.width = max(x.xy.x + x.width for x in self.nodes)
            self.height = max(x.xy.y + x.height for x in self.nodes)

        for node in self.nodes:
            if node.group and fixiate_only_groups == False:
                node.xy = XY(self.xy.x + node.xy.x,
                             self.xy.y + node.xy.y)

            if isinstance(node, NodeGroup):
                node.fixiate(fixiate_only_groups)

    def copyAttributes(self, other):
        if other.xy:
            self.xy = other.xy
        if other.width:
            self.width = other.width
        if other.height:
            self.height = other.height
        if other.label:
            self.label = other.label
        if other.color and other.color != self.__class__.basecolor:
            self.color = other.color
        if other.separated:
            self.separated = other.separated
        if other.nodes:
            self.nodes = other.nodes
        if other.edges:
            self.edges = other.edges

    def setAttributes(self, attrs):
        for attr in attrs:
            value = unquote(attr.value)

            if attr.name == 'label':
                self.label = value
            elif attr.name == 'color':
                self.color = value
            else:
                msg = "Unknown group attribute: group.%s" % attr.name
                raise AttributeError(msg)

    def isOwned(self, node):
        for n in self.traverse_nodes():
            if node == n:
                return True

        return False


class Diagram(NodeGroup):
    def __init__(self):
        NodeGroup.__init__(self, None)

        self.node_width = None
        self.node_height = None
        self.span_width = None
        self.span_height = None
        self.fontsize = None

    def fixiate(self, fixiate_only_groups=False):
        if len(self.nodes) > 0:
            self.width = max(x.xy.x + x.width for x in self.nodes)
            self.height = max(x.xy.y + x.height for x in self.nodes)
        else:
            self.width = 1
            self.height = 1

        for node in self.nodes:
            if isinstance(node, NodeGroup):
                node.fixiate(fixiate_only_groups)

    def setAttributes(self, attrs):
        for attr in attrs:
            value = unquote(attr.value)

            if attr.name == 'node_width':
                self.node_width = int(value)
            elif attr.name == 'node_height':
                self.node_height = int(value)
            elif attr.name == 'span_width':
                self.span_width = int(value)
            elif attr.name == 'span_height':
                self.span_height = int(value)
            elif attr.name == 'fontsize':
                self.fontsize = int(value)
            else:
                msg = "Unknown node attribute: diagram.%s" % attr.name
                raise AttributeError(msg)


class DiagramEdge:
    namespace = {}

    @classmethod
    def get(self, node1, node2):
        if node1 not in self.namespace:
            self.namespace[node1] = {}

        if node2 not in self.namespace[node1]:
            obj = self(node1, node2)
            self.namespace[node1][node2] = obj

        return self.namespace[node1][node2]

    @classmethod
    def find(self, node1, node2=None):
        if node1 not in self.namespace:
            return []

        if node2 is None:
            return self.namespace[node1].values()

        if node2 not in self.namespace[node1]:
            return []

        return self.namespace[node1][node2]

    @classmethod
    def clear(self):
        self.namespace = {}

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

    def copyAttributes(self, other):
        if other.label:
            self.label = other.label
        if other.dir and other.dir != 'forward':
            self.dir = other.dir
        if other.color:
            self.color = other.color
        if other.style:
            self.style = other.style
        if other.folded:
            self.folded = other.folded

    def setAttributes(self, attrs):
        for attr in attrs:
            value = unquote(attr.value)

            if attr.name == 'label':
                self.label = value
            elif attr.name == 'dir':
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
            elif attr.name == 'color':
                self.color = value
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
            elif attr.name == 'noweight':
                msg = "WARNING: edge.noweight is obsoleted, " + \
                      "use edge.folded or edge.nofolded\n"
                sys.stderr.write(msg)

                if value.lower() == 'none':
                    self.folded = False
                else:
                    self.folded = True
            else:
                raise AttributeError("Unknown edge attribute: %s" % attr.name)
