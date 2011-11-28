# -*- coding: utf-8 -*-

from nose.tools import eq_
from utils import __build_diagram, __validate_node_attributes


def test_diagram_attributes():
    diagram = __build_diagram('diagram_attributes.diag')

    eq_(160, diagram.node_width)
    eq_(160, diagram.node_height)
    eq_(32, diagram.span_width)
    eq_(32, diagram.span_height)
    eq_((128, 128, 128), diagram.linecolor)       # gray
    eq_('diamond', diagram.nodes[0].shape)
    eq_((255, 0, 0), diagram.nodes[0].color)      # red
    eq_((0, 128, 0), diagram.nodes[0].textcolor)  # green
    eq_(16, diagram.nodes[0].fontsize)
    eq_((0, 0, 255), diagram.nodes[1].color)      # blue
    eq_((0, 128, 0), diagram.nodes[1].textcolor)  # green
    eq_(16, diagram.nodes[1].fontsize)

    eq_((128, 128, 128), diagram.edges[0].color)  # gray
    eq_((0, 128, 0), diagram.edges[0].textcolor)  # green
    eq_(16, diagram.edges[0].fontsize)


def test_diagram_attributes_order_diagram():
    colors = {'A': (255, 0, 0), 'B': (255, 0, 0)}
    linecolors = {'A': (255, 0, 0), 'B': (255, 0, 0)}
    __validate_node_attributes('diagram_attributes_order.diag',
                               color=colors, linecolor=linecolors)


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


def test_diagram_orientation_diagram():
    positions = {'A': (0, 0), 'B': (0, 1), 'C': (0, 2),
                 'D': (1, 2), 'Z': (2, 0)}
    __validate_node_attributes('diagram_orientation.diag', xy=positions)


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


def test_non_rhombus_relation_height_diagram():
    positions = {'A': (0, 0), 'B': (1, 0), 'C': (2, 0), 'D': (0, 1),
                 'E': (0, 2), 'F': (1, 2), 'G': (1, 3), 'H': (2, 3),
                 'I': (2, 4), 'J': (1, 5), 'K': (2, 5), 'Z': (0, 6)}
    __validate_node_attributes('non_rhombus_relation_height.diag',
                               xy=positions)


def test_define_class_diagram():
    colors = {'A': (255, 0, 0), 'B': (255, 255, 255), 'C': (255, 255, 255)}
    styles = {'A': 'dashed', 'B': None, 'C': None}

    edge_colors = {('A', 'B'): (255, 0, 0), ('B', 'C'): (0, 0, 0)}
    edge_styles = {('A', 'B'): 'dashed', ('B', 'C'): None}

    __validate_node_attributes('define_class.diag',
                               color=colors, edge_color=edge_colors,
                               style=styles, edge_style=edge_styles)
