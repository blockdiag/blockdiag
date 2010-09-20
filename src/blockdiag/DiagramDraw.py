#!/usr/bin/python
# -*- encoding: utf-8 -*-

import Image
import ImageFont
import ImageDraw
from collections import namedtuple


XY = namedtuple('XY', 'x y')

class FoldedTextDraw(ImageDraw.ImageDraw):
    def __init__(self, im, mode=None):
        ImageDraw.ImageDraw.__init__(self, im, mode)

    def text(self, box, string, **kwargs):
        ttfont = kwargs.get('font')
        lineSpacing = kwargs.get('lineSpacing', 2)
        size = (box[2] - box[0], box[3] - box[1])

        lines = self._getFoldedText(size, string,
                                    font=ttfont, lineSpacing=lineSpacing)

        height = 0
        for string in lines:
            height += self.textsize(string, font=ttfont)[1] + lineSpacing

        height = (size[1] - (height - lineSpacing)) / 2
        xy = (box[0], box[1])
        for string in lines:
            textsize = self.textsize(string, font=ttfont)
            x = (size[0] - textsize[0]) / 2

            draw_xy = (xy[0] + x, xy[1] + height)
            ImageDraw.ImageDraw.text(self, draw_xy, string,
                                     fill=self.fill, font=ttfont)

            height += textsize[1] + lineSpacing

    def _getFoldedText(self, size, string, **kwargs):
        ttfont = kwargs.get('font')
        lineSpacing = kwargs.get('lineSpacing', 2)
        lines = []

        height = 0
        truncated = 0
        for line in string.splitlines():
            while line:
                string = string.strip()
                for i in range(0, len(string)):
                    length = len(string) - i
                    metrics = self.textsize(string[0:length], font=ttfont)

                    if metrics[0] <= size[0]:
                        break

                if size[1] < height + metrics[1]:
                    truncated = 1
                    break

                lines.append(line[0:length])
                line = line[length:]

                height += metrics[1] + lineSpacing

        # truncate last line.
        if truncated:
            string = lines.pop()
            for i in range(0, len(string)):
                if i == 0:
                    truncated = string + ' ...'
                else:
                    truncated = string[0:-i] + ' ...'

                size = self.textsize(truncated, font=ttfont)
                if size[0] <= size[0]:
                    lines.append(truncated)
                    break

        return lines


class DiagramMetrix:
    def __init__(self, **kwargs):
        self.cellSize = kwargs.get('cellSize', 8)
        self.pageMargin = kwargs.get('pageMargin', 2)
        self.nodePadding = kwargs.get('nodePadding', 4)
        self.nodeColumns = kwargs.get('nodeColumns', 16)
        self.nodeRows = kwargs.get('nodeRows', 4)
        self.spanColumns = kwargs.get('spanColumns', 8)
        self.spanRows = kwargs.get('spanRows', 3)

        self.pageMargin = self.cellSize * self.pageMargin
        self.nodeWidth = self.cellSize * self.nodeColumns
        self.nodeHeight = self.cellSize * self.nodeRows
        self.spanWidth = self.cellSize * self.spanColumns
        self.spanHeight = self.cellSize * self.spanRows

    def node(self, node):
        return NodeMetrix(node, self)

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
            (self.x, self.y) = self._topLeft(node.xy[0], node.xy[1], metrix)

    @classmethod
    def _topLeft(klass, x, y, metrix):
        x = metrix.pageMargin + x * (metrix.nodeWidth + metrix.spanWidth)
        y = metrix.pageMargin + y * (metrix.nodeHeight + metrix.spanHeight)

        return XY(x, y)

    def coreBox(self):
        m = self.metrix
        x, y = self.topLeft()

        return (x + m.nodePadding,
                y + m.nodePadding,
                x + m.nodeWidth - m.nodePadding * 2,
                y + m.nodeHeight - m.nodePadding * 2)

    def topLeft(self):
        return XY(self.x, self.y)

    def topCenter(self):
        x, y = self.topLeft()
        return XY(x + self.metrix.nodeWidth / 2, y)

    def topRight(self):
        x, y = self.topLeft()
        return XY(x + self.metrix.nodeWidth, y)

    def bottomLeft(self):
        x, y = self.topLeft()
        return XY(x, y + self.metrix.nodeHeight)

    def bottomCenter(self):
        m = self.metrix
        x, y = self.topLeft()
        return XY(x + m.nodeWidth / 2, y + m.nodeHeight)

    def bottomRight(self):
        m = self.metrix
        x, y = self.topLeft()
        return XY(x + m.nodeWidth, y + m.nodeHeight)

    def leftCenter(self):
        x, y = self.topLeft()
        return XY(x, y + self.metrix.nodeHeight / 2)

    def rightCenter(self):
        m = self.metrix
        x, y = self.topLeft()
        return XY(x + m.nodeWidth, y + m.nodeHeight / 2)

    # method aliases
    top = topCenter;
    bottom = bottomCenter;
    right = rightCenter;
    left = leftCenter;


class DiagramDraw(ImageDraw.ImageDraw):
    def __init__(self, im, mode=None, **kwargs):
        self.image = im
        self.metrix = DiagramMetrix(**kwargs)
        self.lineSpacing = kwargs.get('lineSpacing', 2)
        self.fill = kwargs.get('fill', (0, 0, 0))

        ImageDraw.ImageDraw.__init__(self, im, mode)

    def getPaperSize(self, root):
        return self.metrix.pageSize(root)

    def screennode(self, node, **kwargs):
        ttfont = kwargs.get('font')

        metrix = self.metrix.node(node)
        if node.color:
            self.rectangle([metrix.topLeft(), metrix.bottomRight()], outline=self.fill, fill=node.color)
        else:
            self.rectangle([metrix.topLeft(), metrix.bottomRight()], outline=self.fill)

        box = self.metrix.node(node).coreBox()
        draw = FoldedTextDraw(self.image)
        draw.text(box, node.label, font=ttfont, lineSpacing=self.lineSpacing)

    def screennodelist(self, nodelist, **kwargs):
        for node in nodelist:
            self.screennode(node, **kwargs)

    def edge(self, edge):
        lines = []
        head = []
        cellSize = self.metrix.cellSize
        spanWidth = self.metrix.spanWidth
        spanHeight = self.metrix.spanHeight

        node1 = self.metrix.node(edge.node1)
        node2 = self.metrix.node(edge.node2)

        if node1.x < node2.x:
            # draw arrow line
            lines.append(node1.right())

            if edge.node1.xy[1] != edge.node2.xy[1]:
                lines.append((node1.right().x + spanWidth / 2, node1.right().y))
                lines.append((node1.right().x + spanWidth / 2, node1.right().y))
                lines.append((node1.right().x + spanWidth / 2, node2.left().y))
                lines.append((node2.left().x - spanWidth / 2, node2.left().y))
            elif edge.node1.xy[0] + 1 < edge.node2.xy[0]:
                lines.append((node1.right().x + spanWidth / 2, node1.right().y))
                lines.append((node1.right().x + spanWidth / 2,
                              node1.bottomRight().y + spanHeight / 2))
                lines.append((node2.left().x - spanWidth / 2,
                              node2.bottomRight().y + spanHeight / 2))
                lines.append((node2.left().x - spanWidth / 2, node2.left().y))

            lines.append(node2.left())

            # draw arrow head
            head.append(node2.left())
            head.append((node2.left().x - cellSize,
                         node2.left().y - cellSize / 2))
            head.append((node2.left().x - cellSize,
                         node2.left().y + cellSize / 2))

        elif node1.x == node2.x and node1.y > node2.y:
            # draw arrow line
            lines.append(node1.top())
            lines.append(node2.bottom())

            # draw arrow head
            head.append(node2.bottom())
            head.append((node2.bottom().x - cellSize / 2,
                         node2.bottom().y + cellSize))
            head.append((node2.bottom().x + cellSize / 2,
                         node2.bottom().y + cellSize))

        elif node1.y >= node2.y:
            # draw arrow line
            lines.append(node1.right())
            lines.append((node1.right().x + spanWidth / 8, node1.right().y))
            lines.append((node1.right().x + spanWidth / 8,
                          node2.top().y - spanHeight / 2))
            lines.append((node2.top().x, node2.top().y - spanHeight / 2))

            lines.append(node2.top())

            # draw arrow head
            head.append(node2.top())
            head.append((node2.top().x - cellSize / 2,
                         node2.top().y - cellSize))
            head.append((node2.top().x + cellSize / 2,
                         node2.top().y - cellSize))
        else:
            pos = (node1.x, node1.y, node2.x, node2.y)
            raise RuntimeError, "Invalid edge: (%d, %d), (%d, %d)" % pos

        if edge.color:
            color = edge.color
        else:
            color = self.fill

        self.line(lines, fill=color)
        self.polygon(head, outline=color, fill=color)

    def edgelist(self, edgelist, **kwargs):
        for edge in edgelist:
            self.edge(edge)
