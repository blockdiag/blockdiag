#!/usr/bin/python
# -*- encoding: utf-8 -*-

import re
import sys
import math
import yaml
import Image, ImageFont, ImageDraw


class ImageNodeDraw(ImageDraw.ImageDraw):
    def __init__(self, im, mode=None, **kwargs):
        self.nodeColumns = kwargs.get('nodeColumns', 8)
        self.lineSpacing = kwargs.get('lineSpacing', 2)
        self.textMargin = kwargs.get('textMargin', 2)
        self.cellSize = kwargs.get('cellSize', 16)
        self.fill = kwargs.get('fill', (0, 0, 0))

        self.nodeWidth = self.cellSize * self.nodeColumns
        ImageDraw.ImageDraw.__init__(self, im, mode)

    def _getNodeHeight(self, height):
        margined_height = float(height + self.textMargin * 2)
        return int(math.ceil(margined_height / self.cellSize) * self.cellSize)

    def textnode(self, position, string, **kwargs):
        xy = (position[0] + self.textMargin, position[1] + self.textMargin)

        height = 0
        for line in string.splitlines():
            draw_xy = (xy[0], xy[1] + height)
            line_height = self._drawLogicalLine(draw_xy, line, **kwargs)

            height += line_height + self.lineSpacing

        node_width = self.nodeWidth
        node_height = self._getNodeHeight(height)
        bottom_left = (position[0] + node_width, position[1] + node_height)
        self.rectangle([position, bottom_left], outline=self.fill)

        return (node_width, node_height)

    def screennode(self, node, **kwargs):
        size = self.textnode(node.xy, node.title, **kwargs)

        node.width = size[0]
        node.height = size[1]

        if kwargs.get('recursive') and node.children:
            node.children.xy = (node.xy[0] + node.width + self.cellSize * 5,
                                node.xy[1])
            self.screennodelist(node.children, **kwargs)

    def screennodelist(self, nodelist, **kwargs):
        height = 0

        for node in nodelist.nodes:
            node.xy = (nodelist.xy[0], nodelist.xy[1] + height)
            self.screennode(node, **kwargs)

            height += node._height() + self.cellSize * 2

        nodelist.width = self.nodeWidth
        nodelist.height = height

    def nodelink(self, node1, node2):
        line_begin = (node1.xy[0] + node1.width,
                      node1.xy[1] + node1.height / 2)
        line_end = (node2.xy[0],
                    node2.xy[1] + node2.height / 2)

        self.line([line_begin, line_end], fill=self.fill)

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

            if metrics[0] <= (self.nodeWidth - self.textMargin * 2):
                break

        return length

    def _drawLogicalLine(self, position, string, **kwargs):
        ttfont = kwargs.get('font')
        height = 0

        while string:
            string = string.strip()
            pos = self._getLinefeedPosition(string, **kwargs)

            line = string[0:pos]
            string = string[pos:]

            draw_xy = (position[0], position[1] + height)
            self.text(draw_xy, line, fill=self.fill, font=ttfont)

            height += self.textsize(line, font=ttfont)[1] + self.lineSpacing

        return height


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
    if len(sys.argv) == 1:
        print "Usage: blockdiag.py [filename]\n"
        exit(0)

    fontpath = '/usr/share/fonts/truetype/ipafont/ipagp.ttf'
    ttfont = ImageFont.truetype(fontpath, 24)

    cellsize = 16
    image = Image.new('RGB', (1024, 1024), (256, 256, 256))
    draw = ImageNodeDraw(image, nodeColumns=12, cellSize=cellsize)


    filename = sys.argv[1]
    output = re.sub('\..*', '', filename) + '.png'

    list = yaml.load(file(filename))
    root = ScreenNodeBuilder.build(list)

    root.xy = (cellsize * 2, cellsize * 2)
    draw.screennodelist(root, font=ttfont, recursive=1)
    draw.nodelinklist(None, root, recursive=1)

    image.save(output, 'PNG')

main()
