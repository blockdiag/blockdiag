#!/usr/bin/python
# -*- encoding: utf-8 -*-

import os
import sys
import re
from optparse import OptionParser
import Image
import ImageFont
import DiagramDraw
import diagparser


class ScreenNode:
    def __init__(self, id):
        self.id = id
        self.label = re.sub('^"?(.*?)"?$', '\\1', id)
        self.xy = (0, 0)
        self.color = None
        self.children = None

    def setAttributes(self, attrs):
        for attr in attrs:
            value = re.sub('^"?(.*?)"?$', '\\1', attr.value)
            if attr.name == 'label':
                self.label = value
            elif attr.name == 'color':
                self.color = value
            else:
                msg = "Unknown node attribute: %s.%s" % (self.id, attr.name)
                raise AttributeError(msg)


class ScreenEdge:
    def __init__(self, node1, node2):
        self.node1 = node1
        self.node2 = node2
        self.color = None
        self.noweight = None
        self.dir = 'forward'

    def setAttributes(self, attrs):
        for attr in attrs:
            value = re.sub('^"?(.*?)"?$', '\\1', attr.value)
            if attr.name == 'color':
                self.color = value
            elif attr.name == 'dir':
                dir = value.lower()
                if dir in ('back', 'both', 'none'):
                    self.dir = dir
                else:
                    self.dir = 'forward'
            elif attr.name == 'noweight':
                if value.lower() == 'none':
                    self.noweight = None
                else:
                    self.noweight = 1
            else:
                raise AttributeError("Unknown edge attribute: %s" % attr.name)


class ScreenNodeBuilder:
    @classmethod
    def build(klass, tree):
        return klass()._build(tree)

    def __init__(self):
        self.uniqNodes = {}
        self.nodeOrder = []
        self.uniqLinks = {}
        self.widthRefs = []
        self.heightRefs = []
        self.rows = 0

    def _build(self, tree):
        self.buildNodeList(tree)

        return (self.uniqNodes.values(), self.uniqLinks.values())

    def getScreenNode(self, id):
        if id in self.uniqNodes:
            node = self.uniqNodes[id]
        else:
            node = ScreenNode(id)
            self.uniqNodes[id] = node
            self.nodeOrder.append(node)

        return node

    def getScreenEdge(self, id1, id2):
        link = (self.getScreenNode(id1), self.getScreenNode(id2))

        if link in self.uniqLinks:
            edge = self.uniqLinks[link]
        else:
            edge = ScreenEdge(link[0], link[1])
            self.uniqLinks[link] = edge

        return edge

    def getChildren(self, node):
        if isinstance(node, ScreenNode):
            node_id = node.id
        else:
            node_id = node

        uniq = {}
        for edge in self.uniqLinks.values():
            if edge.noweight == None:
                if node_id == None:
                    uniq[edge.node1] = 1
                elif edge.node1.id == node_id:
                    uniq[edge.node2] = 1
        children = uniq.keys()

        order = self.nodeOrder
        children.sort(lambda x, y: cmp(order.index(x), order.index(y)))

        return children

    def setNodeWidth(self, node=None):
        if isinstance(node, ScreenNode):
            node_id = node.id
        else:
            node_id = node

        if node_id in self.widthRefs:
            return

        self.widthRefs.append(node_id)
        for child in self.getChildren(node_id):
            if node_id == child.id:
                pass
            elif child.id in self.widthRefs:
                pass
            else:
                if node_id == None:
                    child.xy = (0, child.xy[1])
                else:
                    child.xy = (node.xy[0] + 1, child.xy[1])
                self.setNodeWidth(child)

    def setNodeHeight(self, node, height):
        node.xy = (node.xy[0], height)
        children = self.getChildren(node)

        if len(children) == 0:
            height += 1
        else:
            for child in children:
                if not child.id in self.heightRefs:
                    if node.xy[0] < child.xy[0]:
                        height = self.setNodeHeight(child, height)
                    else:
                        height += 1

                    self.heightRefs.append(child.id)
                else:
                    if not node.id in self.heightRefs:
                        height += 1

        return height

    def buildNodeList(self, tree):
        for stmt in tree.stmts:
            if isinstance(stmt, diagparser.Node):
                node = self.getScreenNode(stmt.id)
                node.setAttributes(stmt.attrs)
            elif isinstance(stmt, diagparser.Edge):
                while len(stmt.nodes) >= 2:
                    edge = self.getScreenEdge(stmt.nodes.pop(0), stmt.nodes[0])
                    edge.setAttributes(stmt.attrs)
            else:
                raise AttributeError("Unknown sentense: " + str(type(stmt)))

        self.setNodeWidth()

        height = 0
        toplevel_nodes = [x for x in self.nodeOrder if x.xy[0] == 0]
        for node in toplevel_nodes:
            height = self.setNodeHeight(node, height)


def main():
    usage = "usage: %prog [options] infile"
    p = OptionParser(usage=usage)
    p.add_option('-o', dest='filename',
                 help='write diagram to FILE', metavar='FILE')
    p.add_option('-f', '--font', dest='font',
                 help='use FONT to draw diagram', metavar='FONT')
    (options, args) = p.parse_args()

    if len(args) == 0:
        p.print_help()
        exit(0)

    fonts = [options.font,
             'c:/windows/fonts/VL-Gothic-Regular.ttf',
             'c:/windows/fonts/msmincho.ttf',
             '/usr/share/fonts/truetype/ipafont/ipagp.ttf']

    ttfont = None
    for path in fonts:
        if path and os.path.isfile(path):
            ttfont = ImageFont.truetype(path, 11)
            break

    draw = DiagramDraw.DiagramDraw()

    infile = args[0]
    if options.filename:
        outfile = options.filename
    else:
        outfile = re.sub('\..*', '', infile) + '.png'

    try:
        tree = diagparser.parse_file(infile)
        nodelist, edgelist = ScreenNodeBuilder.build(tree)

        draw.screennodelist(nodelist, font=ttfont)
        draw.edgelist(edgelist)
    except Exception, e:
        import traceback
        traceback.print_exc()

        name = e.__class__.__name__
        print "[%s] %s" % (name, e)
        exit(1)

    draw.save(outfile, 'PNG')


if __name__ == '__main__':
    main()
