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


@raises(RuntimeError)
def test_unknown_node_shape_diagram():
    screen = __build_diagram('unknown_node_shape.diag')


@raises(RuntimeError)
def test_unknown_default_shape_diagram():
    screen = __build_diagram('unknown_default_shape.diag')


@raises(RuntimeError)
def test_belongs_to_two_groups_diagram():
    screen = __build_diagram('belongs_to_two_groups.diag')


@raises(NoParseError)
def test_node_follows_group_diagram():
    screen = __build_diagram('node_follows_group.diag')


@raises(NoParseError)
def test_group_follows_node_diagram():
    screen = __build_diagram('group_follows_node.diag')
