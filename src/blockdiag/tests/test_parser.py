# -*- coding: utf-8 -*-

import tempfile
from blockdiag.blockdiag import *
from blockdiag.elements import *
from blockdiag.diagparser import *
from nose.tools import assert_raises


def __build_diagram(filename):
    DiagramNode.clear()
    DiagramEdge.clear()

    import os
    testdir = os.path.dirname(__file__)
    pathname = "%s/diagrams/%s" % (testdir, filename)

    str = open(pathname).read()
    tree = parse(tokenize(str))
    return ScreenNodeBuilder.build(tree)


def test_diagparser_basic():
    # basic digram
    str = ("diagram test {\n"
           "}\n")

    tree = parse(tokenize(str))
    assert isinstance(tree, Graph)


def test_diagparser_without_id():
    str = ("diagram {\n"
           "}\n")
    tree = parse(tokenize(str))
    assert isinstance(tree, Graph)


def test_diagparser_empty():
    str = ("{\n"
           "}\n")
    tree = parse(tokenize(str))
    assert isinstance(tree, Graph)


def test_diagparser_parenthesis_ness():
    def dummy():
        str = ""
        tree = parse(tokenize(str))
    assert_raises(NoParseError, dummy)


def test_empty_diagram():
    screen = __build_diagram('empty.diag')

    assert len(screen.nodes) == 0
    assert len(screen.edges) == 0


def test_diagram_attributes():
    screen = __build_diagram('diagram_attributes.diag')

    print screen.node_width
    assert screen.node_width == 160
    assert screen.node_height == 160
    assert screen.span_width == 32
    assert screen.span_height == 32
    assert screen.fontsize == 16


def test_single_node_diagram():
    screen = __build_diagram('single_node.diag')

    assert len(screen.nodes) == 1
    assert len(screen.edges) == 0
    assert screen.nodes[0].label == 'A'
    assert screen.nodes[0].xy == (0, 0)


def test_node_shape_diagram():
    screen = __build_diagram('node_shape.diag')

    assert_shape = {'A': 'box', 'B': 'roundedbox', 'C': 'diamond',
                    'D': 'ellipse', 'E': 'note', 'F': 'cloud',
                    'G': 'mail', 'H': 'beginpoint', 'I': 'endpoint',
                    'J': 'minidiamond', 'K': 'flowchart.condition',
                    'L': 'flowchart.database', 'M': 'flowchart.input',
                    'N': 'flowchart.loopin', 'O': 'flowchart.loopout',
                    'Z': 'box'}
    for node in screen.nodes:
        assert node.shape == assert_shape[node.id]


def test_unknown_node_shape_diagram():
    screen = __build_diagram('unknown_node_shape.diag')

    assert_shape = {'A': 'box', 'Z': 'box'}
    for node in screen.nodes:
        assert node.shape == assert_shape[node.id]


def test_node_shape_namespace_diagram():
    screen = __build_diagram('node_shape_namespace.diag')

    assert_shape = {'A': 'flowchart.condition', 'B': 'condition', 'Z': 'box'}
    for node in screen.nodes:
        assert node.shape == assert_shape[node.id]


def test_node_has_multilined_label_diagram():
    screen = __build_diagram('node_has_multilined_label.diag')

    assert_pos = {'A': (0, 0), 'Z': (0, 1)}
    assert_label = {'A': "foo\nbar", 'Z': 'Z'}
    for node in screen.nodes:
        assert node.xy == assert_pos[node.id]
        assert node.label == assert_label[node.id]


def test_single_edge_diagram():
    screen = __build_diagram('single_edge.diag')

    assert len(screen.nodes) == 2
    assert len(screen.edges) == 1
    assert screen.nodes[0].label == 'A'
    assert screen.nodes[1].label == 'B'

    assert_pos = {'A': (0, 0), 'B': (1, 0)}
    assert_label = {'A': 'A', 'B': 'B'}
    for node in screen.nodes:
        assert node.xy == assert_pos[node.id]
        assert node.label == assert_label[node.id]


def test_two_edges_diagram():
    screen = __build_diagram('two_edges.diag')

    assert len(screen.nodes) == 3
    assert len(screen.edges) == 2

    assert_pos = {'A': (0, 0), 'B': (1, 0), 'C': (2, 0)}
    for node in screen.nodes:
        assert node.xy == assert_pos[node.id]


def test_node_attribute():
    screen = __build_diagram('node_attribute.diag')

    assert screen.nodes[0].id == 'A'
    assert screen.nodes[0].label == 'B'
    assert screen.nodes[0].color == 'red'
    assert screen.nodes[0].xy == (0, 0)

    assert screen.nodes[1].id == 'B'
    assert screen.nodes[1].label == 'double quoted'
    assert screen.nodes[1].color == (255, 255, 255)
    assert screen.nodes[1].xy == (0, 1)

    assert screen.nodes[2].id == 'C'
    assert screen.nodes[2].label == 'single quoted'

    assert screen.nodes[3].id == 'D'
    assert screen.nodes[3].label == '\'"double" quoted\''

    assert screen.nodes[4].id == 'E'
    assert screen.nodes[4].label == '"\'single\' quoted"'


def test_edge_shape():
    screen = __build_diagram('edge_shape.diag')

    for edge in screen.edges:
        if edge.node1.id == 'A':
            assert edge.dir == 'none'
        elif edge.node1.id == 'B':
            assert edge.dir == 'forward'
        elif edge.node1.id == 'C':
            assert edge.dir == 'back'
        elif edge.node1.id == 'D':
            assert edge.dir == 'both'


def test_edge_attribute():
    screen = __build_diagram('edge_attribute.diag')

    assert_pos = {'A': (0, 0), 'B': (1, 0), 'C': (2, 0),
                  'D': (0, 1), 'E': (1, 1)}
    for node in screen.nodes:
        assert node.xy == assert_pos[node.id]

    for edge in screen.edges:
        if edge.node1.id == 'D':
            assert edge.dir == 'none'
            assert edge.color == None
        else:
            assert edge.dir == 'forward'
            assert edge.color == 'red'


def test_node_height_diagram():
    screen = __build_diagram('node_height.diag')

    assert_pos = {'A': (0, 0), 'B': (1, 0), 'C': (2, 0),
                  'D': (2, 1), 'E': (1, 1), 'Z': (0, 2)}
    for node in screen.nodes:
        assert node.xy == assert_pos[node.id]


def test_branched_diagram():
    screen = __build_diagram('branched.diag')

    assert_pos = {'A': (0, 0), 'B': (1, 0), 'C': (2, 0),
                  'D': (1, 1), 'E': (2, 1), 'Z': (0, 2)}
    for node in screen.nodes:
        assert node.xy == assert_pos[node.id]


def test_multiple_parent_node_diagram():
    screen = __build_diagram('multiple_parent_node.diag')

    assert_pos = {'A': (0, 0), 'B': (1, 0), 'C': (0, 2),
                  'D': (1, 2), 'E': (0, 1), 'Z': (0, 3)}
    for node in screen.nodes:
        assert node.xy == assert_pos[node.id]


def test_twin_multiple_parent_node_diagram():
    screen = __build_diagram('twin_multiple_parent_node.diag')

    assert_pos = {'A': (0, 0), 'B': (1, 0), 'C': (0, 1),
                  'D': (1, 1), 'E': (0, 2), 'Z': (0, 3)}
    for node in screen.nodes:
        assert node.xy == assert_pos[node.id]


def test_circular_ref_to_root_diagram():
    screen = __build_diagram('circular_ref_to_root.diag')

    assert_pos = {'A': (0, 0), 'B': (1, 0), 'C': (2, 0),
                  'D': (2, 1), 'Z': (0, 2)}
    for node in screen.nodes:
        assert node.xy == assert_pos[node.id]


def test_circular_ref_diagram():
    screen = __build_diagram('circular_ref.diag')

    assert_pos = {'A': (0, 0), 'B': (1, 0), 'C': (2, 0),
                  'D': (2, 1), 'Z': (0, 2)}
    for node in screen.nodes:
        assert node.xy == assert_pos[node.id]


def test_labeled_circular_ref_diagram():
    screen = __build_diagram('labeled_circular_ref.diag')

    assert_pos = {'A': (0, 0), 'B': (2, 0), 'C': (1, 0),
                  'Z': (0, 1)}
    for node in screen.nodes:
        assert node.xy == assert_pos[node.id]


def test_skipped_edge_diagram():
    screen = __build_diagram('skipped_edge.diag')

    assert_pos = {'A': (0, 0), 'B': (1, 0), 'C': (2, 0),
                  'Z': (0, 1)}
    for node in screen.nodes:
        assert node.xy == assert_pos[node.id]


def test_circular_skipped_edge_diagram():
    screen = __build_diagram('circular_skipped_edge.diag')

    assert_pos = {'A': (0, 0), 'B': (1, 0), 'C': (2, 0), 'Z': (0, 1)}
    for node in screen.nodes:
        assert node.xy == assert_pos[node.id]


def test_triple_branched_diagram():
    screen = __build_diagram('triple_branched.diag')

    assert_pos = {'A': (0, 0), 'B': (0, 1), 'C': (0, 2),
                  'D': (1, 0), 'Z': (0, 3)}
    for node in screen.nodes:
        assert node.xy == assert_pos[node.id]


def test_twin_circular_ref_to_root_diagram():
    screen = __build_diagram('twin_circular_ref_to_root.diag')

    assert_pos = {'A': (0, 0), 'B': (1, 0), 'C': (1, 1), 'Z': (0, 2)}
    for node in screen.nodes:
        assert node.xy == assert_pos[node.id]


def test_twin_circular_ref_diagram():
    screen = __build_diagram('twin_circular_ref.diag')

    assert_pos = {'A': (0, 0), 'B': (1, 0), 'C': (2, 0),
                  'D': (1, 1), 'Z': (0, 2)}
    for node in screen.nodes:
        assert node.xy == assert_pos[node.id]


def test_skipped_circular_diagram():
    screen = __build_diagram('skipped_circular.diag')

    assert_pos = {'A': (0, 0), 'B': (1, 0), 'C': (2, 0),
                  'Z': (0, 1)}
    for node in (x for x in screen.nodes if x.drawable):
        assert node.xy == assert_pos[node.id]


def test_nested_skipped_circular_diagram():
    screen = __build_diagram('nested_skipped_circular.diag')

    assert_pos = {'A': (0, 0), 'B': (1, 0), 'C': (2, 1),
                  'D': (3, 2), 'E': (4, 1), 'F': (5, 0),
                  'G': (6, 0), 'Z': (0, 3)}
    for node in (x for x in screen.nodes if x.drawable):
        assert node.xy == assert_pos[node.id]


def test_self_ref_diagram():
    screen = __build_diagram('self_ref.diag')

    assert_pos = {'A': (0, 0), 'B': (1, 0), 'Z': (0, 1)}
    for node in screen.nodes:
        assert node.xy == assert_pos[node.id]


def test_folded_edge_diagram():
    screen = __build_diagram('folded_edge.diag')

    assert_pos = {'A': (0, 0), 'B': (1, 0), 'C': (2, 0),
                  'D': (0, 1), 'E': (0, 2), 'F': (1, 1),
                  'Z': (0, 3)}
    for node in screen.nodes:
        assert node.xy == assert_pos[node.id]


def test_flowable_node_diagram():
    screen = __build_diagram('flowable_node.diag')

    assert_pos = {'A': (0, 0), 'B': (1, 0), 'C': (2, 0),
                  'Z': (0, 1)}
    for node in screen.nodes:
        assert node.xy == assert_pos[node.id]


def test_belongs_to_two_groups_diagram():
    def dummy():
        screen = __build_diagram('belongs_to_two_groups.diag')

    assert_raises(RuntimeError, dummy)


def test_nested_groups_diagram():
    screen = __build_diagram('nested_groups.diag')

    assert_pos = {'A': (0, 0), 'B': (0, 1), 'Z': (0, 2)}
    for node in (x for x in screen.nodes if x.drawable):
        assert node.xy == assert_pos[node.id]


def test_nested_groups_and_edges_diagram():
    screen = __build_diagram('nested_groups_and_edges.diag')

    assert_pos = {'A': (0, 0), 'B': (1, 0), 'C': (2, 0), 'Z': (0, 1)}
    for node in (x for x in screen.nodes if x.drawable):
        assert node.xy == assert_pos[node.id]


def test_node_follows_group_diagram():
    def dummy():
        screen = __build_diagram('node_follows_group.diag')

    assert_raises(NoParseError, dummy)


def test_group_follows_node_diagram():
    def dummy():
        screen = __build_diagram('group_follows_node.diag')

    assert_raises(NoParseError, dummy)


def test_empty_group_diagram():
    screen = __build_diagram('empty_group.diag')

    assert_pos = {'Z': (0, 0)}
    for node in (x for x in screen.nodes if x.drawable):
        assert node.xy == assert_pos[node.id]


def test_empty_nested_group_diagram():
    screen = __build_diagram('empty_nested_group.diag')

    assert_pos = {'Z': (0, 0)}
    for node in (x for x in screen.nodes if x.drawable):
        assert node.xy == assert_pos[node.id]


def test_simple_group_diagram():
    screen = __build_diagram('simple_group.diag')

    assert_pos = {'A': (0, 0), 'B': (1, 0), 'C': (1, 1),
                  'Z': (0, 2)}
    for node in (x for x in screen.nodes if x.drawable):
        assert node.xy == assert_pos[node.id]


def test_group_attribute():
    screen = __build_diagram('group_attribute.diag')

    for node in (x for x in screen.nodes if not x.drawable):
        node.color = 'red'
        node.label = 'group label'


def test_merge_groups_diagram():
    screen = __build_diagram('merge_groups.diag')

    assert_pos = {'A': (0, 0), 'B': (1, 0), 'C': (0, 1),
                  'D': (1, 1), 'Z': (0, 2)}
    for node in (x for x in screen.nodes if x.drawable):
        assert node.xy == assert_pos[node.id]


def test_node_attribute_and_group_diagram():
    screen = __build_diagram('node_attribute_and_group.diag')

    assert_pos = {'A': (0, 0), 'B': (1, 0), 'C': (2, 0),
                  'Z': (0, 1)}
    assert_labels = {'A': 'foo', 'B': 'bar', 'C': 'baz',
                     'Z': 'Z'}
    assert_colors = {'A': 'red', 'B': '#888888', 'C': 'blue',
                     'Z': (255, 255, 255)}
    for node in (x for x in screen.nodes if x.drawable):
        assert node.xy == assert_pos[node.id]
        assert node.label == assert_labels[node.id]
        assert node.color == assert_colors[node.id]


def test_group_order_diagram():
    screen = __build_diagram('group_order.diag')

    assert_pos = {'A': (0, 0), 'B': (1, 0), 'C': (1, 1), 'Z': (0, 2)}
    for node in (x for x in screen.nodes if x.drawable):
        assert node.xy == assert_pos[node.id]


def test_group_order2_diagram():
    screen = __build_diagram('group_order2.diag')

    assert_pos = {'A': (0, 0), 'B': (1, 0), 'C': (1, 1),
                  'D': (2, 1), 'E': (1, 2), 'F': (2, 2), 'Z': (0, 3)}
    for node in (x for x in screen.nodes if x.drawable):
        assert node.xy == assert_pos[node.id]


def test_group_order3_diagram():
    screen = __build_diagram('group_order3.diag')

    assert_pos = {'A': (0, 0), 'B': (1, 0), 'C': (2, 0),
                  'D': (2, 1), 'E': (1, 2), 'Z': (0, 3)}
    for node in (x for x in screen.nodes if x.drawable):
        assert node.xy == assert_pos[node.id]


def test_node_in_group_follows_outer_node_diagram():
    screen = __build_diagram('node_in_group_follows_outer_node.diag')

    assert_pos = {'A': (0, 0), 'B': (1, 0), 'C': (2, 0),
                  'Z': (0, 1)}
    for node in (x for x in screen.nodes if x.drawable):
        assert node.xy == assert_pos[node.id]


def test_group_id_and_node_id_are_not_conflicted_diagram():
    screen = __build_diagram('group_id_and_node_id_are_not_conflicted.diag')

    assert_pos = {'A': (0, 0), 'B': (1, 0), 'C': (0, 1),
                  'D': (1, 1), 'Z': (0, 2)}
    for node in (x for x in screen.nodes if x.drawable):
        assert node.xy == assert_pos[node.id]


def test_outer_node_follows_node_in_group_diagram():
    screen = __build_diagram('outer_node_follows_node_in_group.diag')

    assert_pos = {'A': (0, 0), 'B': (1, 0), 'C': (2, 0),
                  'Z': (0, 1)}
    for node in (x for x in screen.nodes if x.drawable):
        assert node.xy == assert_pos[node.id]


def test_large_group_and_node_diagram():
    screen = __build_diagram('large_group_and_node.diag')

    assert_pos = {'A': (0, 0), 'B': (1, 0), 'C': (1, 1),
                  'D': (1, 2), 'E': (1, 3), 'F': (2, 0),
                  'Z': (0, 4)}
    for node in (x for x in screen.nodes if x.drawable):
        assert node.xy == assert_pos[node.id]


def test_large_group_and_node2_diagram():
    screen = __build_diagram('large_group_and_node2.diag')

    assert_pos = {'A': (0, 0), 'B': (1, 0), 'C': (2, 0),
                  'D': (3, 0), 'E': (4, 0), 'F': (5, 0),
                  'Z': (0, 1)}
    for node in (x for x in screen.nodes if x.drawable):
        assert node.xy == assert_pos[node.id]


def test_large_group_and_two_nodes_diagram():
    screen = __build_diagram('large_group_and_two_nodes.diag')

    assert_pos = {'A': (0, 0), 'B': (1, 0), 'C': (1, 1),
                  'D': (1, 2), 'E': (1, 3), 'F': (2, 0),
                  'G': (2, 1), 'Z': (0, 4)}
    for node in (x for x in screen.nodes if x.drawable):
        assert node.xy == assert_pos[node.id]


def test_group_height_diagram():
    screen = __build_diagram('group_height.diag')

    assert_pos = {'A': (0, 0), 'B': (1, 0), 'C': (2, 0),
                  'D': (2, 1), 'E': (1, 2), 'Z': (0, 3)}
    for node in (x for x in screen.nodes if x.drawable):
        assert node.xy == assert_pos[node.id]


def test_multiple_groups_diagram():
    screen = __build_diagram('multiple_groups.diag')

    assert_pos = {'A': (0, 0), 'B': (0, 1), 'C': (0, 2),
                  'D': (0, 3), 'E': (1, 0), 'F': (1, 1),
                  'G': (1, 2), 'H': (2, 0), 'I': (2, 1),
                  'J': (3, 0), 'Z': (0, 4)}
    for node in (x for x in screen.nodes if x.drawable):
        print node.id, node.xy
        assert node.xy == assert_pos[node.id]


def test_multiple_nested_groups_diagram():
    screen = __build_diagram('multiple_nested_groups.diag')

    assert_pos = {'A': (0, 0), 'B': (1, 0), 'C': (1, 1),
                  'Z': (0, 2)}
    for node in (x for x in screen.nodes if x.drawable):
        print node.id, node.xy
        assert node.xy == assert_pos[node.id]


def test_group_works_node_decorator_diagram():
    screen = __build_diagram('group_works_node_decorator.diag')

    assert_pos = {'A': (0, 0), 'B': (1, 0), 'C': (3, 0),
                  'D': (2, 0), 'E': (1, 1), 'Z': (0, 2)}
    for node in (x for x in screen.nodes if x.drawable):
        assert node.xy == assert_pos[node.id]


def test_nested_groups_work_node_decorator_diagram():
    screen = __build_diagram('nested_groups_work_node_decorator.diag')

    assert_pos = {'A': (0, 0), 'B': (0, 1), 'Z': (0, 2)}
    for node in (x for x in screen.nodes if x.drawable):
        assert node.xy == assert_pos[node.id]


def test_reversed_multiple_groups_diagram():
    screen = __build_diagram('reverse_multiple_groups.diag')

    assert_pos = {'A': (3, 0), 'B': (3, 1), 'C': (3, 2),
                  'D': (3, 3), 'E': (2, 0), 'F': (2, 1),
                  'G': (2, 2), 'H': (1, 0), 'I': (1, 1),
                  'J': (0, 0), 'Z': (0, 4)}
    for node in (x for x in screen.nodes if x.drawable):
        assert node.xy == assert_pos[node.id]


def test_group_and_skipped_edge_diagram():
    screen = __build_diagram('group_and_skipped_edge.diag')

    assert_pos = {'A': (0, 0), 'B': (1, 0), 'C': (2, 0),
                  'D': (3, 0), 'E': (1, 1), 'Z': (0, 2)}
    for node in (x for x in screen.nodes if x.drawable):
        assert node.xy == assert_pos[node.id]
