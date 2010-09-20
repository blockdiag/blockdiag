#!/usr/bin/python
# -*- encoding: utf-8 -*-

import Image
import ImageFont
import ImageDraw


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


class NodeMetrix:
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

    def nodeCoreBox(self, xy):
        xy = self.topLeft(xy)
        return (xy[0] + self.nodePadding,
                xy[1] + self.nodePadding,
                xy[0] + self.nodeWidth - self.nodePadding * 2,
                xy[1] + self.nodeHeight - self.nodePadding * 2)

    def topLeft(self, xy):
        x = self.pageMargin + xy[0] * (self.nodeWidth + self.spanWidth)
        y = self.pageMargin + xy[1] * (self.nodeHeight + self.spanHeight)

        return (x, y)

    def topCenter(self, xy):
        x, y = self.topLeft(xy)
        return (x + self.nodeWidth / 2, y)

    def topRight(self, xy):
        x, y = self.topLeft(xy)
        return (x + self.nodeWidth, y)

    def bottomLeft(self, xy):
        x, y = self.topLeft(xy)
        return (x, y + self.nodeHeight)

    def bottomCenter(self, xy):
        x, y = self.topLeft(xy)
        return (x + self.nodeWidth / 2, y + self.nodeHeight)

    def bottomRight(self, xy):
        x, y = self.topLeft(xy)
        return (x + self.nodeWidth, y + self.nodeHeight)

    def leftCenter(self, xy):
        x, y = self.topLeft(xy)
        return (x, y + self.nodeHeight / 2)

    def rightCenter(self, xy):
        x, y = self.topLeft(xy)
        return (x + self.nodeWidth, y + self.nodeHeight / 2)

    def pageSize(self, nodelist):
        x = 0
        y = 0
        for node in nodelist:
            if x <= node.xy[0]:
                x = node.xy[0]
            if y <= node.xy[1]:
                y = node.xy[1]

        x, y = self.bottomRight((x, y))
        return (x + self.pageMargin, y + self.pageMargin)


class DiagramDraw(ImageDraw.ImageDraw):
    def __init__(self, im, mode=None, **kwargs):
        self.image = im
        self.metrix = NodeMetrix(**kwargs)
        self.lineSpacing = kwargs.get('lineSpacing', 2)
        self.fill = kwargs.get('fill', (0, 0, 0))

        ImageDraw.ImageDraw.__init__(self, im, mode)

    def getPaperSize(self, root):
        return self.metrix.pageSize(root)

    def screennode(self, node, **kwargs):
        ttfont = kwargs.get('font')

        top_left = self.metrix.topLeft(node.xy)
        bottom_right = self.metrix.bottomRight(node.xy)
        if node.color:
            self.rectangle([top_left, bottom_right], outline=self.fill, fill=node.color)
        else:
            self.rectangle([top_left, bottom_right], outline=self.fill)

        box = self.metrix.nodeCoreBox(node.xy)
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

        node1_xy = self.metrix.topLeft(edge.node1.xy)
        node2_xy = self.metrix.topLeft(edge.node2.xy)

        if edge.node1.xy[0] < edge.node2.xy[0]:
            # draw arrow line
            node1_right = self.metrix.rightCenter(edge.node1.xy)
            node2_left = self.metrix.leftCenter(edge.node2.xy)
            node1_bottomRight = self.metrix.bottomRight(edge.node1.xy)
            node2_bottomRight = self.metrix.bottomRight(edge.node2.xy)
            lines.append(node1_right)

            if edge.node1.xy[1] != edge.node2.xy[1]:
                lines.append((node1_right[0] + spanWidth / 2, node1_right[1]))
                lines.append((node1_right[0] + spanWidth / 2, node2_left[1]))
                lines.append((node2_left[0] - spanWidth / 2, node2_left[1]))
            elif edge.node1.xy[0] + 1 < edge.node2.xy[0]:
                lines.append((node1_right[0] + spanWidth / 2, node1_right[1]))
                lines.append((node1_right[0] + spanWidth / 2,
                              node1_bottomRight[1] + spanHeight / 2))
                lines.append((node2_left[0] - spanWidth / 2,
                              node2_bottomRight[1] + spanHeight / 2))
                lines.append((node2_left[0] - spanWidth / 2, node2_left[1]))

            lines.append(node2_left)

            # draw arrow head
            head.append(node2_left)
            head.append((node2_left[0] - cellSize,
                         node2_left[1] - cellSize / 2))
            head.append((node2_left[0] - cellSize,
                         node2_left[1] + cellSize / 2))
        elif edge.node1.xy[0] == edge.node2.xy[0] and edge.node1.xy[1] > edge.node2.xy[1]:
            # draw arrow line
            node1_top = self.metrix.topCenter(node1.xy)
            node2_bottom = self.metrix.bottomCenter(node2.xy)

            lines.append(node1_top)
            lines.append(node2_bottom)

            # draw arrow head
            head.append(node2_bottom)
            head.append((node2_bottom[0] - cellSize / 2,
                         node2_bottom[1] + cellSize))
            head.append((node2_bottom[0] + cellSize / 2,
                         node2_bottom[1] + cellSize))
        elif edge.node1.xy[1] >= edge.node2.xy[1]:
            # draw arrow line
            node1_right = self.metrix.rightCenter(edge.node1.xy)
            node2_top = self.metrix.topCenter(edge.node2.xy)

            lines.append(node1_right)
            lines.append((node1_right[0] + spanWidth / 8, node1_right[1]))
            lines.append((node1_right[0] + spanWidth / 8,
                          node2_top[1] - spanHeight / 2))
            lines.append((node2_top[0], node2_top[1] - spanHeight / 2))

            lines.append(node2_top)

            # draw arrow head
            head.append(node2_top)
            head.append((node2_top[0] - cellSize / 2,
                         node2_top[1] - cellSize))
            head.append((node2_top[0] + cellSize / 2,
                         node2_top[1] - cellSize))
        else:
            pos = node1_xy + node2_xy
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
