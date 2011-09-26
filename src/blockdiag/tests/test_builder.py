# -*- coding: utf-8 -*-

import tempfile
from blockdiag.builder import *
from blockdiag.elements import *
from blockdiag.diagparser import *


def __build_diagram(filename):
    import os
    testdir = os.path.dirname(__file__)
    pathname = "%s/diagrams/%s" % (testdir, filename)

    str = open(pathname).read()
    tree = parse(tokenize(str))
    return ScreenNodeBuilder.build(tree)


def test_diagram_attributes():
    screen = __build_diagram('diagram_attributes.diag')

    assert screen.node_width == 160
    assert screen.node_height == 160
    assert screen.span_width == 32
    assert screen.span_height == 32
    assert screen.fontsize == 16
    assert screen.linecolor == (128, 128, 128)  # gray
    assert screen.nodes[0].shape == 'diamond'
    assert screen.nodes[0].color == (255, 0, 0)  # red
    assert screen.nodes[1].color == (0, 0, 255)  # blue

    assert DiagramEdge.basecolor == (128, 128, 128)  # gray


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
                    'P': 'actor', 'Q': 'flowchart.terminator', 'R': 'textbox',
                    'S': 'dots', 'T': 'none', 'Z': 'box'}
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


def test_quoted_node_id_diagram():
    screen = __build_diagram('quoted_node_id.diag')

    assert_pos = {'A': (0, 0), "'A'": (1, 0), 'B': (2, 0), 'Z': (0, 1)}
    for node in screen.nodes:
        assert node.xy == assert_pos[node.id]


def test_node_id_includes_dot_diagram():
    screen = __build_diagram('node_id_includes_dot.diag')

    assert_pos = {'A.B': (0, 0), 'C.D': (1, 0), 'Z': (0, 1)}
    for node in screen.nodes:
        assert node.xy == assert_pos[node.id]


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


def test_multiple_node_relation_diagram():
    screen = __build_diagram('multiple_node_relation.diag')

    assert_pos = {'A': (0, 0), 'B': (1, 0), 'C': (1, 1),
                  'D': (2, 0), 'Z': (0, 2)}
    for node in screen.nodes:
        assert node.xy == assert_pos[node.id]


def test_node_attribute():
    screen = __build_diagram('node_attribute.diag')

    assert screen.nodes[0].id == 'A'
    assert screen.nodes[0].label == 'B'
    assert screen.nodes[0].color == (255, 0, 0)
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
    assert screen.nodes[4].numbered == '1'


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
            assert edge.color == (0, 0, 0)
        else:
            assert edge.dir == 'forward'
            assert edge.color == (255, 0, 0)  # red


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


def test_circular_ref_and_parent_node_diagram():
    screen = __build_diagram('circular_ref_and_parent_node.diag')

    assert_pos = {'A': (0, 0), 'B': (1, 0), 'C': (1, 1),
                  'D': (2, 1), 'Z': (0, 2)}
    for node in screen.nodes:
        assert node.xy == assert_pos[node.id]


def test_labeled_circular_ref_diagram():
    screen = __build_diagram('labeled_circular_ref.diag')

    assert_pos = {'A': (0, 0), 'B': (2, 0), 'C': (1, 0),
                  'Z': (0, 1)}
    for node in screen.nodes:
        assert node.xy == assert_pos[node.id]


def test_twin_forked_diagram():
    screen = __build_diagram('twin_forked.diag')

    assert_pos = {'A': (0, 0), 'B': (1, 0), 'C': (1, 2), 'D': (2, 0),
                  'E': (3, 0), 'F': (3, 1), 'G': (4, 1), 'Z': (0, 3)}
    for node in screen.nodes:
        print node, assert_pos[node.id]
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

    assert_pos = {'A': (0, 0), 'B': (1, 1), 'C': (2, 0),
                  'Z': (0, 2)}
    for node in (x for x in screen.nodes if x.drawable):
        assert node.xy == assert_pos[node.id]


def test_skipped_twin_circular_diagram():
    screen = __build_diagram('skipped_twin_circular.diag')

    assert_pos = {'A': (0, 0), 'B': (1, 0), 'C': (2, 1),
                  'D': (2, 2), 'E': (3, 0), 'Z': (0, 3)}
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


def test_empty_group_declaration_diagram():
    screen = __build_diagram('empty_group_declaration.diag')

    assert_pos = {'A': (0, 0), 'Z': (0, 1)}
    for node in (x for x in screen.nodes if x.drawable):
        assert node.xy == assert_pos[node.id]


def test_simple_group_diagram():
    screen = __build_diagram('simple_group.diag')

    assert_pos = {'A': (0, 0), 'B': (1, 0), 'C': (1, 1),
                  'Z': (0, 2)}
    for node in (x for x in screen.nodes if x.drawable):
        assert node.xy == assert_pos[node.id]


def test_group_declare_as_node_attribute_diagram():
    screen = __build_diagram('group_declare_as_node_attribute.diag')

    assert_pos = {'A': (0, 0), 'B': (1, 0), 'C': (2, 0),
                  'D': (2, 1), 'E': (2, 2), 'Z': (0, 3)}
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
    assert_colors = {'A': (255, 0, 0), 'B': '#888888', 'C': (0, 0, 255),
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


def test_group_children_height_diagram():
    screen = __build_diagram('group_children_height.diag')

    assert_pos = {'A': (0, 0), 'B': (1, 0), 'C': (1, 1), 'D': (1, 2),
                  'E': (2, 0), 'F': (2, 2), 'Z': (0, 3)}
    for node in (x for x in screen.nodes if x.drawable):
        assert node.xy == assert_pos[node.id]


def test_group_children_order_diagram():
    screen = __build_diagram('group_children_order.diag')

    assert_pos = {'A': (0, 0), 'B': (1, 0), 'C': (1, 1), 'D': (1, 2),
                  'E': (2, 0), 'F': (2, 1), 'G': (2, 2), 'Z': (0, 3)}
    for node in (x for x in screen.nodes if x.drawable):
        assert node.xy == assert_pos[node.id]


def test_group_children_order2_diagram():
    screen = __build_diagram('group_children_order2.diag')

    assert_pos = {'A': (0, 0), 'B': (1, 0), 'C': (1, 1), 'D': (1, 2),
                  'E': (2, 1), 'F': (2, 0), 'G': (2, 2), 'Z': (0, 3)}
    for node in (x for x in screen.nodes if x.drawable):
        assert node.xy == assert_pos[node.id]


def test_group_children_order3_diagram():
    screen = __build_diagram('group_children_order3.diag')

    assert_pos = {'A': (0, 0), 'B': (1, 0), 'C': (1, 1), 'D': (1, 2),
                  'E': (2, 0), 'F': (2, 1), 'G': (2, 2), 'Q': (0, 3),
                  'Z': (0, 4)}
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


def test_diagram_orientation_diagram():
    screen = __build_diagram('diagram_orientation.diag')

    assert_pos = {'A': (0, 0), 'B': (0, 1), 'C': (0, 2),
                  'D': (1, 2), 'Z': (2, 0)}
    for node in (x for x in screen.nodes if x.drawable):
        assert node.xy == assert_pos[node.id]


def test_group_orientation_diagram():
    screen = __build_diagram('group_orientation.diag')

    assert_pos = {'A': (0, 0), 'B': (1, 0), 'C': (1, 1),
                  'D': (2, 1), 'Z': (0, 2)}
    for node in (x for x in screen.nodes if x.drawable):
        assert node.xy == assert_pos[node.id]


def test_nested_group_orientation_diagram():
    screen = __build_diagram('nested_group_orientation.diag')

    assert_pos = {'A': (0, 0), 'B': (0, 1), 'C': (1, 0),
                  'Z': (0, 2)}
    for node in (x for x in screen.nodes if x.drawable):
        assert node.xy == assert_pos[node.id]


def test_nested_group_orientation2_diagram():
    screen = __build_diagram('nested_group_orientation2.diag')

    assert_pos = {'A': (0, 0), 'B': (0, 1), 'C': (0, 2), 'D': (1, 2),
                  'E': (2, 2), 'F': (2, 3), 'Z': (3, 0)}
    for node in (x for x in screen.nodes if x.drawable):
        print node, assert_pos[node.id]
        assert node.xy == assert_pos[node.id]


def test_slided_children_diagram():
    screen = __build_diagram('slided_children.diag')

    assert_pos = {'A': (0, 0), 'B': (1, 0), 'C': (2, 0), 'D': (1, 3),
                  'E': (2, 3), 'F': (3, 2), 'G': (2, 1), 'H': (4, 1)}
    for node in (x for x in screen.nodes if x.drawable):
        print node, assert_pos[node.id]
        assert node.xy == assert_pos[node.id]


def test_rhombus_relation_height_diagram():
    screen = __build_diagram('rhombus_relation_height.diag')

    assert_pos = {'A': (0, 0), 'B': (1, 0), 'C': (1, 1), 'D': (2, 0),
                  'E': (3, 0), 'F': (3, 1), 'Z': (0, 2)}
    for node in (x for x in screen.nodes if x.drawable):
        print node, assert_pos[node.id]
        assert node.xy == assert_pos[node.id]
