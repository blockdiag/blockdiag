# -*- coding: utf-8 -*-

from blockdiag.parser import *
from nose.tools import raises
from utils import __build_diagram


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
def test_unknown_node_class_diagram():
    diagram = __build_diagram('errors/unknown_node_class.diag')


@raises(AttributeError)
def test_unknown_edge_dir_diagram():
    diagram = __build_diagram('errors/unknown_edge_dir.diag')


@raises(AttributeError)
def test_unknown_edge_style_diagram():
    diagram = __build_diagram('errors/unknown_edge_style.diag')


@raises(AttributeError)
def test_unknown_edge_hstyle_diagram():
    diagram = __build_diagram('errors/unknown_edge_hstyle.diag')


@raises(AttributeError)
def test_unknown_edge_class_diagram():
    diagram = __build_diagram('errors/unknown_edge_class.diag')


@raises(AttributeError)
def test_unknown_group_shape_diagram():
    diagram = __build_diagram('errors/unknown_group_shape.diag')


@raises(AttributeError)
def test_unknown_group_class_diagram():
    diagram = __build_diagram('errors/unknown_group_class.diag')


@raises(AttributeError)
def test_unknown_group_orientation_diagram():
    diagram = __build_diagram('errors/unknown_group_orientation.diag')


@raises(RuntimeError)
def test_belongs_to_two_groups_diagram():
    diagram = __build_diagram('errors/belongs_to_two_groups.diag')


@raises(AttributeError)
def test_unknown_plugin_diagram():
    diagram = __build_diagram('errors/unknown_plugin.diag')


@raises(ParseException)
def test_node_follows_group_diagram():
    diagram = __build_diagram('errors/node_follows_group.diag')


@raises(ParseException)
def test_group_follows_node_diagram():
    diagram = __build_diagram('errors/group_follows_node.diag')


@raises(ParseException)
def test_lexer_error_diagram():
    diagram = __build_diagram('errors/lexer_error.diag')
