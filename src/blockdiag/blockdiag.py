#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import re
import sys
import uuid
from ConfigParser import SafeConfigParser
from optparse import OptionParser
import DiagramDraw
import diagparser
from utils.XY import XY
import utils


class Diagram:
    def __init__(self):
        self.nodes = []
        self.edges = []
        self.subdiagram = False
        self.rankdir = None
        self.color = None
        self.label = None
        self.node_width = None
        self.node_height = None
        self.span_width = None
        self.span_height = None
        self.fontsize = None

    def traverse_nodes(self):
        for node in self.nodes:
            if isinstance(node, NodeGroup):
                yield node
                for subnode in node.traverse_nodes():
                    yield subnode
            else:
                yield node

    def setAttributes(self, attrs):
        for attr in attrs:
            value = re.sub('(\A"|"\Z)', '', attr.value, re.M)

            if self.subdiagram:
                if attr.name == 'color':
                    self.color = value
                elif attr.name == 'label':
                    self.label = value
                else:
                    msg = "Unknown node attribute: group.%s" % attr.name
                    raise AttributeError(msg)
            else:
                if attr.name == 'rankdir':
                    if value.upper() == 'LR':
                        self.rankdir = value.upper()
                    else:
                        msg = "WARNING: unknown rankdir: %s\n" % value
                        sys.stderr.write(msg)
                elif attr.name == 'node_width':
                    self.node_width = int(value)
                elif attr.name == 'node_height':
                    self.node_height = int(value)
                elif attr.name == 'span_width':
                    self.span_width = int(value)
                elif attr.name == 'span_height':
                    self.span_height = int(value)
                elif attr.name == 'fontsize':
                    self.fontsize = int(value)
                else:
                    msg = "Unknown node attribute: diagram.%s" % attr.name
                    raise AttributeError(msg)


class DiagramNode:
    @classmethod
    def getId(klass, node):
        try:
            node_id = node.id
        except AttributeError:
            node_id = node

        return node_id

    def __init__(self, id):
        self.id = id
        self.xy = XY(0, 0)
        self.group = None
        self.drawable = 1
        self.order = 0

        if id:
            self.label = re.sub('(\A"|"\Z)', '', id, re.M)
        else:
            self.label = ''
        self.color = (255, 255, 255)
        self.style = None
        self.numbered = None
        self.background = None
        self.description = None
        self.width = 1
        self.height = 1

    def __eq__(self, other):
        if isinstance(other, str):
            return self.id == other
        else:
            return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def copyAttributes(self, other):
        if other.xy:
            self.xy = other.xy
        if other.label and other.id != other.label:
            self.label = other.label
        if other.color and other.color != (255, 255, 255):
            self.color = other.color
        if other.style:
            self.style = other.style
        if other.numbered:
            self.numbered = other.numbered
        if other.background:
            self.background = other.background
        if other.description:
            self.description = other.description
        if other.width:
            self.width = other.width
        if other.height:
            self.height = other.height

    def setAttributes(self, attrs):
        for attr in attrs:
            value = re.sub('(\A"|"\Z)', '', attr.value, re.M)
            if attr.name == 'label':
                self.label = value
            elif attr.name == 'color':
                self.color = value
            elif attr.name == 'style':
                style = value.lower()
                if style in ('solid', 'dotted', 'dashed'):
                    self.style = style
                else:
                    msg = "WARNING: unknown edge style: %s\n" % style
                    sys.stderr.write(msg)
            elif attr.name == 'numbered':
                self.numbered = value
            elif attr.name == 'background':
                if os.path.isfile(value):
                    self.background = value
                else:
                    msg = "WARNING: background image not found: %s\n" % value
                    sys.stderr.write(msg)
            elif attr.name == 'description':
                self.description = value
            elif attr.name == 'width':
                self.width = int(value)
            elif attr.name == 'height':
                self.height = int(value)
            else:
                msg = "Unknown node attribute: %s.%s" % (self.id, attr.name)
                raise AttributeError(msg)


class DiagramEdge:
    def __init__(self, node1, node2):
        self.node1 = node1
        self.node2 = node2
        self.crosspoints = []
        self.skipped = 0

        self.label = None
        self.dir = 'forward'
        self.color = None
        self.style = None
        self.noweight = None

    def copyAttributes(self, other):
        if other.label:
            self.label = other.label
        if other.dir and other.dir != 'forward':
            self.dir = other.dir
        if other.color:
            self.color = other.color
        if other.style:
            self.style = other.style
        if other.noweight:
            self.noweight = other.noweight

    def setAttributes(self, attrs):
        for attr in attrs:
            value = re.sub('(\A"|"\Z)', '', attr.value, re.M)
            if attr.name == 'label':
                self.label = value
            elif attr.name == 'dir':
                dir = value.lower()
                if dir in ('back', 'both', 'none', 'forward'):
                    self.dir = dir
                else:
                    msg = "WARNING: unknown edge dir: %s\n" % dir
                    sys.stderr.write(msg)
            elif attr.name == 'color':
                self.color = value
            elif attr.name == 'style':
                style = value.lower()
                if style in ('solid', 'dotted', 'dashed'):
                    self.style = style
                else:
                    msg = "WARNING: unknown edge style: %s\n" % style
                    sys.stderr.write(msg)
            elif attr.name == 'noweight':
                if value.lower() == 'none':
                    self.noweight = None
                else:
                    self.noweight = 1
            else:
                raise AttributeError("Unknown edge attribute: %s" % attr.name)


class NodeGroup(DiagramNode):
    def __init__(self, id):
        DiagramNode.__init__(self, id)
        self.label = ''
        self.href = None
        self.separated = False
        self.nodes = []
        self.edges = []
        self.color = (243, 152, 0)
        self.width = 1
        self.height = 1
        self.drawable = 0
        self.order = 0

    def __eq__(self, other):
        if isinstance(other, str):
            return self.id == other
        else:
            return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def traverse_nodes(self):
        for node in self.nodes:
            if isinstance(node, NodeGroup):
                yield node
                for subnode in node.traverse_nodes():
                    yield subnode
            else:
                yield node

    def setSize(self, nodes):
        if len(nodes) > 0:
            self.width = max(x.xy.x for x in nodes) + 1
            self.height = max(x.xy.y for x in nodes) + 1

    def copyAttributes(self, other):
        if other.label:
            self.label = other.label
        if other.color and other.color != (243, 152, 0):
            self.color = other.color


class ScreenNodeBuilder:
    @classmethod
    def build(klass, tree, group=False, separate=False):
        return klass()._build(tree, group, separate)

    def __init__(self):
        self.diagram = Diagram()
        self.uniqNodes = {}
        self.nodeOrder = []
        self.uniqLinks = {}
        self.heightRefs = []
        self.circulars = []
        self.coordinates = []
        self.rows = 0
        self.separate = False

    def _build(self, tree, group=False, separate=False):
        self.diagram.subdiagram = group
        self.separate = separate
        self.buildNodeList(tree)

        self.diagram.nodes = self.uniqNodes.values()
        self.diagram.edges = self.uniqLinks.values()

        if self.diagram.rankdir == 'LR':
            for node in self.diagram.nodes:
                i = node.width
                node.width = node.height
                node.height = i

                node.xy = XY(node.xy.y, node.xy.x)

        return self.diagram

    def getDiagramNode(self, id):
        if id in self.uniqNodes:
            node = self.uniqNodes[id]
        else:
            node = DiagramNode(id)
            self.uniqNodes[id] = node
            self.nodeOrder.append(node)

        return node

    def getDiagramGroup(self, id):
        if id is None:
            # generate new id
            id = 'DiagramGroup %s' % uuid.uuid1()
        else:
            id = 'DiagramGroup %s' % id

        if id in self.uniqNodes:
            group = self.uniqNodes[id]
        else:
            group = NodeGroup(id)
            self.uniqNodes[id] = group
            self.nodeOrder.append(group)

        return group

    def getDiagramEdge(self, id1, id2):
        link = (self.getDiagramNode(id1), self.getDiagramNode(id2))

        if link in self.uniqLinks:
            edge = self.uniqLinks[link]
        else:
            edge = DiagramEdge(link[0], link[1])
            self.uniqLinks[link] = edge

        return edge

    def getParents(self, node):
        node_id = DiagramNode.getId(node)

        uniq = {}
        for edge in self.uniqLinks.values():
            if edge.noweight:
                continue

            if edge.node2.id == node_id:
                uniq[edge.node1] = 1
            elif edge.node2.group and edge.node2.group.id == node_id:
                uniq[edge.node1] = 1

        children = []
        for node in uniq.keys():
            if node.group:
                children.append(node.group)
            else:
                children.append(node)

        children.sort(lambda x, y: cmp(x.order, y.order))
        return children

    def getChildren(self, node):
        node_id = DiagramNode.getId(node)

        uniq = {}
        for edge in self.uniqLinks.values():
            if edge.noweight:
                continue

            if node_id == None:
                uniq[edge.node1] = 1
            elif edge.node1.id == node_id:
                uniq[edge.node2] = 1
            elif edge.node1.group and edge.node1.group.id == node_id:
                uniq[edge.node2] = 1

        children = []
        for node in uniq.keys():
            if node.group:
                children.append(node.group)
            else:
                children.append(node)

        children.sort(lambda x, y: cmp(x.order, y.order))
        return children

    def detectCirculars(self):
        for node in self.nodeOrder:
            if not [x for x in self.circulars if node in x]:
                self.detectCircularsSub(node, [node])

        # remove part of other circular
        for c1 in self.circulars:
            for c2 in self.circulars:
                intersect = set(c1) & set(c2)

                if c1 != c2 and set(c1) == intersect:
                    self.circulars.remove(c1)
                    break

    def detectCircularsSub(self, node, parents):
        for child in self.getChildren(node):
            if child in parents:
                i = parents.index(child)
                self.circulars.append(parents[i:])
            else:
                self.detectCircularsSub(child, parents + [child])

    def isCircularRef(self, node1, node2):
        for circular in self.circulars:
            if node1 in circular and node2 in circular:
                parents = []
                for node in circular:
                    for parent in self.getParents(node):
                        if not parent in circular:
                            parents.append(parent)

                parents.sort(lambda x, y: cmp(x.order, y.order))

                for parent in parents:
                    children = self.getChildren(parent)
                    if node1 in children and node2 in children:
                        o1 = circular.index(node1)
                        o2 = circular.index(node2)

                        if o1 > o2:
                            return True
                    elif node2 in children:
                        return True
                    elif node1 in children:
                        return False
                else:
                    o1 = circular.index(node1)
                    o2 = circular.index(node2)

                    if o1 > o2:
                        return True

        return False

    def setNodeWidth(self, depth=0):
        for node in self.nodeOrder:
            if node.xy.x != depth or node.group is not None:
                continue

            for child in self.getChildren(node):
                if self.isCircularRef(node, child):
                    pass
                elif node == child:
                    pass
                elif child.group:
                    pass
                else:
                    child.xy = XY(node.xy.x + node.width, 0)

        depther_node = [x for x in self.nodeOrder if x.xy.x > depth]
        if len(depther_node) > 0:
            self.setNodeWidth(depth + 1)

    def markXY(self, xy, width, height):
        for w in range(width):
            for h in range(height):
                self.coordinates.append(XY(xy.x + w, xy.y + h))

    def setNodeHeight(self, node, height=0):
        xy = XY(node.xy.x, height)
        if xy in self.coordinates:
            return False
        node.xy = xy

        count = 0
        children = self.getChildren(node)
        children.sort(lambda x, y: cmp(x.xy.x, y.xy.y))
        for child in children:
            if child.id in self.heightRefs:
                pass
            elif node is not None and node.xy.x >= child.xy.x:
                pass
            else:
                while True:
                    if self.setNodeHeight(child, height):
                        child.xy = XY(child.xy.x, height)
                        self.markXY(child.xy, child.width, child.height)
                        self.heightRefs.append(child.id)

                        count += 1
                        break
                    else:
                        if count == 0:
                            return False

                        height += 1

                height += 1

        return True

    def adjustNodeOrder(self):
        for node in self.nodeOrder:
            parents = self.getParents(node)
            if len(set(parents)) > 1:
                for i in range(1, len(parents)):
                    idx1 = self.nodeOrder.index(parents[i - 1])
                    idx2 = self.nodeOrder.index(parents[i])
                    if idx1 < idx2:
                        self.nodeOrder.remove(parents[i])
                        self.nodeOrder.insert(idx1 + 1, parents[i])
                    else:
                        self.nodeOrder.remove(parents[i - 1])
                        self.nodeOrder.insert(idx2 + 1, parents[i - 1])

    def buildNodeGroup(self, group, tree):
        nodes = [x.id for x in tree.stmts if isinstance(x, diagparser.Node)]
        for edge in self.uniqLinks.values():
            node1_id = edge.node1.id
            node2_id = edge.node2.id

            if node1_id in nodes and node2_id in nodes:
                edge = diagparser.Edge([node1_id, node2_id], [])
                tree.stmts.append(edge)

        diagram = ScreenNodeBuilder.build(tree, group=True,
                                          separate=self.separate)
        group.copyAttributes(diagram)
        if len(diagram.nodes) == 0:
            del self.uniqNodes[group.id]
            self.nodeOrder.remove(group)
            return

        group.setSize(diagram.nodes)

        for node in diagram.nodes:
            n = self.getDiagramNode(node.id)
            if n.group:
                msg = "DiagramNode could not belong to two groups"
                raise RuntimeError(msg)
            n.copyAttributes(node)
            n.group = group

            group.nodes.append(n)

        for edge in diagram.edges:
            e = self.getDiagramEdge(edge.node1.id, edge.node2.id)
            e.copyAttributes(edge)
            e.group = group

            group.edges.append(e)

        if self.separate:
            group.width = 1
            group.height = 1
            group.separated = True

            for node in diagram.nodes:
                if node.id in self.uniqNodes:
                    del self.uniqNodes[node.id]
                if node in self.nodeOrder:
                    self.nodeOrder.remove(node)

                for link in self.uniqLinks.keys():
                    if link[0] == node:
                        del self.uniqLinks[link]

                        if link[1] != group:
                            link = (group, link[1])
                            edge = DiagramEdge(link[0], link[1])
                            self.uniqLinks[link] = edge
                    elif link[1] == node:
                        del self.uniqLinks[link]

                        if link[0] != group:
                            link = (link[0], group)
                            edge = DiagramEdge(link[0], link[1])
                            self.uniqLinks[link] = edge

    def buildNodeList(self, tree):
        nodeGroups = {}
        for stmt in tree.stmts:
            if isinstance(stmt, diagparser.Node):
                node = self.getDiagramNode(stmt.id)
                node.setAttributes(stmt.attrs)
            elif isinstance(stmt, diagparser.Edge):
                while len(stmt.nodes) >= 2:
                    edge = self.getDiagramEdge(stmt.nodes.pop(0),
                                               stmt.nodes[0])
                    edge.setAttributes(stmt.attrs)
            elif isinstance(stmt, diagparser.SubGraph):
                group = self.getDiagramGroup(stmt.id)
                nodeGroups[group] = stmt
            elif isinstance(stmt, diagparser.DefAttrs):
                self.diagram.setAttributes(stmt.attrs)
            else:
                raise AttributeError("Unknown sentense: " + str(type(stmt)))

        for group in nodeGroups:
            self.buildNodeGroup(group, nodeGroups[group])

        for i in range(len(self.nodeOrder)):
            self.nodeOrder[i].order = i

        self.detectCirculars()
        self.setNodeWidth()
        self.adjustNodeOrder()

        height = 0
        toplevel_nodes = [x for x in self.nodeOrder if x.xy.x == 0]
        for node in toplevel_nodes:
            if not node.group:
                self.setNodeHeight(node, height)
                height = max(x.xy.y for x in self.nodeOrder) + 1

        for node in self.nodeOrder:
            if isinstance(node, NodeGroup) and not self.separate:
                for child in node.nodes:
                    child.xy = XY(node.xy.x + child.xy.x,
                                  node.xy.y + child.xy.y)


def parse_option():
    usage = "usage: %prog [options] infile"
    p = OptionParser(usage=usage)
    p.add_option('-a', '--antialias', action='store_true',
                 help='Pass diagram image to anti-alias filter')
    p.add_option('-c', '--config',
                 help='read configurations from FILE', metavar='FILE')
    p.add_option('-o', dest='filename',
                 help='write diagram to FILE', metavar='FILE')
    p.add_option('-f', '--font', default=[], action='append',
                 help='use FONT to draw diagram', metavar='FONT')
    p.add_option('-P', '--pdb', dest='pdb', action='store_true', default=False,
                 help='Drop into debugger on exception')
    p.add_option('-s', '--separate', action='store_true',
                 help='Separate diagram images for each group (SVG only)')
    p.add_option('-T', dest='type', default='PNG',
                 help='Output diagram as TYPE format')
    options, args = p.parse_args()

    if len(args) == 0:
        p.print_help()
        sys.exit(0)

    options.type = options.type.upper()
    if not options.type in ('SVG', 'PNG'):
        msg = "ERROR: unknown format: %s\n" % options.type
        sys.stderr.write(msg)
        sys.exit(0)

    if options.separate and options.type != 'SVG':
        msg = "ERROR: --separate option work in SVG images.\n"
        sys.stderr.write(msg)
        sys.exit(0)

    if options.config and not os.path.isfile(options.config):
        msg = "ERROR: config file is not found: %s\n" % options.config
        sys.stderr.write(msg)
        sys.exit(0)

    configpath = options.config or "%s/.blockdiagrc" % os.environ.get('HOME')
    if os.path.isfile(configpath):
        config = SafeConfigParser()
        config.read(configpath)

        if config.has_option('blockdiag', 'fontpath'):
            fontpath = config.get('blockdiag', 'fontpath')
            options.font.append(fontpath)

    return options, args


def detectfont(options):
    fonts = options.font + \
            ['c:/windows/fonts/VL-Gothic-Regular.ttf',  # for Windows
             'c:/windows/fonts/msmincho.ttf',  # for Windows
             '/usr/share/fonts/truetype/ipafont/ipagp.ttf',  # for Debian
             '/usr/local/share/font-ipa/ipagp.otf',  # for FreeBSD
             '/System/Library/Fonts/AppleGothic.ttf']  # for MaxOS

    fontpath = None
    for path in fonts:
        if path and os.path.isfile(path):
            fontpath = path
            break

    return fontpath


def main():
    options, args = parse_option()

    infile = args[0]
    if options.filename:
        outfile = options.filename
    else:
        outfile = re.sub('\..*', '', infile) + '.' + options.type.lower()

    if options.pdb:
        sys.excepthook = utils.postmortem

    fontpath = detectfont(options)

    tree = diagparser.parse_file(infile)
    diagram = ScreenNodeBuilder.build(tree, separate=options.separate)

    if options.separate:
        for i, node in enumerate(diagram.traverse_nodes()):
            if isinstance(node, NodeGroup):
                draw = DiagramDraw.DiagramDraw(options.type, node,
                                               font=fontpath,
                                               basediagram=diagram,
                                               antialias=options.antialias)
                draw.draw()
                outfile2 = re.sub('.svg$', '_%d.svg' % i, outfile)
                draw.save(outfile2)
                node.href = './%s' % os.path.basename(outfile2)

    draw = DiagramDraw.DiagramDraw(options.type, diagram, font=fontpath,
                                   antialias=options.antialias)
    draw.draw()
    draw.save(outfile)


if __name__ == '__main__':
    main()
