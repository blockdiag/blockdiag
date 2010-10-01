#!/usr/bin/python
# -*- coding: utf-8 -*-

try:
    from collections import namedtuple
except ImportError:
    from utils.namedtuple import namedtuple


XY = namedtuple('XY', 'x y')


class xylist(list):
    def add(self, x, y=None):
        if y is None:
            elem = x
        else:
            elem = XY(x, y)

        if len(self) == 0:
            self.append(elem)
        elif self[-1] != elem:
            self.append(elem)


class DiagramMetrix:
    def __init__(self, **kwargs):
        self.cellSize = kwargs.get('cellSize', 8)
        self.nodePadding = kwargs.get('nodePadding', 4)
        self.lineSpacing = kwargs.get('lineSpacing', 2)
        self.shadowOffsetY = kwargs.get('shadowOffsetY', 6)
        self.shadowOffsetX = kwargs.get('shadowOffsetX', 3)

        self.pageMargin = self.cellSize * kwargs.get('pageMargin', 3)
        self.nodeWidth = self.cellSize * kwargs.get('nodeColumns', 16)
        self.nodeHeight = self.cellSize * kwargs.get('nodeRows', 5)
        self.spanWidth = self.cellSize * kwargs.get('spanColumns', 8)
        self.spanHeight = self.cellSize * kwargs.get('spanRows', 5)

    def node(self, node):
        return NodeMetrix(node, self)

    def group(self, group):
        return NodeMetrix(group, self)

    def edge(self, edge):
        return EdgeMetrix(edge, self)

    def pageSize(self, nodelist):
        x = 0
        y = 0
        for node in nodelist:
            if x <= node.xy[0]:
                x = node.xy[0]
            if y <= node.xy[1]:
                y = node.xy[1]

        x, y = NodeMetrix.new2(x, y, self).bottomRight()
        return (x + self.pageMargin, y + self.pageMargin)


class NodeMetrix:
    @classmethod
    def new2(klass, x, y, metrix):
        o = klass(None, metrix)
        (o.x, o.y) = klass._topLeft(x, y, metrix)

        return o

    def __init__(self, node, metrix):
        self.metrix = metrix

        if node:
            self.width = node.width
            self.height = node.height
            (self.x, self.y) = self._topLeft(node.xy[0], node.xy[1], metrix)
        else:
            self.width = 1
            self.height = 1
            self.x = 0
            self.y = 0

    @classmethod
    def _topLeft(klass, x, y, metrix):
        x = metrix.pageMargin + x * (metrix.nodeWidth + metrix.spanWidth)
        y = metrix.pageMargin + y * (metrix.nodeHeight + metrix.spanHeight)

        return XY(x, y)

    def box(self):
        m = self.metrix
        topLeft = self.topLeft()
        bottomRight = self.bottomRight()

        return (topLeft.x, topLeft.y, bottomRight.x, bottomRight.y)

    def marginBox(self):
        m = self.metrix
        topLeft = self.topLeft()
        bottomRight = self.bottomRight()

        return (topLeft.x - m.spanWidth / 8,
                topLeft.y - m.spanHeight / 4,
                bottomRight.x + m.spanWidth / 4,
                bottomRight.y + m.spanHeight / 2)

    def coreBox(self):
        m = self.metrix
        topLeft = self.topLeft()
        bottomRight = self.bottomRight()

        return (topLeft.x + m.nodePadding,
                topLeft.y + m.nodePadding,
                bottomRight.x - m.nodePadding * 2,
                bottomRight.y - m.nodePadding * 2)

    def shadowBox(self):
        m = self.metrix
        topLeft = self.topLeft()
        bottomRight = self.bottomRight()

        return (topLeft.x + m.shadowOffsetX,
                topLeft.y + m.shadowOffsetY,
                bottomRight.x + m.shadowOffsetX,
                bottomRight.y + m.shadowOffsetY)

    def _nodeWidth(self):
        m = self.metrix
        return self.width * m.nodeWidth + (self.width - 1) * m.spanWidth

    def _nodeHeight(self):
        m = self.metrix
        return self.height * m.nodeHeight + (self.height - 1) * m.spanHeight

    def topLeft(self):
        return XY(self.x, self.y)

    def topCenter(self):
        x, y = self.topLeft()
        return XY(x + self._nodeWidth() / 2, y)

    def topRight(self):
        x, y = self.topLeft()
        return XY(x + self._nodeWidth(), y)

    def bottomLeft(self):
        x, y = self.topLeft()
        return XY(x, y + self._nodeHeight())

    def bottomCenter(self):
        x, y = self.topLeft()
        return XY(x + self._nodeWidth() / 2, y + self._nodeHeight())

    def bottomRight(self):
        x, y = self.topLeft()
        return XY(x + self._nodeWidth(), y + self._nodeHeight())

    def leftCenter(self):
        x, y = self.topLeft()
        return XY(x, y + self._nodeHeight() / 2)

    def rightCenter(self):
        x, y = self.topLeft()
        return XY(x + self._nodeWidth(), y + self._nodeHeight() / 2)

    # method aliases
    top = topCenter
    bottom = bottomCenter
    right = rightCenter
    left = leftCenter


class EdgeMetrix:
    def __init__(self, edge, metrix):
        self.metrix = metrix
        self.edge = edge

    def direction(self):
        node1 = self.metrix.node(self.edge.node1)
        node2 = self.metrix.node(self.edge.node2)

        if node1.x > node2.x:
            if node1.y > node2.y:
                dir = 'left-up'
            elif node1.y == node2.y:
                dir = 'left'
            else:
                dir = 'left-down'
        elif node1.x == node2.x:
            if node1.y > node2.y:
                dir = 'up'
            elif node1.y == node2.y:
                dir = 'same'
            else:
                dir = 'down'
        else:
            if node1.y > node2.y:
                dir = 'right-up'
            elif node1.y == node2.y:
                dir = 'right'
            else:
                dir = 'right-down'

        return dir

    def heads(self):
        heads = []
        dir = self.direction()

        if self.edge.dir in ('back', 'both'):
            if dir in ('left-up', 'left', 'right-up', 'right', 'right-down'):
                heads.append(self._head(self.edge.node1, 'left'))
            elif dir == 'up':
                heads.append(self._head(self.edge.node1, 'down'))
            elif dir in ('left-down'):
                heads.append(self._head(self.edge.node1, 'up'))

        if self.edge.dir in ('forward', 'both'):
            if dir in ('right-up', 'right', 'right-down'):
                heads.append(self._head(self.edge.node2, 'right'))
            elif dir == 'up':
                heads.append(self._head(self.edge.node2, 'up'))
            elif dir in ('left-up', 'left', 'left-down'):
                heads.append(self._head(self.edge.node2, 'down'))

        return heads

    def _head(self, node, direct):
        head = xylist()
        cell = self.metrix.cellSize
        node = self.metrix.node(node)

        if direct == 'up':
            xy = node.bottom()
            head.add(xy)
            head.add(xy.x - cell / 2, xy.y + cell)
            head.add(xy.x + cell / 2, xy.y + cell)
        elif direct == 'down':
            xy = node.top()
            head.add(xy)
            head.add(xy.x - cell / 2, xy.y - cell)
            head.add(xy.x + cell / 2, xy.y - cell)
        elif direct == 'right':
            xy = node.left()
            head.add(xy)
            head.add(xy.x - cell, xy.y - cell / 2)
            head.add(xy.x - cell, xy.y + cell / 2)
        elif direct == 'left':
            xy = node.right()
            head.add(xy)
            head.add(xy.x + cell, xy.y - cell / 2)
            head.add(xy.x + cell, xy.y + cell / 2)

        return head

    def shaft(self):
        span = XY(self.metrix.spanWidth, self.metrix.spanHeight)

        node1 = self.metrix.node(self.edge.node1)
        node2 = self.metrix.node(self.edge.node2)

        shaft = xylist()
        if node1.x < node2.x and node1.y == node2.y:  # right, right(skipped)
            shaft.add(node1.right())

            if self.edge.skipped:
                shaft.add(node1.right().x + span.x / 2, node1.right().y)
                shaft.add(node1.right().x + span.x / 2,
                          node1.bottomRight().y + span.y / 2)
                shaft.add(node2.left().x - span.x / 4,
                          node2.bottomRight().y + span.y / 2)
                shaft.add(node2.left().x - span.x / 4, node2.left().y)

            shaft.add(node2.left())

        elif node1.x < node2.x:  # right-up, right-down, right-down(skipped)
            shaft.add(node1.right())
            shaft.add(node1.right().x + span.x / 2, node1.right().y)

            if self.edge.skipped:
                shaft.add(node1.right().x + span.x / 2,
                          node2.topLeft().y - span.y / 2)
                shaft.add(node2.left().x - span.x / 4,
                          node2.topLeft().y - span.y / 2)
                shaft.add(node2.left().x - span.x / 4, node2.left().y)
            else:
                shaft.add(node1.right().x + span.x / 2, node2.left().y)
                shaft.add(node2.left().x - span.x / 2, node2.left().y)

            shaft.add(node2.left())

        elif node1.x == node2.x and node1.y > node2.y:  # up
            shaft.add(node1.top())
            shaft.add(node2.bottom())

        elif node1.y >= node2.y:  # left, left-up
            shaft.add(node1.right())
            shaft.add(node1.right().x + span.x / 8, node1.right().y)
            shaft.add(node1.right().x + span.x / 8, node2.top().y - span.y / 2)
            shaft.add(node2.top().x, node2.top().y - span.y / 2)
            shaft.add(node2.top())

        elif node1.x > node2.x:  # left-down
            shaft.add(node1.bottom())
            shaft.add(node1.bottom().x, node2.top().y - span.y / 2)
            shaft.add(node2.top().x, node2.top().y - span.y / 2)
            shaft.add(node2.top())

        else:  # down and misc.
            pos = (node1.x, node1.y, node2.x, node2.y)
            raise RuntimeError("Invalid edge: (%d, %d), (%d, %d)" % pos)

        return shaft
