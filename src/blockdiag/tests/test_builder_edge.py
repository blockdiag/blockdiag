# -*- coding: utf-8 -*-

from nose.tools import eq_
from utils import __build_diagram, __validate_node_attributes


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


def test_folded_edge_diagram():
    positions = {'A': (0, 0), 'B': (1, 0), 'C': (2, 0), 'D': (0, 1),
                 'E': (0, 2), 'F': (1, 1), 'Z': (0, 3)}
    __validate_node_attributes('folded_edge.diag', xy=positions)
