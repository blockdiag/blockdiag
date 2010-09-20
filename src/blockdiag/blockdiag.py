#!/usr/bin/python
# -*- encoding: utf-8 -*-

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
        self.linkForward = {}
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
            self.nodeOrder.append(id)

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

    def setNodeWidth(self, parent, node):
        if node.id in self.widthRefs or parent == node:
            return

        node.xy = (parent.xy[0] + 1, node.xy[1])
        self.widthRefs.append(parent.id)

        if node.id in self.linkForward:
            for child_id in self.getChildrenIds(node):
                childnode = self.getScreenNode(child_id)
                self.setNodeWidth(node, childnode)

    def setNodeHeight(self, node, height):
        node.xy = (node.xy[0], height)
        if node.id in self.linkForward:
            for child_id in self.getChildrenIds(node):
                if not child_id in self.heightRefs:
                    childnode = self.getScreenNode(child_id)

                    if node.xy[0] < childnode.xy[0]:
                        height = self.setNodeHeight(childnode, height)
                    else:
                        height += 1

                    self.heightRefs.append(child_id)
                else:
                    if not node.id in self.heightRefs:
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
                    edge = self.getScreenEdge(stmt.nodes.pop(0), stmt.nodes[0])
                    edge.setAttributes(stmt.attrs)
            else:
                raise AttributeError("Unknown sentense: " + str(type(stmt)))

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
        fontpath = 'c:/windows/fonts/VL-Gothic-Regular.ttf'
    else:
        fontpath = '/usr/share/fonts/truetype/ipafont/ipagp.ttf'
    ttfont = ImageFont.truetype(fontpath, 11)

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
