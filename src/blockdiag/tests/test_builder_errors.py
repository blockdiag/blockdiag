# -*- coding: utf-8 -*-

import tempfile
from blockdiag.builder import *
from blockdiag.elements import *
from blockdiag.diagparser import *
from nose.tools import raises


def __build_diagram(filename):
    import os
    testdir = os.path.dirname(__file__)
    pathname = "%s/diagrams/%s" % (testdir, filename)

    str = open(pathname).read()
    tree = parse(tokenize(str))
    return ScreenNodeBuilder.build(tree)


@raises(AttributeError)
def test_unknown_diagram_default_shape_diagram():
    diagram = __build_diagram('errors/unknown_diagram_default_shape.diag')


@raises(AttributeError)
def test_unknown_diagram_edge_layout_diagram():
    diagram = __build_diagram('errors/unknown_diagram_edge_layout.diag')


@raises(AttributeError)
def test_unknown_diagram_orientation_diagram():
    diagram = __build_diagram('errors/unknown_diagram_orientation.diag')


@raises(AttributeError)
def test_unknown_node_shape_diagram():
    diagram = __build_diagram('errors/unknown_node_shape.diag')


@raises(AttributeError)
def test_unknown_node_attribute_diagram():
    diagram = __build_diagram('errors/unknown_node_attribute.diag')


@raises(AttributeError)
def test_unknown_node_style_diagram():
    diagram = __build_diagram('errors/unknown_node_style.diag')


@raises(AttributeError)
def test_unknown_edge_dir_diagram():
    diagram = __build_diagram('errors/unknown_edge_dir.diag')


@raises(AttributeError)
def test_unknown_edge_style_diagram():
    diagram = __build_diagram('errors/unknown_edge_style.diag')


@raises(AttributeError)
def test_unknown_edge_hstyle_diagram():
    diagram = __build_diagram('errors/unknown_edge_hstyle.diag')


@raises(RuntimeError)
def test_belongs_to_two_groups_diagram():
    diagram = __build_diagram('errors/belongs_to_two_groups.diag')


@raises(NoParseError)
def test_node_follows_group_diagram():
    diagram = __build_diagram('errors/node_follows_group.diag')


@raises(NoParseError)
def test_group_follows_node_diagram():
    diagram = __build_diagram('errors/group_follows_node.diag')
