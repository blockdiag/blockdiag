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
           "  A;\n"
           "}\n")
    tree = parse(tokenize(str))
    nodelist, edgelist = ScreenNodeBuilder.build(tree)

    assert len(nodelist) == 1
    assert len(edgelist) == 0
    assert nodelist[0].label == 'A'
    assert nodelist[0].xy == (0, 0)


def test_single_edge_diagram():
    # empty diagram
    str = ("diagram {\n"
           "  A -> B;\n"
           "}\n")
    tree = parse(tokenize(str))
    nodelist, edgelist = ScreenNodeBuilder.build(tree)

    assert len(nodelist) == 2
    assert len(edgelist) == 1
    assert nodelist[0].label == 'A'
    assert nodelist[1].label == 'B'

    assert_pos = {'A': (0, 0), 'B': (1, 0)}
    assert_label = {'A': 'A', 'B': 'B'}
    for node in nodelist:
        assert node.xy == assert_pos[node.id]
        assert node.label == assert_label[node.id]


def test_two_edges_diagram():
    # empty diagram
    str = ("diagram {\n"
           "  A -> B -> C;\n"
           "}\n")
    tree = parse(tokenize(str))
    nodelist, edgelist = ScreenNodeBuilder.build(tree)

    assert len(nodelist) == 3
    assert len(edgelist) == 2

    assert_pos = {'A': (0, 0), 'B': (1, 0), 'C': (2, 0)}
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
           "  A -> B -> C [color = red]\n"
           "  D -> E [dir = none]\n"
           "}\n")
    tree = parse(tokenize(str))
    nodelist, edgelist = ScreenNodeBuilder.build(tree)

    assert_pos = {'A': (0, 0), 'B': (1, 0), 'C': (2, 0),
                  'D': (0, 1), 'E': (1, 1)}
    for node in nodelist:
        assert node.xy == assert_pos[node.id]

    for edge in edgelist:
        if edge.node1.id == 'D':
            assert edge.dir == 'none'
            assert edge.color == None
        else:
            assert edge.dir == 'forward'
            assert edge.color == 'red'


def test_branched_diagram():
    # empty diagram
    str = ("diagram {\n"
           "  A -> B -> C\n"
           "  A -> D -> E\n"
           "  Z\n"
           "}\n")
    tree = parse(tokenize(str))
    nodelist, edgelist = ScreenNodeBuilder.build(tree)

    assert_pos = {'A': (0, 0), 'B': (1, 0), 'C': (2, 0),
                  'D': (1, 1), 'E': (2, 1), 'Z': (0, 2)}
    for node in nodelist:
        assert node.xy == assert_pos[node.id]


def test_circular_ref_diagram():
    # empty diagram
    str = ("diagram {\n"
           "  A -> B -> C -> A\n"
           "       B -> D\n"
           "  Z\n"
           "}\n")
    tree = parse(tokenize(str))
    nodelist, edgelist = ScreenNodeBuilder.build(tree)

    assert_pos = {'A': (0, 0), 'B': (1, 0), 'C': (2, 0),
                  'D': (2, 1), 'Z': (0, 2)}
    for node in nodelist:
        assert node.xy == assert_pos[node.id]


def test_skipped_edge_diagram():
    # empty diagram
    str = ("diagram {\n"
           "  A -> B -> C\n"
           "  A      -> C\n"
           "  Z\n"
           "}\n")
    tree = parse(tokenize(str))
    nodelist, edgelist = ScreenNodeBuilder.build(tree)

    assert_pos = {'A': (0, 0), 'B': (1, 0), 'C': (2, 0),
                  'Z': (0, 1)}
    for node in nodelist:
        assert node.xy == assert_pos[node.id]


def test_circular_skipped_edge_diagram():
    # empty diagram
    str = ("diagram {\n"
           "  A -> B -> C -> A\n"
           "  A      -> C\n"
           "  Z\n"
           "}\n")
    tree = parse(tokenize(str))
    nodelist, edgelist = ScreenNodeBuilder.build(tree)

    assert_pos = {'A': (0, 0), 'B': (1, 0), 'C': (2, 0), 'Z': (0, 1)}
    for node in nodelist:
        assert node.xy == assert_pos[node.id]


def test_triple_branched_diagram():
    # empty diagram
    str = ("diagram {\n"
           "  A -> D\n"
           "  B -> D\n"
           "  C -> D\n"
           "  Z\n"
           "}\n")
    tree = parse(tokenize(str))
    nodelist, edgelist = ScreenNodeBuilder.build(tree)

    assert_pos = {'A': (0, 0), 'B': (0, 1), 'C': (0, 2),
                  'D': (1, 0), 'Z': (0, 3)}
    for node in nodelist:
        assert node.xy == assert_pos[node.id]


def test_twin_circular_ref_diagram():
    # empty diagram
    str = ("diagram {\n"
           "  A -> B -> A\n"
           "  A -> C -> A\n"
           "  Z\n"
           "}\n")
    tree = parse(tokenize(str))
    nodelist, edgelist = ScreenNodeBuilder.build(tree)

    assert_pos = {'A': (0, 0), 'B': (1, 0), 'C': (1, 1), 'Z': (0, 2)}
    for node in nodelist:
        assert node.xy == assert_pos[node.id]


def test_self_ref_diagram():
    # empty diagram
    str = ("diagram {\n"
           "  A -> B -> B\n"
           "  Z\n"
           "}\n")
    tree = parse(tokenize(str))
    nodelist, edgelist = ScreenNodeBuilder.build(tree)

    assert_pos = {'A': (0, 0), 'B': (1, 0), 'Z': (0, 1)}
    for node in nodelist:
        assert node.xy == assert_pos[node.id]


def test_noweight_edge_diagram():
    # empty diagram
    str = ("diagram {\n"
           "  A -> B -> C\n"
           "       B -> D -> E[noweight = 1]\n"
           "  D -> F\n"
           "  Z\n"
           "}\n")
    tree = parse(tokenize(str))
    nodelist, edgelist = ScreenNodeBuilder.build(tree)

    assert_pos = {'A': (0, 0), 'B': (1, 0), 'C': (2, 0),
                  'D': (0, 1), 'E': (0, 2), 'F': (1, 1),
                  'Z': (0, 3)}
    for node in nodelist:
        assert node.xy == assert_pos[node.id]


def test_flowable_node_diagram():
    # empty diagram
    str = ("diagram {\n"
           "  B -> C\n"
           "  A -> B\n"
           "  Z\n"
           "}\n")
    tree = parse(tokenize(str))
    nodelist, edgelist = ScreenNodeBuilder.build(tree)

    assert_pos = {'A': (0, 0), 'B': (1, 0), 'C': (2, 0),
                  'Z': (0, 1)}
    for node in nodelist:
        assert node.xy == assert_pos[node.id]


def test_simple_group_diagram():
    # empty diagram
    str = ("diagram {\n"
           "  group {\n"
           "    A -> B\n"
           "    A -> C\n"
           "  }\n"
           "  Z\n"
           "}\n")
    tree = parse(tokenize(str))
    nodelist, edgelist = ScreenNodeBuilder.build(tree)

    assert_pos = {'A': (0, 0), 'B': (1, 0), 'C': (1, 1),
                  'Z': (0, 2)}
    for node in (x for x in nodelist if x.drawable):
        assert node.xy == assert_pos[node.id]


def test_group_and_node_diagram():
    # empty diagram
    str = ("diagram {\n"
           "  group {\n"
           "    A -> B\n"
           "  }\n"
           "  B -> C\n"
           "  Z\n"
           "}\n")
    tree = parse(tokenize(str))
    nodelist, edgelist = ScreenNodeBuilder.build(tree)

    assert_pos = {'A': (0, 0), 'B': (1, 0), 'C': (2, 0),
                  'Z': (0, 1)}
    for node in (x for x in nodelist if x.drawable):
        assert node.xy == assert_pos[node.id]


def test_group_and_node_diagram():
    # empty diagram
    str = ("diagram {\n"
           "  group {\n"
           "    A -> B\n"
           "  }\n"
           "  B -> C\n"
           "  B -> D\n"
           "  Z\n"
           "}\n")
    tree = parse(tokenize(str))
    nodelist, edgelist = ScreenNodeBuilder.build(tree)

    assert_pos = {'A': (0, 0), 'B': (1, 0), 'C': (2, 0),
                  'D': (2, 1), 'Z': (0, 2)}
    for node in (x for x in nodelist if x.drawable):
        assert node.xy == assert_pos[node.id]


def test_large_group_and_node_diagram():
    # empty diagram
    str = ("diagram {\n"
           "  group {\n"
           "    A -> B\n"
           "    A -> C\n"
           "    A -> D\n"
           "    A -> E\n"
           "  }\n"
           "  B -> F\n"
           "  Z\n"
           "}\n")
    tree = parse(tokenize(str))
    nodelist, edgelist = ScreenNodeBuilder.build(tree)

    assert_pos = {'A': (0, 0), 'B': (1, 0), 'C': (1, 1),
                  'D': (1, 2), 'E': (1, 3), 'F': (2, 0),
                  'Z': (0, 4)}
    for node in (x for x in nodelist if x.drawable):
        assert node.xy == assert_pos[node.id]


def test_large_group_and_two_node_diagram():
    # empty diagram
    str = ("diagram {\n"
           "  group {\n"
           "    A -> B\n"
           "    A -> C\n"
           "    A -> D\n"
           "    A -> E\n"
           "  }\n"
           "  B -> F\n"
           "  C -> G\n"
           "  Z\n"
           "}\n")
    tree = parse(tokenize(str))
    nodelist, edgelist = ScreenNodeBuilder.build(tree)

    assert_pos = {'A': (0, 0), 'B': (1, 0), 'C': (1, 1),
                  'D': (1, 2), 'E': (1, 3), 'F': (2, 0),
                  'G': (2, 1), 'Z': (0, 4)}
    for node in (x for x in nodelist if x.drawable):
        assert node.xy == assert_pos[node.id]
