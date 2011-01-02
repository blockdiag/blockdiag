#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import re
from utils.XY import XY


def unquote(string):
    if string:
        return re.sub('(\A"|"\Z)', '', string, re.M)
    else:
        return string


class Diagram:
    def __init__(self):
        self.separated = False
        self.nodes = []
        self.edges = []
        self.xy = None
        self.width = None
        self.height = None
        self.rankdir = None
        self.color = None
        self.label = None
        self.node_width = None
        self.node_height = None
        self.span_width = None
        self.span_height = None
        self.fontsize = None

    def traverse_nodes(self):
        for node in self.nodes:
            if isinstance(node, NodeGroup):
                for subnode in node.traverse_nodes():
                    yield subnode
                yield node
            else:
                yield node

    def fixiate(self, fixiate_only_groups=False):
        for node in self.nodes:
            if isinstance(node, NodeGroup) and not node.group:
                node.fixiate()

    def setAttributes(self, attrs):
        for attr in attrs:
            value = unquote(attr.value)

            if attr.name == 'rankdir':
                if value.upper() == 'LR':
                    self.rankdir = value.upper()
                else:
                    msg = "WARNING: unknown rankdir: %s\n" % value
                    sys.stderr.write(msg)
            elif attr.name == 'node_width':
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


class DiagramNode:
    def __init__(self, id):
        self.id = id
        self.xy = XY(0, 0)
        self.group = None
        self.drawable = 1
        self.order = 0

        if id:
            self.label = unquote(id)
        else:
            self.label = ''
        self.color = (255, 255, 255)
        self.style = None
        self.numbered = None
        self.background = None
        self.description = None
        self.width = 1
        self.height = 1

    def __eq__(self, other):
        if isinstance(other, str):
            return self.id == other
        else:
            return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def copyAttributes(self, other):
        if other.xy:
            self.xy = other.xy
        if other.label and other.id != other.label:
            self.label = other.label
        if other.color and other.color != (255, 255, 255):
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


class DiagramEdge:
    def __init__(self, node1, node2):
        self.node1 = node1
        self.node2 = node2
        self.crosspoints = []
        self.skipped = 0

        self.label = None
        self.dir = 'forward'
        self.color = None
        self.style = None
        self.noweight = None

    def copyAttributes(self, other):
        if other.label:
            self.label = other.label
        if other.dir and other.dir != 'forward':
            self.dir = other.dir
        if other.color:
            self.color = other.color
        if other.style:
            self.style = other.style
        if other.noweight:
            self.noweight = other.noweight

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
            elif attr.name == 'noweight':
                if value.lower() == 'none':
                    self.noweight = None
                else:
                    self.noweight = 1
            else:
                raise AttributeError("Unknown edge attribute: %s" % attr.name)


class NodeGroup(DiagramNode):
    def __init__(self, id):
        DiagramNode.__init__(self, id)
        self.label = ''
        self.href = None
        self.separated = False
        self.rankdir = None
        self.nodes = []
        self.edges = []
        self.color = (243, 152, 0)
        self.width = 1
        self.height = 1
        self.drawable = 0
        self.order = 0

    def __eq__(self, other):
        if isinstance(other, str):
            return self.id == other
        else:
            return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def traverse_nodes(self):
        for node in self.nodes:
            if isinstance(node, NodeGroup):
                for subnode in node.traverse_nodes():
                    yield subnode
                yield node
            else:
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
            if node.group and node.group == self and \
               fixiate_only_groups == False:
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
        if other.color and other.color != (243, 152, 0):
            self.color = other.color
        if other.separated:
            self.separated = other.separated

    def isOwned(self, node):
        for n in self.traverse_nodes():
            if node == n:
                return True

        return False
