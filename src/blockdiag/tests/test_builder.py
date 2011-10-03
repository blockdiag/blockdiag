# -*- coding: utf-8 -*-

import tempfile
from nose.tools import eq_
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


def __validate_node_attributes(filename, **kwargs):
    diagram = __build_diagram(filename)

    for name, values in kwargs.items():
        print "[node.%s]" % name
        for node in (n for n in diagram.nodes  if n.drawable):
            print node
            value = getattr(node, name)
            eq_(values[node.id], value)


def test_diagram_attributes():
    diagram = __build_diagram('diagram_attributes.diag')

    eq_(160, diagram.node_width)
    eq_(160, diagram.node_height)
    eq_(32, diagram.span_width)
    eq_(32, diagram.span_height)
    eq_(16, diagram.fontsize)
    eq_((128, 128, 128), diagram.linecolor)       # gray
    eq_('diamond', diagram.nodes[0].shape)
    eq_((255, 0, 0), diagram.nodes[0].color)      # red
    eq_((0, 128, 0), diagram.nodes[0].textcolor)  # green
    eq_((0, 0, 255), diagram.nodes[1].color)      # blue
    eq_((0, 128, 0), diagram.nodes[1].textcolor)  # green

    eq_((128, 128, 128), diagram.edges[0].color)  # gray
    eq_((0, 128, 0), diagram.edges[0].textcolor)  # green


def test_single_node_diagram():
    diagram = __build_diagram('single_node.diag')

    assert len(diagram.nodes) == 1
    assert len(diagram.edges) == 0
    assert diagram.nodes[0].label == 'A'
    assert diagram.nodes[0].xy == (0, 0)


def test_node_shape_diagram():
    shapes = {'A': 'box', 'B': 'roundedbox', 'C': 'diamond',
              'D': 'ellipse', 'E': 'note', 'F': 'cloud',
              'G': 'mail', 'H': 'beginpoint', 'I': 'endpoint',
              'J': 'minidiamond', 'K': 'flowchart.condition',
              'L': 'flowchart.database', 'M': 'flowchart.input',
              'N': 'flowchart.loopin', 'O': 'flowchart.loopout',
              'P': 'actor', 'Q': 'flowchart.terminator', 'R': 'textbox',
              'S': 'dots', 'T': 'none', 'Z': 'box'}
    __validate_node_attributes('node_shape.diag', shape=shapes)


def test_node_shape_namespace_diagram():
    shapes = {'A': 'flowchart.condition', 'B': 'condition', 'Z': 'box'}
    __validate_node_attributes('node_shape_namespace.diag', shape=shapes)


def test_node_has_multilined_label_diagram():
    positions = {'A': (0, 0), 'Z': (0, 1)}
    labels = {'A': "foo\nbar", 'Z': 'Z'}
    __validate_node_attributes('node_has_multilined_label.diag',
                               xy=positions, label=labels)


def test_quoted_node_id_diagram():
    positions = {'A': (0, 0), "'A'": (1, 0), 'B': (2, 0), 'Z': (0, 1)}
    __validate_node_attributes('quoted_node_id.diag', xy=positions)


def test_node_id_includes_dot_diagram():
    positions = {'A.B': (0, 0), 'C.D': (1, 0), 'Z': (0, 1)}
    __validate_node_attributes('node_id_includes_dot.diag', xy=positions)


def test_single_edge_diagram():
    diagram = __build_diagram('single_edge.diag')

    assert len(diagram.nodes) == 2
    assert len(diagram.edges) == 1

    positions = {'A': (0, 0), 'B': (1, 0)}
    labels = {'A': 'A', 'B': 'B'}
    __validate_node_attributes('single_edge.diag', xy=positions, label=labels)


def test_two_edges_diagram():
    diagram = __build_diagram('two_edges.diag')

    assert len(diagram.nodes) == 3
    assert len(diagram.edges) == 2

    positions = {'A': (0, 0), 'B': (1, 0), 'C': (2, 0)}
    __validate_node_attributes('two_edges.diag', xy=positions)


def test_multiple_node_relation_diagram():
    positions = {'A': (0, 0), 'B': (1, 0), 'C': (1, 1),
                 'D': (2, 0), 'Z': (0, 2)}
    __validate_node_attributes('multiple_node_relation.diag', xy=positions)


def test_node_attribute():
    labels = {'A': 'B', 'B': 'double quoted', 'C': 'single quoted',
              'D': '\'"double" quoted\'', 'E': '"\'single\' quoted"',
              'F': 'F', 'G': 'G'}
    colors = {'A': (255, 0, 0), 'B': (255, 255, 255), 'C': (255, 0, 0),
              'D': (255, 0, 0), 'E': (255, 0, 0), 'F': (255, 255, 255),
              'G': (255, 255, 255)}
    textcolors = {'A': (0, 0, 0), 'B': (0, 0, 0), 'C': (0, 0, 0),
                  'D': (0, 0, 0), 'E': (0, 0, 0), 'F': (255, 0, 0),
                  'G': (0, 0, 0)}
    numbered = {'A': None, 'B': None, 'C': None, 'D': None,
                'E': '1', 'F': None, 'G': None}
    stacked = {'A': False, 'B': False, 'C': False, 'D': False,
               'E': False, 'F': False, 'G': True}
    __validate_node_attributes('node_attribute.diag', label=labels,
                               color=colors, textcolor=textcolors,
                               numbered=numbered, stacked=stacked)


def test_edge_shape():
    diagram = __build_diagram('edge_shape.diag')

    for edge in diagram.edges:
        if edge.node1.id == 'A':
            assert edge.dir == 'none'
        elif edge.node1.id == 'B':
            assert edge.dir == 'forward'
        elif edge.node1.id == 'C':
            assert edge.dir == 'back'
        elif edge.node1.id == 'D':
            assert edge.dir == 'both'


def test_edge_attribute():
    diagram = __build_diagram('edge_attribute.diag')

    for edge in diagram.edges:
        if edge.node1.id == 'D':
            assert edge.dir == 'none'
            assert edge.color == (0, 0, 0)
        else:
            assert edge.dir == 'forward'
            assert edge.color == (255, 0, 0)  # red

    positions = {'A': (0, 0), 'B': (1, 0), 'C': (2, 0),
                 'D': (0, 1), 'E': (1, 1)}
    __validate_node_attributes('edge_attribute.diag', xy=positions)


def test_node_height_diagram():
    positions = {'A': (0, 0), 'B': (1, 0), 'C': (2, 0),
                 'D': (2, 1), 'E': (1, 1), 'Z': (0, 2)}
    __validate_node_attributes('node_height.diag', xy=positions)


def test_branched_diagram():
    positions = {'A': (0, 0), 'B': (1, 0), 'C': (2, 0),
                 'D': (1, 1), 'E': (2, 1), 'Z': (0, 2)}
    __validate_node_attributes('branched.diag', xy=positions)


def test_multiple_parent_node_diagram():
    positions = {'A': (0, 0), 'B': (1, 0), 'C': (0, 2),
                 'D': (1, 2), 'E': (0, 1), 'Z': (0, 3)}
    __validate_node_attributes('multiple_parent_node.diag', xy=positions)


def test_twin_multiple_parent_node_diagram():
    positions = {'A': (0, 0), 'B': (1, 0), 'C': (0, 1),
                 'D': (1, 1), 'E': (0, 2), 'Z': (0, 3)}
    __validate_node_attributes('twin_multiple_parent_node.diag', xy=positions)


def test_circular_ref_to_root_diagram():
    positions = {'A': (0, 0), 'B': (1, 0), 'C': (2, 0),
                  'D': (2, 1), 'Z': (0, 2)}
    __validate_node_attributes('circular_ref_to_root.diag', xy=positions)


def test_circular_ref_diagram():
    positions = {'A': (0, 0), 'B': (1, 0), 'C': (2, 0),
                  'D': (2, 1), 'Z': (0, 2)}
    __validate_node_attributes('circular_ref.diag', xy=positions)


def test_circular_ref_and_parent_node_diagram():
    positions = {'A': (0, 0), 'B': (1, 0), 'C': (1, 1),
                 'D': (2, 1), 'Z': (0, 2)}
    __validate_node_attributes('circular_ref_and_parent_node.diag',
                               xy=positions)


def test_labeled_circular_ref_diagram():
    positions = {'A': (0, 0), 'B': (2, 0), 'C': (1, 0),
                 'Z': (0, 1)}
    __validate_node_attributes('labeled_circular_ref.diag', xy=positions)


def test_twin_forked_diagram():
    positions = {'A': (0, 0), 'B': (1, 0), 'C': (1, 2), 'D': (2, 0),
                  'E': (3, 0), 'F': (3, 1), 'G': (4, 1), 'Z': (0, 3)}
    __validate_node_attributes('twin_forked.diag', xy=positions)


def test_skipped_edge_diagram():
    positions = {'A': (0, 0), 'B': (1, 0), 'C': (2, 0), 'Z': (0, 1)}
    __validate_node_attributes('skipped_edge.diag', xy=positions)


def test_circular_skipped_edge_diagram():
    positions = {'A': (0, 0), 'B': (1, 0), 'C': (2, 0), 'Z': (0, 1)}
    __validate_node_attributes('circular_skipped_edge.diag', xy=positions)


def test_triple_branched_diagram():
    positions = {'A': (0, 0), 'B': (0, 1), 'C': (0, 2),
                 'D': (1, 0), 'Z': (0, 3)}
    __validate_node_attributes('triple_branched.diag', xy=positions)


def test_twin_circular_ref_to_root_diagram():
    positions = {'A': (0, 0), 'B': (1, 0), 'C': (1, 1), 'Z': (0, 2)}
    __validate_node_attributes('twin_circular_ref_to_root.diag', xy=positions)


def test_twin_circular_ref_diagram():
    positions = {'A': (0, 0), 'B': (1, 0), 'C': (2, 0),
                 'D': (1, 1), 'Z': (0, 2)}
    __validate_node_attributes('twin_circular_ref.diag', xy=positions)


def test_skipped_circular_diagram():
    positions = {'A': (0, 0), 'B': (1, 1), 'C': (2, 0),
                 'Z': (0, 2)}
    __validate_node_attributes('skipped_circular.diag', xy=positions)


def test_skipped_twin_circular_diagram():
    positions = {'A': (0, 0), 'B': (1, 0), 'C': (2, 1),
                 'D': (2, 2), 'E': (3, 0), 'Z': (0, 3)}
    __validate_node_attributes('skipped_twin_circular.diag', xy=positions)


def test_nested_skipped_circular_diagram():
    positions = {'A': (0, 0), 'B': (1, 0), 'C': (2, 1),
                 'D': (3, 2), 'E': (4, 1), 'F': (5, 0),
                 'G': (6, 0), 'Z': (0, 3)}
    __validate_node_attributes('nested_skipped_circular.diag', xy=positions)


def test_self_ref_diagram():
    positions = {'A': (0, 0), 'B': (1, 0), 'Z': (0, 1)}
    __validate_node_attributes('self_ref.diag', xy=positions)


def test_folded_edge_diagram():
    positions = {'A': (0, 0), 'B': (1, 0), 'C': (2, 0), 'D': (0, 1),
                 'E': (0, 2), 'F': (1, 1), 'Z': (0, 3)}
    __validate_node_attributes('folded_edge.diag', xy=positions)


def test_flowable_node_diagram():
    positions = {'A': (0, 0), 'B': (1, 0), 'C': (2, 0), 'Z': (0, 1)}
    __validate_node_attributes('flowable_node.diag', xy=positions)


def test_nested_groups_diagram():
    positions = {'A': (0, 0), 'B': (0, 1), 'Z': (0, 2)}
    __validate_node_attributes('nested_groups.diag', xy=positions)


def test_nested_groups_and_edges_diagram():
    positions = {'A': (0, 0), 'B': (1, 0), 'C': (2, 0), 'Z': (0, 1)}
    __validate_node_attributes('nested_groups_and_edges.diag', xy=positions)


def test_empty_group_diagram():
    positions = {'Z': (0, 0)}
    __validate_node_attributes('empty_group.diag', xy=positions)


def test_empty_nested_group_diagram():
    positions = {'Z': (0, 0)}
    __validate_node_attributes('empty_nested_group.diag', xy=positions)


def test_empty_group_declaration_diagram():
    positions = {'A': (0, 0), 'Z': (0, 1)}
    __validate_node_attributes('empty_group_declaration.diag', xy=positions)


def test_simple_group_diagram():
    positions = {'A': (0, 0), 'B': (1, 0), 'C': (1, 1), 'Z': (0, 2)}
    __validate_node_attributes('simple_group.diag', xy=positions)


def test_group_declare_as_node_attribute_diagram():
    positions = {'A': (0, 0), 'B': (1, 0), 'C': (2, 0),
                  'D': (2, 1), 'E': (2, 2), 'Z': (0, 3)}
    __validate_node_attributes('group_declare_as_node_attribute.diag',
                               xy=positions)


def test_group_attribute():
    diagram = __build_diagram('group_attribute.diag')

    for node in (x for x in diagram.nodes if not x.drawable):
        node.color = 'red'
        node.label = 'group label'


def test_merge_groups_diagram():
    positions = {'A': (0, 0), 'B': (1, 0), 'C': (0, 1),
                 'D': (1, 1), 'Z': (0, 2)}
    __validate_node_attributes('merge_groups.diag', xy=positions)


def test_node_attribute_and_group_diagram():
    positions = {'A': (0, 0), 'B': (1, 0), 'C': (2, 0), 'Z': (0, 1)}
    labels = {'A': 'foo', 'B': 'bar', 'C': 'baz', 'Z': 'Z'}
    colors = {'A': (255, 0, 0), 'B': '#888888', 'C': (0, 0, 255),
              'Z': (255, 255, 255)}
    __validate_node_attributes('node_attribute_and_group.diag',
                               xy=positions, label=labels, color=colors)


def test_group_sibling_diagram():
    positions = {'A': (0, 0), 'B': (1, 0), 'C': (1, 2), 'D': (2, 0),
                 'E': (2, 1), 'F': (2, 2), 'Z': (0, 3)}
    __validate_node_attributes('group_sibling.diag', xy=positions)


def test_group_order_diagram():
    positions = {'A': (0, 0), 'B': (1, 0), 'C': (1, 1), 'Z': (0, 2)}
    __validate_node_attributes('group_order.diag', xy=positions)


def test_group_order2_diagram():
    positions = {'A': (0, 0), 'B': (1, 0), 'C': (1, 1),
                 'D': (2, 1), 'E': (1, 2), 'F': (2, 2), 'Z': (0, 3)}
    __validate_node_attributes('group_order2.diag', xy=positions)


def test_group_order3_diagram():
    positions = {'A': (0, 0), 'B': (1, 0), 'C': (2, 0),
                 'D': (2, 1), 'E': (1, 2), 'Z': (0, 3)}
    __validate_node_attributes('group_order3.diag', xy=positions)


def test_group_children_height_diagram():
    positions = {'A': (0, 0), 'B': (1, 0), 'C': (1, 1), 'D': (1, 2),
                 'E': (2, 0), 'F': (2, 2), 'Z': (0, 3)}
    __validate_node_attributes('group_children_height.diag', xy=positions)


def test_group_children_order_diagram():
    positions = {'A': (0, 0), 'B': (1, 0), 'C': (1, 1), 'D': (1, 2),
                 'E': (2, 0), 'F': (2, 1), 'G': (2, 2), 'Z': (0, 3)}
    __validate_node_attributes('group_children_order.diag', xy=positions)


def test_group_children_order2_diagram():
    positions = {'A': (0, 0), 'B': (1, 0), 'C': (1, 1), 'D': (1, 2),
                 'E': (2, 1), 'F': (2, 0), 'G': (2, 2), 'Z': (0, 3)}
    __validate_node_attributes('group_children_order2.diag', xy=positions)


def test_group_children_order3_diagram():
    positions = {'A': (0, 0), 'B': (1, 0), 'C': (1, 1), 'D': (1, 2),
                 'E': (2, 0), 'F': (2, 1), 'G': (2, 2), 'Q': (0, 3),
                 'Z': (0, 4)}
    __validate_node_attributes('group_children_order3.diag', xy=positions)


def test_node_in_group_follows_outer_node_diagram():
    positions = {'A': (0, 0), 'B': (1, 0), 'C': (2, 0), 'Z': (0, 1)}
    __validate_node_attributes('node_in_group_follows_outer_node.diag',
                               xy=positions)


def test_group_id_and_node_id_are_not_conflicted_diagram():
    positions = {'A': (0, 0), 'B': (1, 0), 'C': (0, 1),
                 'D': (1, 1), 'Z': (0, 2)}
    __validate_node_attributes('group_id_and_node_id_are_not_conflicted.diag',
                               xy=positions)


def test_outer_node_follows_node_in_group_diagram():
    positions = {'A': (0, 0), 'B': (1, 0), 'C': (2, 0), 'Z': (0, 1)}
    __validate_node_attributes('outer_node_follows_node_in_group.diag',
                               xy=positions)


def test_large_group_and_node_diagram():
    positions = {'A': (0, 0), 'B': (1, 0), 'C': (1, 1), 'D': (1, 2),
                 'E': (1, 3), 'F': (2, 0), 'Z': (0, 4)}
    __validate_node_attributes('large_group_and_node.diag', xy=positions)


def test_large_group_and_node2_diagram():
    positions = {'A': (0, 0), 'B': (1, 0), 'C': (2, 0), 'D': (3, 0),
                 'E': (4, 0), 'F': (5, 0), 'Z': (0, 1)}
    __validate_node_attributes('large_group_and_node2.diag', xy=positions)


def test_large_group_and_two_nodes_diagram():
    positions = {'A': (0, 0), 'B': (1, 0), 'C': (1, 1), 'D': (1, 2),
                 'E': (1, 3), 'F': (2, 0), 'G': (2, 1), 'Z': (0, 4)}
    __validate_node_attributes('large_group_and_two_nodes.diag', xy=positions)


def test_group_height_diagram():
    positions = {'A': (0, 0), 'B': (1, 0), 'C': (2, 0),
                 'D': (2, 1), 'E': (1, 2), 'Z': (0, 3)}
    __validate_node_attributes('group_height.diag', xy=positions)


def test_multiple_groups_diagram():
    positions = {'A': (0, 0), 'B': (0, 1), 'C': (0, 2), 'D': (0, 3),
                 'E': (1, 0), 'F': (1, 1), 'G': (1, 2), 'H': (2, 0),
                 'I': (2, 1), 'J': (3, 0), 'Z': (0, 4)}
    __validate_node_attributes('multiple_groups.diag', xy=positions)


def test_multiple_nested_groups_diagram():
    positions = {'A': (0, 0), 'B': (1, 0), 'C': (1, 1), 'Z': (0, 2)}
    __validate_node_attributes('multiple_nested_groups.diag', xy=positions)


def test_group_works_node_decorator_diagram():
    positions = {'A': (0, 0), 'B': (1, 0), 'C': (3, 0),
                 'D': (2, 0), 'E': (1, 1), 'Z': (0, 2)}
    __validate_node_attributes('group_works_node_decorator.diag', xy=positions)


def test_nested_groups_work_node_decorator_diagram():
    positions = {'A': (0, 0), 'B': (0, 1), 'Z': (0, 2)}
    __validate_node_attributes('nested_groups_work_node_decorator.diag',
                               xy=positions)


def test_reversed_multiple_groups_diagram():
    positions = {'A': (3, 0), 'B': (3, 1), 'C': (3, 2), 'D': (3, 3),
                 'E': (2, 0), 'F': (2, 1), 'G': (2, 2), 'H': (1, 0),
                 'I': (1, 1), 'J': (0, 0), 'Z': (0, 4)}
    __validate_node_attributes('reverse_multiple_groups.diag', xy=positions)


def test_group_and_skipped_edge_diagram():
    positions = {'A': (0, 0), 'B': (1, 0), 'C': (2, 0),
                 'D': (3, 0), 'E': (1, 1), 'Z': (0, 2)}
    __validate_node_attributes('group_and_skipped_edge.diag', xy=positions)


def test_diagram_orientation_diagram():
    positions = {'A': (0, 0), 'B': (0, 1), 'C': (0, 2),
                 'D': (1, 2), 'Z': (2, 0)}
    __validate_node_attributes('diagram_orientation.diag', xy=positions)


def test_group_orientation_diagram():
    positions = {'A': (0, 0), 'B': (1, 0), 'C': (1, 1),
                 'D': (2, 1), 'Z': (0, 2)}
    __validate_node_attributes('group_orientation.diag', xy=positions)


def test_nested_group_orientation_diagram():
    positions = {'A': (0, 0), 'B': (0, 1), 'C': (1, 0), 'Z': (0, 2)}
    __validate_node_attributes('nested_group_orientation.diag', xy=positions)


def test_nested_group_orientation2_diagram():
    positions = {'A': (0, 0), 'B': (0, 1), 'C': (0, 2), 'D': (1, 2),
                 'E': (2, 2), 'F': (2, 3), 'Z': (3, 0)}
    __validate_node_attributes('nested_group_orientation2.diag', xy=positions)


def test_slided_children_diagram():
    positions = {'A': (0, 0), 'B': (1, 0), 'C': (2, 0), 'D': (1, 3),
                 'E': (2, 3), 'F': (3, 2), 'G': (2, 1), 'H': (4, 1)}
    __validate_node_attributes('slided_children.diag', xy=positions)


def test_rhombus_relation_height_diagram():
    positions = {'A': (0, 0), 'B': (1, 0), 'C': (1, 1), 'D': (2, 0),
                 'E': (3, 0), 'F': (3, 1), 'Z': (0, 2)}
    __validate_node_attributes('rhombus_relation_height.diag', xy=positions)
