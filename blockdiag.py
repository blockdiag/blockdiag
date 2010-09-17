#!/usr/bin/python
# -*- encoding: utf-8 -*-

import re
import yaml
from optparse import OptionParser
import Image, ImageFont, ImageDraw


class FoldedTextDraw(ImageDraw.ImageDraw):
    def __init__(self, im, mode=None):
        ImageDraw.ImageDraw.__init__(self, im, mode)

    def text(self, box, string, **kwargs):
        ttfont = kwargs.get('font')
        lineSpacing = kwargs.get('lineSpacing', 2)
        size = (box[2] - box[0], box[3] - box[1])

        lines = self._getFoldedText(size, string, font=ttfont, lineSpacing=lineSpacing)

        height = 0
        for string in lines:
            height += self.textsize(string, font=ttfont)[1] + lineSpacing

        height = (size[1] - (height - lineSpacing)) / 2
        xy = (box[0], box[1])
        for string in lines:
            textsize = self.textsize(string, font=ttfont)
            x = (size[0] - textsize[0]) / 2

            draw_xy = (xy[0] + x, xy[1] + height)
            ImageDraw.ImageDraw.text(self, draw_xy, string, fill=self.fill, font=ttfont)

            height += size[1] + lineSpacing

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
        self.nodeColumns = kwargs.get('nodeColumns', 16)
        self.nodeRows = kwargs.get('nodeRows', 4)
        self.lineSpacing = kwargs.get('lineSpacing', 2)
        self.nodePadding = kwargs.get('nodePadding', 4)
        self.cellSize = kwargs.get('cellSize', 16)
        self.spanColumns = kwargs.get('spanColumns', 8)
        self.spanRows = kwargs.get('spanRows', 2)
        self.pageMargin = kwargs.get('pageMargin', 2)
        self.fill = kwargs.get('fill', (0, 0, 0))

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

    def pageSize(self, root):
        x, y = self.bottomRight((root.width() - 1, root.height() - 1))
        return (x + self.pageMargin, y + self.pageMargin)


class ImageNodeDraw(ImageDraw.ImageDraw):
    def __init__(self, im, mode=None, **kwargs):
        self.image = im
        self.metrix = NodeMetrix(**kwargs)

        self.nodeColumns = kwargs.get('nodeColumns', 16)
        self.nodeRows = kwargs.get('nodeRows', 4)
        self.lineSpacing = kwargs.get('lineSpacing', 2)
        self.nodePadding = kwargs.get('nodePadding', 4)
        self.cellSize = kwargs.get('cellSize', 16)
        self.spanColumns = kwargs.get('spanColumns', 8)
        self.spanRows = kwargs.get('spanRows', 2)
        self.pageMargin = kwargs.get('pageMargin', 2)
        self.fill = kwargs.get('fill', (0, 0, 0))

        self.pageMargin = self.cellSize * self.pageMargin
        self.nodeWidth = self.cellSize * self.nodeColumns
        self.nodeHeight = self.cellSize * self.nodeRows
        self.spanWidth = self.cellSize * self.spanColumns
        self.spanHeight = self.cellSize * self.spanRows
        ImageDraw.ImageDraw.__init__(self, im, mode)

    def getPaperSize(self, root):
        return self.metrix.pageSize(root)

    def screennode(self, node, **kwargs):
        ttfont = kwargs.get('font')

        box = self.metrix.nodeCoreBox(node.xy)
        draw = FoldedTextDraw(self.image)
        draw.text(box, node.title, font=ttfont, lineSpacing=self.lineSpacing)

        top_left = self.metrix.topLeft(node.xy)
        bottom_right = self.metrix.bottomRight(node.xy)
        self.rectangle([top_left, bottom_right], outline=self.fill)

        if kwargs.get('recursive') and node.children:
            self.screennodelist(node.children, **kwargs)

    def screennodelist(self, nodelist, **kwargs):
        for node in nodelist.nodes:
            self.screennode(node, **kwargs)

    def nodelink(self, node1, node2):
        lines = []
        head = []

        node1_xy = self.metrix.topLeft(node1.xy)
        node2_xy = self.metrix.topLeft(node2.xy)

        if node1.xy[0] < node2.xy[0]:
            # draw arrow line
            node1_right = self.metrix.rightCenter(node1.xy)
            node2_left = self.metrix.leftCenter(node2.xy)
            lines.append(node1_right)

            if node1.xy[1] != node2.xy[1]:
                lines.append((node1_right[0] + self.spanWidth / 2, node1_right[1]))
                lines.append((node2_left[0] - self.spanWidth / 2, node2_left[1]))

            lines.append(node2_left)

            # draw arrow head
            head.append(node2_left)
            head.append((node2_left[0] - self.cellSize,
                         node2_left[1] - self.cellSize / 2))
            head.append((node2_left[0] - self.cellSize,
                         node2_left[1] + self.cellSize / 2))
        else:
            raise

        self.line(lines, fill=self.fill)
        self.polygon(head, outline=self.fill, fill=self.fill)

    def nodelinklist(self, parent, nodelist, **kwargs):
        if parent:
            for node in nodelist.nodes:
                self.nodelink(parent, node)

        if kwargs.get('recursive'):
            for node in nodelist.nodes:
                if node.children:
                    self.nodelinklist(node, node.children, **kwargs)


class ScreenNode:
    def __init__(self, title=None):
        self.title = title
        self.xy = None
        self.children = None

    def width(self):
        if self.children:
            width = 1 + self.children.width()
        else:
            width = 1

        return width

    def height(self):
        if self.children:
           height = self.children.height()
        else:
           height = 1

        return height


class ScreenNodeList:
    def __init__(self, nodes=None):
        self.nodes = nodes or []
        self.xy = None

    def width(self):
        width = 1
        for node in self.nodes:
           if width < node.width():
               width = node.width()

        return width

    def height(self):
        height = 0
        for node in self.nodes:
           height += node.height()

        return height

    def append(self, node):
        self.nodes.append(node)


class ScreenNodeBuilder:
    @classmethod
    def build(klass, list):
        nodelist = klass.buildNodeList(list)
        klass.doLayout(nodelist)
        return nodelist

    @classmethod
    def buildNodeList(klass, list):
        root = ScreenNodeList()
        for node in list:
            if isinstance(node, dict):
                for key in node.keys():
                    screennode = ScreenNode(key)
                    screennode.children = klass.buildNodeList(node[key])

                    root.append(screennode)
            else:
                root.append(ScreenNode(node))

        return root

    @classmethod
    def doLayout(klass, root, x=-1, y=0):
        height = 0
        root.xy = (x + 1, y)
        for node in root.nodes:
            node.xy = (root.xy[0], root.xy[1] + height)

            if node.children:
                node.children.xy = node.xy
                klass.doLayout(node.children, node.xy[0], node.xy[1])

            height += node.height()


def main():
    usage = "usage: %prog [options] infile"
    p = OptionParser(usage=usage)
    p.add_option('-o', dest='filename',
                 help='write diagram to FILE', metavar='FILE')
    (options, args) = p.parse_args()

    if len(args) == 0:
        p.print_help()
        exit(0)

    fontpath = '/usr/share/fonts/truetype/ipafont/ipagp.ttf'
    ttfont = ImageFont.truetype(fontpath, 24)

    imgbuff = Image.new('RGB', (10240, 10240), (256, 256, 256))
    draw = ImageNodeDraw(imgbuff)

    infile = args[0]
    if options.filename:
        outfile = options.filename
    else:
        outfile = re.sub('\..*', '', infile) + '.png'

    list = yaml.load(file(infile))
    root = ScreenNodeBuilder.build(list)

    draw.screennodelist(root, font=ttfont, recursive=1)
    draw.nodelinklist(None, root, recursive=1)

    image = imgbuff.crop((0, 0) + draw.getPaperSize(root))
    image.save(outfile, 'PNG')

main()
