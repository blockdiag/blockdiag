# -*- coding: utf-8 -*-

from nose.tools import eq_
from utils import __build_diagram, __validate_node_attributes


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


def test_multiple_node_relation_diagram():
    positions = {'A': (0, 0), 'B': (1, 0), 'C': (1, 1),
                 'D': (2, 0), 'Z': (0, 2)}
    __validate_node_attributes('multiple_node_relation.diag', xy=positions)


def test_node_attribute():
    labels = {'A': 'B', 'B': 'double quoted', 'C': 'single quoted',
              'D': '\'"double" quoted\'', 'E': '"\'single\' quoted"',
              'F': 'F', 'G': 'G', 'H': 'H'}
    colors = {'A': (255, 0, 0), 'B': (255, 255, 255), 'C': (255, 0, 0),
              'D': (255, 0, 0), 'E': (255, 0, 0), 'F': (255, 255, 255),
              'G': (255, 255, 255), 'H': (255, 255, 255)}
    textcolors = {'A': (0, 0, 0), 'B': (0, 0, 0), 'C': (0, 0, 0),
                  'D': (0, 0, 0), 'E': (0, 0, 0), 'F': (255, 0, 0),
                  'G': (0, 0, 0), 'H': (0, 0, 0)}
    numbered = {'A': None, 'B': None, 'C': None, 'D': None,
                'E': '1', 'F': None, 'G': None, 'H': None}
    stacked = {'A': False, 'B': False, 'C': False, 'D': False,
               'E': False, 'F': False, 'G': True, 'H': False}
    fontsize = {'A': None, 'B': None, 'C': None, 'D': None,
                'E': None, 'F': None, 'G': None, 'H': 16}
    __validate_node_attributes('node_attribute.diag', label=labels,
                               color=colors, textcolor=textcolors,
                               numbered=numbered, stacked=stacked,
                               fontsize=fontsize)


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


def test_flowable_node_diagram():
    positions = {'A': (0, 0), 'B': (1, 0), 'C': (2, 0), 'Z': (0, 1)}
    __validate_node_attributes('flowable_node.diag', xy=positions)
