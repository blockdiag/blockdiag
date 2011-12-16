# -*- coding: utf-8 -*-

import tempfile
from blockdiag.builder import *
from blockdiag.elements import *
from blockdiag.parser import parse_string


def __build_diagram(filename):
    import os
    testdir = os.path.dirname(__file__)
    pathname = "%s/diagrams/%s" % (testdir, filename)

    str = open(pathname).read()
    tree = parse_string(str)
    return SeparateDiagramBuilder.build(tree)


def test_separate1_diagram():
    diagram = __build_diagram('separate1.diag')

    assert_pos = {0: {'B': (0, 0), 'C': (1, 0), 'D': (4, 0),
                      'E': (2, 0), 'F': (3, 0)},
                  1: {'A': (0, 0), 'B': (1, 0), 'D': (3, 0)},
                  2: {'A': (0, 0), 'Z': (0, 1)}}

    for i, diagram in enumerate(diagram):
        for node in diagram.traverse_nodes():
            if isinstance(node, DiagramNode):
                print node, assert_pos[i][node.id]
                assert node.xy == assert_pos[i][node.id]


def test_separate2_diagram():
    diagram = __build_diagram('separate2.diag')

    assert_pos = {0: {'A': (0, 0), 'C': (1, 0), 'D': (2, 0),
                      'E': (0, 2), 'G': (3, 0), 'H': (3, 1)},
                  1: {'A': (0, 0), 'B': (1, 0), 'E': (2, 0),
                      'F': (4, 2), 'G': (4, 0), 'H': (4, 1)},
                  2: {'A': (0, 0), 'F': (2, 2), 'G': (2, 0),
                      'H': (2, 1), 'Z': (0, 3)}}

    for i, diagram in enumerate(diagram):
        for node in diagram.traverse_nodes():
            if isinstance(node, DiagramNode):
                print node, assert_pos[i][node.id]
                assert node.xy == assert_pos[i][node.id]
