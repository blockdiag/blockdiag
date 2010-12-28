#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import re
import sys
import uuid
from ConfigParser import SafeConfigParser
from optparse import OptionParser
from elements import *
import DiagramDraw
import diagparser
from utils.XY import XY
import utils


class ScreenNodeBuilder:
    @classmethod
    def build(klass, tree, subdiagram=False, separate=False):
        return klass(subdiagram)._build(tree, separate)

    def __init__(self, subdiagram=False):
        if subdiagram:
            self.diagram = NodeGroup('')
        else:
            self.diagram = Diagram()

        self.uniqNodes = {}
        self.nodeOrder = []
        self.uniqLinks = {}
        self.heightRefs = []
        self.circulars = []
        self.coordinates = []
        self.separate = False

    def _build(self, tree, separate=False):
        self.separate = separate
        self.diagram.separated = separate
        self.buildNodeList(tree)

        self.diagram.nodes = self.nodeOrder
        self.diagram.edges = self.uniqLinks.values()
        self.diagram.fixiate()

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

    def removeDiagramNode(self, id):
        group = self.getDiagramNode(id)

        del self.uniqNodes[group.id]
        self.nodeOrder.remove(group)

    def getDiagramGroup(self, id):
        if id is None:
            # generate new id
            id = 'DiagramGroup %s' % uuid.uuid1()
        elif not re.search('DiagramGroup', id):
            id = 'DiagramGroup %s' % id

        if id in self.uniqNodes:
            group = self.uniqNodes[id]
        else:
            group = NodeGroup(id)
            self.uniqNodes[id] = group
            self.nodeOrder.append(group)

        return group

    def removeDiagramGroup(self, id):
        group = self.getDiagramGroup(id)

        del self.uniqNodes[group.id]
        self.nodeOrder.remove(group)

    def getDiagramEdge(self, id1, id2, type=None):
        link = (self.getDiagramNode(id1), self.getDiagramNode(id2))

        if link in self.uniqLinks:
            edge = self.uniqLinks[link]
        else:
            edge = DiagramEdge(link[0], link[1])
            self.uniqLinks[link] = edge

        if type:
            edge.setAttributes([diagparser.Attr('dir', type)])

        return edge

    def getRelatedNodes(self, node, parent=False, child=False):
        uniq = {}
        for edge in self.uniqLinks.values():
            if edge.noweight:
                continue

            if parent:
                if edge.node2.id == node.id:
                    uniq[edge.node1] = 1
                elif edge.node2.group and edge.node2.group.id == node.id:
                    uniq[edge.node1] = 1
            elif child:
                if edge.node1.id == node.id:
                    uniq[edge.node2] = 1
                elif edge.node1.group and edge.node1.group.id == node.id:
                    uniq[edge.node2] = 1

        related = []
        for uniq_node in uniq.keys():
            if uniq_node.group:
                if node != uniq_node.group:
                    related.append(uniq_node.group)
            else:
                related.append(uniq_node)

        related.sort(lambda x, y: cmp(x.order, y.order))
        return related

    def getParents(self, node):
        return self.getRelatedNodes(node, parent=True)

    def getChildren(self, node):
        return self.getRelatedNodes(node, child=True)

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
                        if circular.index(node1) > circular.index(node2):
                            return True
                    elif node2 in children:
                        return True
                    elif node1 in children:
                        return False
                else:
                    if circular.index(node1) > circular.index(node2):
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
        self.markXY(node.xy, node.width, node.height)

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

            if isinstance(node, NodeGroup):
                nodes = [n for n in node.nodes if n in self.nodeOrder]
                if nodes:
                    idx = min(self.nodeOrder.index(n) for n in nodes)
                    if idx < self.nodeOrder.index(node):
                        self.nodeOrder.remove(node)
                        self.nodeOrder.insert(idx + 1, node)

        for i in range(len(self.nodeOrder)):
            self.nodeOrder[i].order = i

    def buildNodeGroup(self, group, tree):
        def picknodes(tree, list):
            for node in tree.stmts:
                if isinstance(node, diagparser.Node):
                    list.append(node.id)
                elif isinstance(node, diagparser.SubGraph):
                    picknodes(node, list)

            return list

        nodes = picknodes(tree, [])
        for edge in self.uniqLinks.values():
            node1_id = edge.node1.id
            node2_id = edge.node2.id

            if node1_id in nodes and node2_id in nodes:
                edge = diagparser.Edge([node1_id, (None, node2_id)], [])
                tree.stmts.append(edge)

        diagram = ScreenNodeBuilder.build(tree, subdiagram=True,
                                          separate=self.separate)
        if len(diagram.nodes) == 0:
            self.removeDiagramGroup(group.id)
            return

        group.copyAttributes(diagram)

        for node in diagram.nodes:
            if isinstance(node, NodeGroup):
                n = self.getDiagramGroup(node.id)
                n.nodes = node.nodes
            else:
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
            group.separated = True

            for node in diagram.nodes:
                self.removeDiagramNode(node.id)

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
                edge_from = stmt.nodes.pop(0)
                while len(stmt.nodes):
                    type, edge_to = stmt.nodes.pop(0)
                    edge = self.getDiagramEdge(edge_from, edge_to, type)
                    edge.setAttributes(stmt.attrs)

                    edge_from = edge_to
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
                height = max(xy.y for xy in self.coordinates) + 1


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
