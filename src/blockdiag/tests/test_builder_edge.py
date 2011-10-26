# -*- coding: utf-8 -*-

from nose.tools import eq_
from utils import stderr_wrapper, __build_diagram, __validate_node_attributes


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
            assert edge.thick == None
        elif edge.node1.id == 'F':
            assert edge.dir == 'forward'
            assert edge.color == (0, 0, 0)
            assert edge.thick == 3
        else:
            assert edge.dir == 'forward'
            assert edge.color == (255, 0, 0)  # red
            assert edge.thick == None

    positions = {'A': (0, 0), 'B': (1, 0), 'C': (2, 0),
                 'D': (0, 1), 'E': (1, 1), 'F': (0, 2), 'G': (1, 2)}
    __validate_node_attributes('edge_attribute.diag', xy=positions)


def test_folded_edge_diagram():
    positions = {'A': (0, 0), 'B': (1, 0), 'C': (2, 0), 'D': (0, 1),
                 'E': (0, 2), 'F': (1, 1), 'Z': (0, 3)}
    __validate_node_attributes('folded_edge.diag', xy=positions)


def test_skipped_edge_right_diagram():
    filename = 'skipped_edge_right.diag'
    skipped = {('A', 'B'): False, ('A', 'C'): True}
    __validate_node_attributes(filename, edge_skipped=skipped)


def test_skipped_edge_rightup_diagram():
    filename = 'skipped_edge_rightup.diag'
    skipped = {('A', 'B'): False, ('D', 'C'): True}
    __validate_node_attributes(filename, edge_skipped=skipped)


def test_skipped_edge_rightdown_diagram():
    filename = 'skipped_edge_rightdown.diag'
    skipped = {('A', 'B'): False, ('A', 'C'): True}
    __validate_node_attributes(filename, edge_skipped=skipped)


def test_skipped_edge_up_diagram():
    filename = 'skipped_edge_up.diag'
    skipped = {('C', 'A'): True}
    __validate_node_attributes(filename, edge_skipped=skipped)


def test_skipped_edge_down_diagram():
    filename = 'skipped_edge_down.diag'
    skipped = {('A', 'C'): True}
    __validate_node_attributes(filename, edge_skipped=skipped)


def test_skipped_edge_leftdown_diagram():
    filename = 'skipped_edge_leftdown.diag'
    skipped = {('A', 'B'): False, ('C', 'G'): True}
    __validate_node_attributes(filename, edge_skipped=skipped)


@stderr_wrapper
def test_skipped_edge_flowchart_rightdown_diagram():
    filename = 'skipped_edge_flowchart_rightdown.diag'
    skipped = {('A', 'B'): False, ('A', 'D'): True}
    __validate_node_attributes(filename, edge_skipped=skipped)


@stderr_wrapper
def test_skipped_edge_flowchart_rightdown2_diagram():
    filename = 'skipped_edge_flowchart_rightdown2.diag'
    skipped = {('B', 'C'): False, ('A', 'C'): True}
    __validate_node_attributes(filename, edge_skipped=skipped)


def test_skipped_edge_portrait_right_diagram():
    filename = 'skipped_edge_portrait_right.diag'
    skipped = {('A', 'C'): True}
    __validate_node_attributes(filename, edge_skipped=skipped)


def test_skipped_edge_portrait_rightdown_diagram():
    filename = 'skipped_edge_portrait_rightdown.diag'
    skipped = {('A', 'B'): False, ('A', 'E'): True}
    __validate_node_attributes(filename, edge_skipped=skipped)


def test_skipped_edge_portrait_leftdown_diagram():
    filename = 'skipped_edge_portrait_leftdown.diag'
    skipped = {('A', 'B'): False, ('D', 'C'): True}
    __validate_node_attributes(filename, edge_skipped=skipped)


def test_skipped_edge_portrait_down_diagram():
    filename = 'skipped_edge_portrait_down.diag'
    skipped = {('A', 'B'): False, ('A', 'C'): True}
    __validate_node_attributes(filename, edge_skipped=skipped)


@stderr_wrapper
def test_skipped_edge_portrait_flowchart_rightdown_diagram():
    filename = 'skipped_edge_portrait_flowchart_rightdown.diag'
    skipped = {('A', 'B'): False, ('A', 'D'): True}
    __validate_node_attributes(filename, edge_skipped=skipped)


@stderr_wrapper
def test_skipped_edge_portrait_flowchart_rightdown2_diagram():
    filename = 'skipped_edge_portrait_flowchart_rightdown2.diag'
    skipped = {('B', 'C'): False, ('A', 'C'): True}
    __validate_node_attributes(filename, edge_skipped=skipped)
