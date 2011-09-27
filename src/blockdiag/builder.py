# -*- coding: utf-8 -*-
#  Copyright 2011 Takeshi KOMIYA
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import os
import re
from elements import *
import diagparser
from utils.XY import XY


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
                msg = "could not belong to two groups: %s" % node.id
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
        for c1 in self.circulars[:]:
            for c2 in self.circulars:
                intersect = set(c1) & set(c2)

                if c1 != c2 and set(c1) == intersect:
                    if c1 in self.circulars:
                        self.circulars.remove(c1)
                    break

                if c1 != c2 and intersect:
                    if c1 in self.circulars:
                        self.circulars.remove(c1)
                    self.circulars.remove(c2)
                    self.circulars.append(c1 + c2)
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
        for node in list(self.diagram.nodes):
            parents = self.get_parent_nodes(node)
            if len(set(parents)) > 1:
                for i in range(1, len(parents)):
                    node1 = parents[i - 1]
                    node2 = parents[i]

                    if node1.xy.x == node2.xy.x:
                        idx1 = self.diagram.nodes.index(node1)
                        idx2 = self.diagram.nodes.index(node2)

                        if idx1 < idx2:
                            self.diagram.nodes.remove(node2)
                            self.diagram.nodes.insert(idx1 + 1, node2)
                        else:
                            self.diagram.nodes.remove(node1)
                            self.diagram.nodes.insert(idx2 + 1, node1)

            children = self.get_child_nodes(node)
            if len(set(children)) > 1:
                for i in range(1, len(children)):
                    node1 = children[i - 1]
                    node2 = children[i]

                    idx1 = self.diagram.nodes.index(node1)
                    idx2 = self.diagram.nodes.index(node2)

                    if node1.xy.x == node2.xy.x:
                        if idx1 < idx2:
                            self.diagram.nodes.remove(node2)
                            self.diagram.nodes.insert(idx1 + 1, node2)
                        else:
                            self.diagram.nodes.remove(node1)
                            self.diagram.nodes.insert(idx2 + 1, node1)
                    elif self.is_circular_ref(node1, node2):
                        pass
                    else:
                        if node1.xy.x < node2.xy.x:
                            self.diagram.nodes.remove(node2)
                            self.diagram.nodes.insert(idx1 + 1, node2)
                        else:
                            self.diagram.nodes.remove(node1)
                            self.diagram.nodes.insert(idx2 + 1, node1)

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
        for x in range(node.width):
            for y in range(node.height):
                xy = XY(node.xy.x + x, height + y)
                if xy in self.coordinates:
                    return False
        node.xy = XY(node.xy.x, height)
        self.mark_xy(node.xy, node.width, node.height)

        count = 0
        children = self.get_child_nodes(node)
        children.sort(lambda x, y: cmp(x.xy.x, y.xy.y))

        grandchild = 0
        for child in children:
            if self.get_child_nodes(child):
                grandchild += 1

        prev_child = None
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

                if prev_child and grandchild > 1 and \
                   not self.is_rhombus(prev_child, child):
                    coord = [p.y for p in self.coordinates if p.x > child.xy.x]
                    if coord:
                        height = max(coord) + 1

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
                prev_child = child

        return True

    def is_rhombus(self, node1, node2):
        ret = False
        while True:
            if node1 == node2:
                ret = True
                break

            child1 = self.get_child_nodes(node1)
            child2 = self.get_child_nodes(node2)

            if len(child1) != 1 or len(child2) != 1:
                break
            elif node1.xy.x > child1[0].xy.x or node2.xy.x > child2[0].xy.x:
                break
            else:
                node1 = child1[0]
                node2 = child2[0]

        return ret

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
        DiagramNode.clear()
        DiagramEdge.clear()
        NodeGroup.clear()
        Diagram.clear()

        diagram = DiagramTreeBuilder().build(tree)
        if layout:
            DiagramLayoutManager(diagram).run()
            diagram.fixiate(True)

        return diagram


class SeparateDiagramBuilder:
    @classmethod
    def build(cls, tree):
        DiagramNode.clear()
        DiagramEdge.clear()
        NodeGroup.clear()
        Diagram.clear()

        return cls(tree).run()

    def __init__(self, tree):
        self.diagram = DiagramTreeBuilder().build(tree)

    @property
    def _groups(self):
        # Store nodes and edges of subgroups
        nodes = {self.diagram: self.diagram.nodes}
        edges = {self.diagram: self.diagram.edges}
        levels = {self.diagram: self.diagram.level}
        for group in self.diagram.traverse_groups():
            nodes[group] = group.nodes
            edges[group] = group.edges
            levels[group] = group.level

        groups = {}
        orders = {}
        for node in self.diagram.traverse_nodes():
            groups[node] = node.group
            orders[node] = node.order

        for group in self.diagram.traverse_groups():
            yield group

            # Restore nodes, groups and edges
            for g in nodes:
                g.nodes = nodes[g]
                g.edges = edges[g]
                g.level = levels[g]

            for n in groups:
                n.group = groups[n]
                n.order = orders[n]
                n.xy = XY(0, 0)
                n.width = 1
                n.height = 1

            for edge in DiagramEdge.find_all():
                edge.skipped = False
                edge.crosspoints = []

        yield self.diagram

    def _filter_edges(self, edges, parent, level):
        filtered = {}
        for e in edges:
            if e.node1.group.is_parent(parent):
                if e.node1.group.level > level:
                    e = e.duplicate()
                    if isinstance(e.node1, NodeGroup):
                        e.node1 = e.node1.parent(level + 1)
                    else:
                        e.node1 = e.node1.group.parent(level + 1)
            else:
                continue

            if e.node2.group.is_parent(parent):
                if e.node2.group.level > level:
                    e = e.duplicate()
                    if isinstance(e.node2, NodeGroup):
                        e.node2 = e.node2.parent(level + 1)
                    else:
                        e.node2 = e.node2.group.parent(level + 1)
            else:
                continue

            filtered[(e.node1, e.node2)] = e

        return filtered.values()

    def run(self):
        for i, group in enumerate(self._groups):
            base = self.diagram.duplicate()
            base.level = group.level - 1

            # bind edges on base diagram (outer the group)
            edges = DiagramEdge.find(None, group) + \
                    DiagramEdge.find(group, None)
            base.edges = self._filter_edges(edges, self.diagram, group.level)

            # bind edges on target group (inner the group)
            subgroups = group.traverse_groups()
            edges = sum([g.edges for g in subgroups], group.edges)
            group.edges = []
            for e in self._filter_edges(edges, group, group.level):
                if isinstance(e.node1, NodeGroup) and e.node1 == e.node2:
                    pass
                else:
                    group.edges.append(e)

            # clear subgroups in the group
            for g in group.nodes:
                if isinstance(g, NodeGroup):
                    g.nodes = []
                    g.edges = []

            # pick up nodes to base diagram
            nodes1 = [e.node1 for e in DiagramEdge.find(None, group)]
            nodes1.sort(lambda x, y: cmp(x.order, y.order))
            nodes2 = [e.node2 for e in DiagramEdge.find(group, None)]
            nodes2.sort(lambda x, y: cmp(x.order, y.order))

            nodes = nodes1 + [group] + nodes2
            for i, n in enumerate(nodes):
                n.order = i
                if n not in base.nodes:
                    base.nodes.append(n)
                    n.group = base

            if isinstance(group, Diagram):
                base = group

            DiagramLayoutManager(base).run()
            base.fixiate(True)

            yield base
