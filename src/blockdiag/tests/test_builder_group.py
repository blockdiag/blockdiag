# -*- coding: utf-8 -*-

from nose.tools import eq_
from utils import __build_diagram, __validate_node_attributes


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
        node.shape = 'line'


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


def test_group_children_order4_diagram():
    positions = {'A': (0, 0), 'B': (1, 0), 'C': (1, 1), 'D': (1, 2),
                 'E': (2, 0), 'Z': (0, 3)}
    __validate_node_attributes('group_children_order4.diag', xy=positions)


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


def test_group_orientation_diagram():
    positions = {'A': (0, 0), 'B': (1, 0), 'C': (1, 1),
                 'D': (2, 1), 'Z': (0, 2)}
    __validate_node_attributes('group_orientation.diag', xy=positions)


def test_nested_group_orientation_diagram():
    positions = {'A': (0, 0), 'B': (0, 1), 'C': (1, 0), 'Z': (0, 2)}
    __validate_node_attributes('nested_group_orientation.diag', xy=positions)
