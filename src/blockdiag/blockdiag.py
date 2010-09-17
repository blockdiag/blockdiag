#!/usr/bin/python
# -*- encoding: utf-8 -*-

import sys
import re
import math
import yaml
from optparse import OptionParser
import Image, ImageFont, ImageDraw


class ImageNodeDraw(ImageDraw.ImageDraw):
    def __init__(self, im, mode=None, **kwargs):
        self.nodeColumns = kwargs.get('nodeColumns', 16)
        self.nodeRows = kwargs.get('nodeRows', 4)
        self.lineSpacing = kwargs.get('lineSpacing', 2)
        self.nodePadding = kwargs.get('nodePadding', 4)
        self.cellSize = kwargs.get('cellSize', 16)
        self.spanColumns = kwargs.get('spanColumns', 8)
        self.spanRows = kwargs.get('spanRows', 2)
        self.fill = kwargs.get('fill', (0, 0, 0))

        self.nodeWidth = self.cellSize * self.nodeColumns
        self.nodeHeight = self.cellSize * self.nodeRows
        self.spanWidth = self.cellSize * self.spanColumns
        self.spanHeight = self.cellSize * self.spanRows
        ImageDraw.ImageDraw.__init__(self, im, mode)

    def textnode(self, position, string, **kwargs):
        lines = self._getLogicalLines(string, **kwargs)
        lines = self._truncateLines(lines, **kwargs)

        height = 0
        ttfont = kwargs.get('font')
        for string in lines:
            height += self.textsize(string, font=ttfont)[1] + self.lineSpacing

        height = (self.nodeHeight - self.nodePadding - height) / 2
        xy = (position[0] + self.nodePadding, position[1] + self.nodePadding)
        for string in lines:
            size = self.textsize(string, font=ttfont)
            x = (self.nodeWidth - self.nodePadding - size[0]) / 2

            draw_xy = (xy[0] + x, xy[1] + height)
            self.text(draw_xy, string, fill=self.fill, font=ttfont)

            height += size[1] + self.lineSpacing

        bottom_left = (position[0] + self.nodeWidth,
                       position[1] + self.nodeHeight)
        self.rectangle([position, bottom_left], outline=self.fill)

    def screennode(self, node, **kwargs):
        self.textnode(node.xy, node.title, **kwargs)

        node.width = self.nodeWidth
        node.height = self.nodeHeight

        if kwargs.get('recursive') and node.children:
            node.children.xy = (node.xy[0] + node.width + self.spanWidth,
                                node.xy[1])
            self.screennodelist(node.children, **kwargs)

    def screennodelist(self, nodelist, **kwargs):
        width = 0
        height = 0

        for node in nodelist.nodes:
            node.xy = (nodelist.xy[0], nodelist.xy[1] + height)
            self.screennode(node, **kwargs)

            height += node._height() + self.spanHeight
            if width < node._width():
                width = node._width()

        nodelist.width = width
        nodelist.height = height - self.spanHeight

    def nodelink(self, node1, node2):
        lines = []
        if node1.xy[0] < node2.xy[0] and node1.xy[1] != node2.xy[1]:
            lines.append((node1.xy[0] + node1.width,
                          node1.xy[1] + node1.height / 2))
            lines.append((node1.xy[0] + node1.width + self.spanWidth / 2,
                          node1.xy[1] + node1.height / 2))
            lines.append((node2.xy[0] - self.spanWidth / 2,
                          node2.xy[1] + node2.height / 2))
            lines.append((node2.xy[0],
                          node2.xy[1] + node2.height / 2))
        else:
            lines.append((node1.xy[0] + node1.width,
                          node1.xy[1] + node1.height / 2))
            lines.append((node2.xy[0],
                          node2.xy[1] + node2.height / 2))

        self.line(lines, fill=self.fill)

    def nodelinklist(self, parent, nodelist, **kwargs):
        if parent:
            for node in nodelist.nodes:
                self.nodelink(parent, node)

        if kwargs.get('recursive'):
            for node in nodelist.nodes:
                if node.children:
                    self.nodelinklist(node, node.children, **kwargs)

    def _getLinefeedPosition(self, string, **kwargs):
        ttfont = kwargs.get('font')

        for i in range(0, len(string)):
            length = len(string) - i
            metrics = self.textsize(string[0:length], font=ttfont)

            if metrics[0] <= (self.nodeWidth - self.nodePadding * 2):
                break

        return length

    def _getLogicalLines(self, string, **kwargs):
        ttfont = kwargs.get('font')
        lines = []

        for line in string.splitlines():
            while line:
                string = string.strip()
                pos = self._getLinefeedPosition(line, **kwargs)

                lines.append(line[0:pos])
                line = line[pos:]

        return lines

    def _truncateLines(self, lines, **kwargs):
        ttfont = kwargs.get('font')
        height = 0
        truncated = 0
        truncated_lines = []

        for string in lines:
            size = self.textsize(string, font=ttfont)
            height += size[1] + self.lineSpacing

            if height < self.nodeHeight - self.nodePadding * 2:
                truncated_lines.append(string)
            else:
                truncated = 1

        if truncated:
            string = truncated_lines.pop()
            for i in range(0, len(string)):
                if i == 0:
                    truncated = string + ' ...'
                else:
                    truncated = string[0:-i] + ' ...'

                size = self.textsize(truncated, font=ttfont)
                if size[0] <= self.nodeWidth - self.nodePadding * 2:
                    truncated_lines.append(truncated)
                    break

        return truncated_lines


class ScreenNode:
    def __init__(self, title=None):
        self.title = title
        self.xy = None
        self.width = None
        self.height = None
        self.children = None

    def _height(self):
        if self.children and self.height < self.children.height:
            height = self.children.height
        else:
            height = self.height

        return height

    def _width(self):
        if self.children:
            width = self.children.xy[0] - self.xy[0] + self.children.width
        else:
            width = self.width

        return width


class ScreenNodeList:
    def __init__(self, nodes=None):
        self.nodes = nodes or []
        self.xy = None
        self.width = None
        self.height = None

    def append(self, node):
        self.nodes.append(node)


class ScreenNodeBuilder:
    @classmethod
    def build(klass, list):
        root = ScreenNodeList()
        for node in list:
            if isinstance(node, dict):
                for key in node.keys():
                    screennode = ScreenNode(key)
                    screennode.children = klass.build(node[key])

                    root.append(screennode)
            else:
                root.append(ScreenNode(node))

        return root


def main():
    usage = "usage: %prog [options] infile"
    p = OptionParser(usage=usage)
    p.add_option('-o', dest='filename',
                 help='write diagram to FILE', metavar='FILE')
    (options, args) = p.parse_args()

    if len(args) == 0:
        p.print_help()
        exit(0)

    if sys.platform.startswith('win'):
        fontpath = 'c:/windows/fonts/msmincho.ttf'
    else:
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

    paperMargin = draw.cellSize * 2
    root.xy = (paperMargin, paperMargin)
    draw.screennodelist(root, font=ttfont, recursive=1)
    draw.nodelinklist(None, root, recursive=1)

    size = (0, 0, root.width + paperMargin * 2, root.height + paperMargin * 2)
    image = imgbuff.crop(size)

    image.save(outfile, 'PNG')


if __name__ == '__main__':
    main()

