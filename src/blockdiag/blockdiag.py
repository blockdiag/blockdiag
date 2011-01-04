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


class DiagramTreeBuilder:
    def build(self, tree):
        diagram = self.instantiate(Diagram(), tree)

        self.bind_edges(diagram)
        return diagram

    def is_related_group(self, group1, group2):
        gr = group1
        while gr is not None:
            if gr == group2:
                return True

            gr = gr.group

        gr = group2
        while gr is not None:
            if gr == group1:
                return True

            gr = gr.group

        return False

    def belong_to(self, node, group, override=True):
        if node.group and node.group != group and override:
            if not self.is_related_group(node.group, group):
                msg = "DiagramNode could not belong to two groups"
                raise RuntimeError(msg)

            old_group = node.group

            parent = group.parent(old_group.level + 1)
            if parent:
                if parent in old_group.nodes:
                    old_group.nodes.remove(parent)

                index = old_group.nodes.index(node)
                old_group.nodes.insert(index + 1, parent)

            old_group.nodes.remove(node)
            node.group = None

        if node.group is None:
            node.group = group

            if node not in group.nodes:
                group.nodes.append(node)

    def unbelong_to(self, node, group):
        if node in group.nodes:
            group.nodes.remove(node)

    def instantiate(self, group, tree):
        for stmt in tree.stmts:
            if isinstance(stmt, diagparser.Node):
                node = DiagramNode.get(stmt.id)
                node.setAttributes(stmt.attrs)
                self.belong_to(node, group)

            elif isinstance(stmt, diagparser.Edge):
                edge_from = DiagramNode.get(stmt.nodes.pop(0))
                self.belong_to(edge_from, group, override=False)

                while len(stmt.nodes):
                    type, edge_to = stmt.nodes.pop(0)
                    edge_to = DiagramNode.get(edge_to)
                    self.belong_to(edge_to, group, override=False)

                    edge = DiagramEdge.get(edge_from, edge_to)
                    if type:
                        edge.setAttributes([diagparser.Attr('dir', type)])
                    edge.setAttributes(stmt.attrs)

                    edge_from = edge_to

            elif isinstance(stmt, diagparser.SubGraph):
                subgroup = NodeGroup.get(stmt.id)
                subgroup.level = group.level + 1
                self.belong_to(subgroup, group)
                self.instantiate(subgroup, stmt)
                if len(subgroup.nodes) == 0:
                    self.unbelong_to(subgroup, group)

            elif isinstance(stmt, diagparser.DefAttrs):
                group.setAttributes(stmt.attrs)

            else:
                raise AttributeError("Unknown sentense: " + str(type(stmt)))

        for i, node in enumerate(group.nodes):
            node.order = i

        return group

    def bind_edges(self, group):
        for node in group.nodes:
            if isinstance(node, DiagramNode):
                group.edges += DiagramEdge.find(node)
            else:
                self.bind_edges(node)


class DiagramLayoutManager:
    def __init__(self, diagram):
        self.diagram = diagram

        self.circulars = []
        self.heightRefs = []
        self.coordinates = []

    def run(self):
        for group in self.diagram.traverse_groups():
            self.__class__(group).run()

        self.edges = DiagramEdge.find_by_level(self.diagram.level)
        self.do_layout()
        self.diagram.fixiate(fixiate_only_groups=True)

    def do_layout(self):
        self.detectCirculars()

        self.setNodeWidth()
        self.adjustNodeOrder()

        height = 0
        toplevel_nodes = [x for x in self.diagram.nodes if x.xy.x == 0]
        for node in self.diagram.nodes:
            if node.xy.x == 0:
                self.setNodeHeight(node, height)
                height = max(xy.y for xy in self.coordinates) + 1

    def getRelatedNodes(self, node, parent=False, child=False):
        uniq = {}
        for edge in self.edges:
            if edge.folded:
                continue

            if parent and edge.node2 == node:
                uniq[edge.node1] = 1
            elif child and edge.node1 == node:
                uniq[edge.node2] = 1

        related = []
        for uniq_node in uniq.keys():
            if uniq_node == node:
                pass
            else:
                related.append(uniq_node)

        related.sort(lambda x, y: cmp(x.order, y.order))
        return related

    def getParents(self, node):
        return self.getRelatedNodes(node, parent=True)

    def getChildren(self, node):
        return self.getRelatedNodes(node, child=True)

    def detectCirculars(self):
        for node in self.diagram.nodes:
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
        for node in self.diagram.nodes:
            if node.xy.x != depth:
                continue

            for child in self.getChildren(node):
                if self.isCircularRef(node, child):
                    pass
                elif node == child:
                    pass
                else:
                    child.xy = XY(node.xy.x + node.width, 0)

        depther_node = [x for x in self.diagram.nodes if x.xy.x > depth]
        if len(depther_node) > 0:
            self.setNodeWidth(depth + 1)

    def adjustNodeOrder(self):
        for node in self.diagram.nodes:
            parents = self.getParents(node)
            if len(set(parents)) > 1:
                for i in range(1, len(parents)):
                    idx1 = self.diagram.nodes.index(parents[i - 1])
                    idx2 = self.diagram.nodes.index(parents[i])
                    if idx1 < idx2:
                        self.diagram.nodes.remove(parents[i])
                        self.diagram.nodes.insert(idx1 + 1, parents[i])
                    else:
                        self.diagram.nodes.remove(parents[i - 1])
                        self.diagram.nodes.insert(idx2 + 1, parents[i - 1])

            if isinstance(node, NodeGroup):
                nodes = [n for n in node.nodes if n in self.diagram.nodes]
                if nodes:
                    idx = min(self.diagram.nodes.index(n) for n in nodes)
                    if idx < self.diagram.nodes.index(node):
                        self.diagram.nodes.remove(node)
                        self.diagram.nodes.insert(idx + 1, node)

        for i, node in enumerate(self.diagram.nodes):
            node.order = i

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


class ScreenNodeBuilder:
    @classmethod
    def build(klass, tree, subdiagram=False, group_id=None, separate=False):
        diagram = DiagramTreeBuilder().build(tree)
        DiagramLayoutManager(diagram).run()
        diagram.fixiate()
        return diagram


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
