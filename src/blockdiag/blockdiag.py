#!/usr/bin/python
# -*- encoding: utf-8 -*-

import sys
import re
from optparse import OptionParser
import Image
import ImageFont
import ImageDraw
import diagparser


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
        self.cellSize = kwargs.get('cellSize', 16)
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


class ImageNodeDraw(ImageDraw.ImageDraw):
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

        box = self.metrix.nodeCoreBox(node.xy)
        draw = FoldedTextDraw(self.image)
        draw.text(box, node.title, font=ttfont, lineSpacing=self.lineSpacing)

        top_left = self.metrix.topLeft(node.xy)
        bottom_right = self.metrix.bottomRight(node.xy)
        self.rectangle([top_left, bottom_right], outline=self.fill)

    def screennodelist(self, nodelist, **kwargs):
        for node in nodelist:
            self.screennode(node, **kwargs)

    def nodelink(self, node1, node2):
        lines = []
        head = []
        cellSize = self.metrix.cellSize
        spanWidth = self.metrix.spanWidth
        spanHeight = self.metrix.spanHeight

        node1_xy = self.metrix.topLeft(node1.xy)
        node2_xy = self.metrix.topLeft(node2.xy)

        if node1.xy[0] < node2.xy[0]:
            # draw arrow line
            node1_right = self.metrix.rightCenter(node1.xy)
            node2_left = self.metrix.leftCenter(node2.xy)
            node1_bottomRight = self.metrix.bottomRight(node1.xy)
            node2_bottomRight = self.metrix.bottomRight(node2.xy)
            lines.append(node1_right)

            if node1.xy[1] != node2.xy[1]:
                lines.append((node1_right[0] + spanWidth / 2, node1_right[1]))
                lines.append((node1_right[0] + spanWidth / 2, node2_left[1]))
                lines.append((node2_left[0] - spanWidth / 2, node2_left[1]))
            elif node1.xy[0] + 1 < node2.xy[0]:
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
        elif node1.xy[0] == node2.xy[0] and node1.xy[1] > node2.xy[1]:
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
        elif node1.xy[1] >= node2.xy[1]:
            # draw arrow line
            node1_right = self.metrix.rightCenter(node1.xy)
            node2_top = self.metrix.topCenter(node2.xy)

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
            raise

        self.line(lines, fill=self.fill)
        self.polygon(head, outline=self.fill, fill=self.fill)

    def nodelinklist(self, linklist, **kwargs):
        for link in linklist:
            self.nodelink(link[0], link[1])


class ScreenNode:
    def __init__(self, id):
        self.id = id
        self.title = re.sub('^"?(.*?)"?$', '\\1', id)
        self.xy = (0, 0)
        self.children = None

    def setAttributes(self, attrs):
        for attr in attrs:
            if attr.name == 'label':
                self.title = re.sub('^"?(.*?)"?$', '\\1', attr.value)
            else:
                raise


class ScreenEdge:
    def __init__(self, node1, node2):
        self.node1 = node1
        self.node2 = node2


class ScreenNodeBuilder:
    @classmethod
    def build(klass, tree):
        return klass()._build(tree)

    def __init__(self):
        self.uniqNodes = {}
        self.nodeOrder = []
        self.uniqLinks = {}
        self.linkForward = {}
        self.rows = 0

    def _build(self, tree):
        self.buildNodeList(tree)

        return (self.uniqNodes.values(), self.uniqLinks.keys())

    def getScreenNode(self, title, xy=(0, 0)):
        if title in self.uniqNodes:
            node = self.uniqNodes[title]
        else:
            node = ScreenNode(title)
            node.xy = xy
            self.uniqNodes[title] = node
            self.nodeOrder.append(title)

        return node

    def getScreenEdge(self, id1, id2):
        link = (self.getScreenNode(id1), self.getScreenNode(id2))

        if link in self.uniqLinks:
            edge = self.uniqLinks[link]
        else:
            edge = ScreenEdge(link[0], link[1])
            self.uniqLinks[link] = edge

            if not id1 in self.linkForward:
                self.linkForward[id1] = {}
            self.linkForward[id1][id2] = 1

        return edge

    def getChildrenIds(self, node):
        if isinstance(node, ScreenNode):
            node_id = node.id
        else:
            node_id = node

        if node_id in self.linkForward:
            children = self.linkForward[node_id].keys()
        elif node == None:
            children = self.linkForward.keys()
        else:
            children = []

        order = self.nodeOrder
        children.sort(lambda x, y: cmp(order.index(x), order.index(y)))

        return children

    def setNodeWidth(self, parent, node, drawn=[]):
        if node.id in drawn or parent == node:
            return

        node.xy = (parent.xy[0] + 1, node.xy[1])
        drawn.append(parent.id)

        if node.id in self.linkForward:
            for child_id in self.getChildrenIds(node):
                childnode = self.getScreenNode(child_id)
                self.setNodeWidth(node, childnode)

    def setNodeHeight(self, node, height, references=[]):
        node.xy = (node.xy[0], height)
        if node.id in self.linkForward:
            for child_id in self.getChildrenIds(node):
                if not child_id in references:
                    childnode = self.getScreenNode(child_id)

                    if node.xy[0] < childnode.xy[0]:
                        height = self.setNodeHeight(childnode, height, references)
                    else:
                        height += 1

                    references.append(child_id)
                else:
                    if not node.id in references:
                        height += 1
        else:
            height += 1

        return height

    def buildNodeList(self, tree):
        for stmt in tree.stmts:
            if isinstance(stmt, diagparser.Node):
                node = self.getScreenNode(stmt.id)
                node.setAttributes(stmt.attrs)
            elif isinstance(stmt, diagparser.Edge):
                while len(stmt.nodes) >= 2:
                    self.getScreenEdge(stmt.nodes.pop(0), stmt.nodes[0])
            else:
                raise

        for parent_id in self.getChildrenIds(None):
            parent = self.getScreenNode(parent_id)
            for child_id in self.getChildrenIds(parent):
                childnode = self.getScreenNode(child_id)
                self.setNodeWidth(parent, childnode)

        height = 0
        for node_id in self.nodeOrder:
            node = self.uniqNodes[node_id]
            if node.xy[0] == 0:
                height = self.setNodeHeight(node, height)


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

    tree = diagparser.parse_file(infile)
    nodelist, linklist = ScreenNodeBuilder.build(tree)

    draw.screennodelist(nodelist, font=ttfont)
    draw.nodelinklist(linklist)

    image = imgbuff.crop((0, 0) + draw.getPaperSize(nodelist))
    image.save(outfile, 'PNG')


if __name__ == '__main__':
    main()
