# -*- coding: utf-8 -*-

import tempfile
from blockdiag.blockdiag import *
from blockdiag.diagparser import *
from nose.tools import assert_raises


def test_diagparser():
    # basic digram
    str = ("diagram test {\n"
           "}\n")

    tree = parse(tokenize(str))
    assert isinstance(tree, Graph)

    # digram without id
    str = ("diagram {\n"
           "}\n")
    tree = parse(tokenize(str))
    assert isinstance(tree, Graph)

    # digram without diagram and id
    str = ("{\n"
           "}\n")
    tree = parse(tokenize(str))
    assert isinstance(tree, Graph)

    # parsing error for empty string
    def dummy():
        str = ""
        tree = parse(tokenize(str))
    assert_raises(NoParseError, dummy)


def test_empty_diagram():
    # empty diagram
    str = ("diagram {\n"
           "}\n")
    tree = parse(tokenize(str))
    nodelist, edgelist = ScreenNodeBuilder.build(tree)

    assert len(nodelist) == 0
    assert len(edgelist) == 0


def test_single_node_diagram():
    # empty diagram
    str = ("diagram {\n"
           "  foo;\n"
           "}\n")
    tree = parse(tokenize(str))
    nodelist, edgelist = ScreenNodeBuilder.build(tree)

    assert len(nodelist) == 1
    assert len(edgelist) == 0
    assert nodelist[0].label == 'foo'
    assert nodelist[0].xy == (0, 0)


def test_single_edge_diagram():
    # empty diagram
    str = ("diagram {\n"
           "  foo -> bar;\n"
           "}\n")
    tree = parse(tokenize(str))
    nodelist, edgelist = ScreenNodeBuilder.build(tree)

    assert len(nodelist) == 2
    assert len(edgelist) == 1
    assert nodelist[0].label == 'foo'
    assert nodelist[0].xy == (0, 0)
    assert nodelist[1].label == 'bar'
    assert nodelist[1].xy == (1, 0)
    assert edgelist[0].node1.id == 'foo'
    assert edgelist[0].node2.id == 'bar'


def test_two_edges_diagram():
    # empty diagram
    str = ("diagram {\n"
           "  foo -> bar -> baz;\n"
           "}\n")
    tree = parse(tokenize(str))
    nodelist, edgelist = ScreenNodeBuilder.build(tree)

    assert len(nodelist) == 3
    assert len(edgelist) == 2

    assert_pos = {'foo': (0, 0), 'bar': (1, 0), 'baz': (2, 0)}
    for node in nodelist:
        assert node.xy == assert_pos[node.id]


def test_node_attribute():
    # empty diagram
    str = ("diagram {\n"
           "  foo [label = bar, color = red];\n"
           "  bar\n"
           "}\n")
    tree = parse(tokenize(str))
    nodelist, edgelist = ScreenNodeBuilder.build(tree)

    assert nodelist[0].id == 'foo'
    assert nodelist[0].label == 'bar'
    assert nodelist[0].color == 'red'
    assert nodelist[0].xy == (0, 0)

    assert nodelist[1].id == 'bar'
    assert nodelist[1].label == 'bar'
    assert nodelist[1].color == None
    assert nodelist[1].xy == (0, 1)


def test_edge_attribute():
    # empty diagram
    str = ("diagram {\n"
           "  foo -> bar -> baz [color = red]\n"
           "  hoge -> fuga [dir = none]\n"
           "}\n")
    tree = parse(tokenize(str))
    nodelist, edgelist = ScreenNodeBuilder.build(tree)

    for edge in edgelist:
        if edge.node1.id == 'hoge':
            assert edge.dir == 'none'
            assert edge.color == None
        else:
            assert edge.dir == 'forward'
            assert edge.color == 'red'
