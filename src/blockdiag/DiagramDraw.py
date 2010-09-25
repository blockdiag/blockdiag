#!/usr/bin/python
# -*- encoding: utf-8 -*-

import Image
import ImageFont
import ImageDraw
import ImageFilter

try:
    from collections import namedtuple
except ImportError:
    from utils.namedtuple import namedtuple


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
        self.pageMargin = kwargs.get('pageMargin', 3)
        self.nodePadding = kwargs.get('nodePadding', 4)
        self.nodeColumns = kwargs.get('nodeColumns', 16)
        self.nodeRows = kwargs.get('nodeRows', 5)
        self.spanColumns = kwargs.get('spanColumns', 8)
        self.spanRows = kwargs.get('spanRows', 5)

        self.pageMargin = self.cellSize * self.pageMargin
        self.nodeWidth = self.cellSize * self.nodeColumns
        self.nodeHeight = self.cellSize * self.nodeRows
        self.spanWidth = self.cellSize * self.spanColumns
        self.spanHeight = self.cellSize * self.spanRows

    def node(self, node):
        return NodeMetrix(node, self)

    def group(self, group):
        return GroupMetrix(group, self)

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
    top = topCenter
    bottom = bottomCenter
    right = rightCenter
    left = leftCenter


class GroupMetrix:
    def __init__(self, group, metrix):
        self.metrix = metrix
        self.width = group.width
        self.height = group.height

        if group:
            (self.x, self.y) = self._topLeft(group.xy[0], group.xy[1], metrix)

    @classmethod
    def _topLeft(klass, x, y, m):
        x = m.pageMargin + x * (m.nodeWidth + m.spanWidth) - m.spanWidth / 8
        y = m.pageMargin + y * (m.nodeHeight + m.spanHeight) - m.spanHeight / 4

        return XY(x, y)

    def topLeft(self):
        return XY(self.x, self.y)

    def bottomRight(self):
        m = self.metrix
        x, y = self.topLeft()
        x += self.width * m.nodeWidth + (self.width - 0.75) * m.spanWidth
        y += self.height * m.nodeHeight + (self.height - 0.5) * m.spanHeight
        return XY(x, y)


class xylist(list):
    def add(self, x, y=None):
        if y is None:
            self.append(x)
        else:
            self.append(XY(x, y))


class DiagramDraw(object):
    def __init__(self, mode=None, **kwargs):
        self.mode = None
        self.image = None
        self.imageDraw = None
        self.metrix = DiagramMetrix(**kwargs)
        self.lineSpacing = kwargs.get('lineSpacing', 2)
        self.fill = kwargs.get('fill', (0, 0, 0))
        self.defaultFill = kwargs.get('defaultFill', (255, 255, 255))
        self.group = kwargs.get('group', (243, 152, 0))
        self.shadow = kwargs.get('shadow', (128, 128, 128))
        self.shadowOffsetY = kwargs.get('shadowOffsetY', 6)
        self.shadowOffsetX = kwargs.get('shadowOffsetX', 3)

    def getPaperSize(self, root):
        return self.metrix.pageSize(root)

    def screennode(self, node, **kwargs):
        ttfont = kwargs.get('font')

        metrix = self.metrix.node(node)
        box = [metrix.topLeft(), metrix.bottomRight()]
        if node.color:
            self.imageDraw.rectangle(box, outline=self.fill,
                                     fill=node.color)
        else:
            self.imageDraw.rectangle(box, outline=self.fill,
                                     fill=self.defaultFill)

        box = self.metrix.node(node).coreBox()
        draw = FoldedTextDraw(self.image)
        draw.text(box, node.label, font=ttfont, lineSpacing=self.lineSpacing)

    def dropshadow(self, node, **kwargs):
        metrix = self.metrix.node(node)

        def shift(original):
            return XY(original.x + self.shadowOffsetX,
                      original.y + self.shadowOffsetY)
        box = [shift(metrix.topLeft()), shift(metrix.bottomRight())]
        self.imageDraw.rectangle(box, fill=self.shadow)

    def screennodelist(self, nodelist, **kwargs):
        self.image = Image.new(
            'RGB', self.getPaperSize(nodelist), (256, 256, 256))
        self.imageDraw = ImageDraw.ImageDraw(self.image, self.mode)

        for node in (x for x in nodelist if x.drawable == 0):  # == ScreenGroup
            metrix = self.metrix.group(node)
            box = [metrix.topLeft(), metrix.bottomRight()]
            self.imageDraw.rectangle(box, fill=self.group)

        for node in (x for x in nodelist if x.drawable):
            self.dropshadow(node, **kwargs)
        for i in range(15):
            self.image = self.image.filter(ImageFilter.SMOOTH_MORE)

        self.imageDraw = ImageDraw.ImageDraw(self.image, self.mode)
        for node in (x for x in nodelist if x.drawable):
            self.screennode(node, **kwargs)

    def arrow_head(self, xy, direct, **kwargs):
        head = xylist(xy)
        cell = self.metrix.cellSize

        if direct == 'up':
            head.add(xy.x - cell / 2, xy.y + cell)
            head.add(xy.x + cell / 2, xy.y + cell)
        elif direct == 'down':
            head.add(xy.x - cell / 2, xy.y - cell)
            head.add(xy.x + cell / 2, xy.y - cell)
        elif direct == 'right':
            head.add(xy.x - cell, xy.y - cell / 2)
            head.add(xy.x - cell, xy.y + cell / 2)
        elif direct == 'left':
            head.add(xy.x + cell, xy.y - cell / 2)
            head.add(xy.x + cell, xy.y + cell / 2)

        if kwargs.get('color'):
            color = kwargs.get('color')
        else:
            color = self.fill

        self.imageDraw.polygon(head, outline=color, fill=color)

    def edge(self, edge):
        lines = xylist()
        head = xylist()
        span = XY(self.metrix.spanWidth, self.metrix.spanHeight)

        node1 = self.metrix.node(edge.node1)
        node2 = self.metrix.node(edge.node2)

        if node1.x < node2.x and node1.y == node2.y:  # right, right(skipped)
            # draw arrow line
            lines.add(node1.right())

            if edge.node1.xy[0] + 1 < edge.node2.xy[0]:
                lines.add(node1.right().x + span.x / 2, node1.right().y)
                lines.add(node1.right().x + span.x / 2,
                          node1.bottomRight().y + span.y / 2)
                lines.add(node2.left().x - span.x / 4,
                          node2.bottomRight().y + span.y / 2)
                lines.add(node2.left().x - span.x / 4, node2.left().y)

            lines.add(node2.left())

            # draw arrow head
            if edge.dir in ('back', 'both'):
                self.arrow_head(node1.right(), 'left', color=edge.color)
            if edge.dir in ('forward', 'both'):
                self.arrow_head(node2.left(), 'right', color=edge.color)

        elif node1.x < node2.x:  # right-up, right-down
            # draw arrow line
            lines.add(node1.right())
            lines.add(node1.right().x + span.x / 2, node1.right().y)
            lines.add(node1.right().x + span.x / 2, node1.right().y)
            lines.add(node1.right().x + span.x / 2, node2.left().y)
            lines.add(node2.left().x - span.x / 2, node2.left().y)
            lines.add(node2.left())

            # draw arrow head
            if edge.dir in ('back', 'both'):
                self.arrow_head(node1.right(), 'left', color=edge.color)
            if edge.dir in ('forward', 'both'):
                self.arrow_head(node2.left(), 'right', color=edge.color)

        elif node1.x == node2.x and node1.y > node2.y:  # up
            # draw arrow line
            lines.add(node1.top())
            lines.add(node2.bottom())

            # draw arrow head
            if edge.dir in ('back', 'both'):
                self.arrow_head(node1.top(), 'down', color=edge.color)
            if edge.dir in ('forward', 'both'):
                self.arrow_head(node2.bottom(), 'up', color=edge.color)

        elif node1.y >= node2.y:  # left, left-up
            # draw arrow line
            lines.add(node1.right())
            lines.add(node1.right().x + span.x / 8, node1.right().y)
            lines.add(node1.right().x + span.x / 8, node2.top().y - span.y / 2)
            lines.add(node2.top().x, node2.top().y - span.y / 2)
            lines.add(node2.top())

            # draw arrow head
            if edge.dir in ('back', 'both'):
                self.arrow_head(node1.right(), 'left', color=edge.color)
            if edge.dir in ('forward', 'both'):
                self.arrow_head(node2.top(), 'down', color=edge.color)

        elif node1.x > node2.x:  # left-down
            # draw arrow line
            lines.add(node1.bottom())
            lines.add(node1.bottom().x, node2.top().y - span.y / 2)
            lines.add(node2.top().x, node2.top().y - span.y / 2)
            lines.add(node2.top())

            # draw arrow head
            if edge.dir in ('back', 'both'):
                self.arrow_head(node1.bottom(), 'up', color=edge.color)
            if edge.dir in ('forward', 'both'):
                self.arrow_head(node2.top(), 'down', color=edge.color)

        else:  # down and misc.
            pos = (node1.x, node1.y, node2.x, node2.y)
            raise RuntimeError("Invalid edge: (%d, %d), (%d, %d)" % pos)

        if edge.color:
            color = edge.color
        else:
            color = self.fill

        self.imageDraw.line(lines, fill=color)

    def edgelist(self, edgelist, **kwargs):
        for edge in edgelist:
            self.edge(edge)

    def save(self, filename, format):
        self.image.save(filename, format)
