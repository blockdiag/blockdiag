#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import re
import sys
from ConfigParser import SafeConfigParser
from optparse import OptionParser
from elements import *
import DiagramDraw
import diagparser
import noderenderer
from utils.XY import XY
import utils


class DiagramTreeBuilder:
    def build(self, tree):
        diagram = self.instantiate(Diagram(), tree)
        for subgroup in diagram.traverse_groups():
            if len(subgroup.nodes) == 0:
                subgroup.group.nodes.remove(subgroup)

        self.bind_edges(diagram)
        return diagram

    def is_related_group(self, group1, group2):
        if group1.is_parent(group2) or group2.is_parent(group1):
            return True
        else:
            return False

    def belong_to(self, node, group):
        if node.group and node.group.level > group.level:
            override = False
        else:
            override = True

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
            # Translate Node having group attribute to SubGraph
            if isinstance(stmt, diagparser.Node):
                group_attr = [a for a in stmt.attrs if a.name == 'group']
                if group_attr:
                    group_id = group_attr[-1]
                    stmt.attrs.remove(group_id)

                    if group_id.value != group.id:
                        stmt = diagparser.SubGraph(group_id.value, [stmt])

            # Instantiate statements
            if isinstance(stmt, diagparser.Node):
                node = DiagramNode.get(stmt.id)
                node.set_attributes(stmt.attrs)
                self.belong_to(node, group)

            elif isinstance(stmt, diagparser.Edge):
                nodes = stmt.nodes.pop(0)
                edge_from = [DiagramNode.get(n) for n in nodes]
                for node in edge_from:
                    self.belong_to(node, group)

                while len(stmt.nodes):
                    edge_type, edge_to = stmt.nodes.pop(0)
                    edge_to = [DiagramNode.get(n) for n in edge_to]
                    for node in edge_to:
                        self.belong_to(node, group)

                    for node1 in edge_from:
                        for node2 in edge_to:
                            edge = DiagramEdge.get(node1, node2)
                            if edge_type:
                                attrs = [diagparser.Attr('dir', edge_type)]
                                edge.set_attributes(attrs)
                            edge.set_attributes(stmt.attrs)

                    edge_from = edge_to

            elif isinstance(stmt, diagparser.SubGraph):
                subgroup = NodeGroup.get(stmt.id)
                subgroup.level = group.level + 1
                self.belong_to(subgroup, group)
                self.instantiate(subgroup, stmt)

            elif isinstance(stmt, diagparser.DefAttrs):
                group.set_attributes(stmt.attrs)

            else:
                raise AttributeError("Unknown sentense: " + str(type(stmt)))

        group.update_order()
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
        if isinstance(self.diagram, Diagram):
            for group in self.diagram.traverse_groups():
                self.__class__(group).run()

        self.edges = DiagramEdge.find_by_level(self.diagram.level)
        self.do_layout()
        self.diagram.fixiate()

        if self.diagram.orientation == 'portrait':
            self.rotate_diagram()

    def rotate_diagram(self):
        for node in self.diagram.traverse_nodes():
            node.xy = XY(node.xy.y, node.xy.x)
            node.width, node.height = (node.height, node.width)

            if isinstance(node, NodeGroup):
                if node.orientation == 'portrait':
                    node.orientation = 'landscape'
                else:
                    node.orientation = 'portrait'

        xy = (self.diagram.height, self.diagram.width)
        self.diagram.width, self.diagram.height = xy

    def do_layout(self):
        self.detect_circulars()

        self.set_node_width()
        self.adjust_node_order()

        height = 0
        toplevel_nodes = [x for x in self.diagram.nodes if x.xy.x == 0]
        for node in self.diagram.nodes:
            if node.xy.x == 0:
                self.set_node_height(node, height)
                height = max(xy.y for xy in self.coordinates) + 1

    def get_related_nodes(self, node, parent=False, child=False):
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
            elif uniq_node.group != node.group:
                pass
            else:
                related.append(uniq_node)

        related.sort(lambda x, y: cmp(x.order, y.order))
        return related

    def get_parent_nodes(self, node):
        return self.get_related_nodes(node, parent=True)

    def get_child_nodes(self, node):
        return self.get_related_nodes(node, child=True)

    def detect_circulars(self):
        for node in self.diagram.nodes:
            if not [x for x in self.circulars if node in x]:
                self.detect_circulars_sub(node, [node])

        # remove part of other circular
        for c1 in self.circulars:
            for c2 in self.circulars:
                intersect = set(c1) & set(c2)

                if c1 != c2 and set(c1) == intersect:
                    self.circulars.remove(c1)
                    break

    def detect_circulars_sub(self, node, parents):
        for child in self.get_child_nodes(node):
            if child in parents:
                i = parents.index(child)
                self.circulars.append(parents[i:])
            else:
                self.detect_circulars_sub(child, parents + [child])

    def is_circular_ref(self, node1, node2):
        for circular in self.circulars:
            if node1 in circular and node2 in circular:
                parents = []
                for node in circular:
                    for parent in self.get_parent_nodes(node):
                        if not parent in circular:
                            parents.append(parent)

                parents.sort(lambda x, y: cmp(x.order, y.order))

                for parent in parents:
                    children = self.get_child_nodes(parent)
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

    def set_node_width(self, depth=0):
        for node in self.diagram.nodes:
            if node.xy.x != depth:
                continue

            for child in self.get_child_nodes(node):
                if self.is_circular_ref(node, child):
                    pass
                elif node == child:
                    pass
                elif child.xy.x > node.xy.x + node.width:
                    pass
                else:
                    child.xy = XY(node.xy.x + node.width, 0)

        depther_node = [x for x in self.diagram.nodes if x.xy.x > depth]
        if len(depther_node) > 0:
            self.set_node_width(depth + 1)

    def adjust_node_order(self):
        for node in self.diagram.nodes:
            parents = self.get_parent_nodes(node)
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
                children = self.get_child_nodes(node)
                if len(set(children)) > 1:
                    while True:
                        exchange = 0

                        for i in range(1, len(children)):
                            node1 = children[i - 1]
                            node2 = children[i]

                            idx1 = self.diagram.nodes.index(node1)
                            idx2 = self.diagram.nodes.index(node2)
                            ret = self.compare_child_node_order(node,
                                                                node1, node2)

                            if ret < 0 and idx1 < idx2:
                                self.diagram.nodes.remove(node1)
                                self.diagram.nodes.insert(idx2 + 1, node1)
                                exchange += 1

                        if exchange == 0:
                            break

        self.diagram.update_order()

    def compare_child_node_order(self, parent, node1, node2):
        def compare(x, y):
            x = x.duplicate()
            y = y.duplicate()
            while x.node1 == y.node1 and x.node1.group is not None:
                x.node1 = x.node1.group
                y.node1 = y.node1.group

            return cmp(x.node1.order, y.node1.order)

        edges = DiagramEdge.find(parent, node1) + \
                DiagramEdge.find(parent, node2)
        edges.sort(compare)
        if len(edges) == 0:
            return 0
        elif edges[0].node2 == node1:
            return 1
        else:
            return -1

    def mark_xy(self, xy, width, height):
        for w in range(width):
            for h in range(height):
                self.coordinates.append(XY(xy.x + w, xy.y + h))

    def set_node_height(self, node, height=0):
        xy = XY(node.xy.x, height)
        if xy in self.coordinates:
            return False
        node.xy = xy
        self.mark_xy(node.xy, node.width, node.height)

        count = 0
        children = self.get_child_nodes(node)
        children.sort(lambda x, y: cmp(x.xy.x, y.xy.y))
        for child in children:
            if child.id in self.heightRefs:
                pass
            elif node.xy.x >= child.xy.x:
                pass
            else:
                if isinstance(node, NodeGroup):
                    parent_height = self.get_parent_node_height(node, child)
                    if parent_height and parent_height > height:
                        height = parent_height

                while True:
                    if self.set_node_height(child, height):
                        child.xy = XY(child.xy.x, height)
                        self.mark_xy(child.xy, child.width, child.height)
                        self.heightRefs.append(child.id)

                        count += 1
                        break
                    else:
                        if count == 0:
                            return False

                        height += 1

                height += 1

        return True

    def get_parent_node_height(self, parent, child):
        heights = []
        for e in DiagramEdge.find(parent, child):
            y = parent.xy.y

            node = e.node1
            while node != parent:
                y += node.xy.y
                node = node.group

            heights.append(y)

        if heights:
            return min(heights)
        else:
            return None


class ScreenNodeBuilder:
    @classmethod
    def build(klass, tree, layout=True):
        diagram = DiagramTreeBuilder().build(tree)
        if layout:
            DiagramLayoutManager(diagram).run()
            diagram.fixiate(True)
        return diagram

    @classmethod
    def separate(self, diagram):
        if diagram.group is None:
            pass

        DiagramLayoutManager(diagram).run()
        diagram.fixiate(True)

        return diagram

    @classmethod
    def _separate(self, diagram):
        diagrams = []
        for group in diagram.traverse_groups():
            base = Diagram()
            parent = group.group
            edges = DiagramEdge.find_by_level(parent.level)

            uniq_edges = {}
            for edge in edges:
                if edge.node1 == group or edge.node2 == group:
                    uniq_edges[edge.node1] = 1
                    uniq_edges[edge.node2] = 1

            uniq_nodes = {}
            nodes = uniq_edges.keys()
            nodes.sort(lambda x, y: cmp(x.order, y.order))
            for node in nodes:
                if isinstance(node, NodeGroup):
                    group = node.duplicate()
                    group.group = base
                    for subnode in node.nodes:
                        if isinstance(subnode, NodeGroup):
                            subgroup = subnode.duplicate()
                            subgroup.group = group
                            subgroup.separated = True
                            group.nodes.append(subgroup)
                        else:
                            newnode = subnode.duplicate()
                            newnode.group = group
                            uniq_nodes[subnode] = newnode
                            group.nodes.append(newnode)

                    base.nodes.append(group)
                else:
                    newnode = node.duplicate()
                    newnode.group = base
                    uniq_nodes[node] = newnode
                    base.nodes.append(newnode)

            for edge in DiagramEdge.find_all():
                if edge.node1 in uniq_nodes and edge.node2 in uniq_nodes:
                    node1 = uniq_nodes[edge.node1]
                    node2 = uniq_nodes[edge.node2]
                    DiagramEdge.get(node1, node2)

            self.bind_edges(base)
            diagrams.append(base)

        return diagrams

    @classmethod
    def bind_edges(self, group):
        for node in group.nodes:
            if isinstance(node, DiagramNode):
                group.edges += DiagramEdge.find(node)
            else:
                self.bind_edges(node)


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
    if not options.type in ('SVG', 'PNG', 'PDF'):
        msg = "ERROR: unknown format: %s\n" % options.type
        sys.stderr.write(msg)
        sys.exit(0)

    if options.type == 'PDF':
        try:
            import reportlab.pdfgen.canvas
        except ImportError:
            msg = "ERROR: colud not output PDF format; Install reportlab\n"
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
    if options.separate:
        diagram = ScreenNodeBuilder.build(tree, layout=False)

        for i, group in enumerate(diagram.traverse_groups()):
            group = ScreenNodeBuilder.separate(group)

            draw = DiagramDraw.DiagramDraw(options.type, group,
                                           font=fontpath,
                                           basediagram=diagram,
                                           antialias=options.antialias)
            draw.draw()
            outfile2 = re.sub('.svg$', '', outfile) + ('_%d.svg' % (i + 1))
            draw.save(outfile2)
            group.href = './%s' % os.path.basename(outfile2)

        diagram = ScreenNodeBuilder.separate(diagram)
    else:
        diagram = ScreenNodeBuilder.build(tree)

    draw = DiagramDraw.DiagramDraw(options.type, diagram, outfile,
                                   font=fontpath, antialias=options.antialias)
    draw.draw()
    draw.save()


if __name__ == '__main__':
    main()
