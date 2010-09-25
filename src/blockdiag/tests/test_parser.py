# -*- coding: utf-8 -*-

import tempfile
from blockdiag.blockdiag import *
from blockdiag.diagparser import *
from nose.tools import assert_raises


def test_diagparser_basic():
    # basic digram
    str = ("diagram test {\n"
           "}\n")

    tree = parse(tokenize(str))
    assert isinstance(tree, Graph)


def test_diagparser_without_id():
    str = ("diagram {\n"
           "}\n")
    tree = parse(tokenize(str))
    assert isinstance(tree, Graph)


def test_diagparser_empty():
    str = ("{\n"
           "}\n")
    tree = parse(tokenize(str))
    assert isinstance(tree, Graph)


def test_diagparser_parenthesis_ness():
    def dummy():
        str = ""
        tree = parse(tokenize(str))
    assert_raises(NoParseError, dummy)


def test_empty_diagram():
    str = ("diagram {\n"
           "}\n")
    tree = parse(tokenize(str))
    nodelist, edgelist = ScreenNodeBuilder.build(tree)

    assert len(nodelist) == 0
    assert len(edgelist) == 0


def test_single_node_diagram():
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


def test_belongs_to_two_groups_diagram():
    def dummy():
        str = ("diagram {\n"
               "  group {\n"
               "    A\n"
               "  }\n"
               "  group {\n"
               "    A\n"
               "  }\n"
               "  Z\n"
               "}\n")
        tree = parse(tokenize(str))
        nodelist, edgelist = ScreenNodeBuilder.build(tree)

    assert_raises(RuntimeError, dummy)


def test_nested_groups_diagram():
    def dummy():
        str = ("diagram {\n"
               "  group {\n"
               "    A\n"
               "    group {\n"
               "      B\n"
               "    }\n"
               "  }\n"
               "  Z\n"
               "}\n")
        tree = parse(tokenize(str))
        nodelist, edgelist = ScreenNodeBuilder.build(tree)

    assert_raises(NoParseError, dummy)


def test_node_follows_group_diagram():
    def dummy():
        str = ("diagram {\n"
               "  A -> group {\n"
               "    B\n"
               "  }\n"
               "  Z\n"
               "}\n")
        tree = parse(tokenize(str))
        nodelist, edgelist = ScreenNodeBuilder.build(tree)

    assert_raises(NoParseError, dummy)


def test_group_follows_node_diagram():
    def dummy():
        str = ("diagram {\n"
               "  A -> group {\n"
               "    B\n"
               "  }\n"
               "  Z\n"
               "}\n")
        tree = parse(tokenize(str))
        nodelist, edgelist = ScreenNodeBuilder.build(tree)

    assert_raises(NoParseError, dummy)


def test_simple_group_diagram():
    str = ("diagram {\n"
           "  group {\n"
           "  }\n"
           "  Z\n"
           "}\n")
    tree = parse(tokenize(str))
    nodelist, edgelist = ScreenNodeBuilder.build(tree)

    assert_pos = {'Z': (0, 0)}
    for node in (x for x in nodelist if x.drawable):
        assert node.xy == assert_pos[node.id]


def test_simple_group_diagram():
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


def test_group_id_and_node_id_are_not_conflicted_diagram():
    str = ("diagram {\n"
           "  A -> B\n"
           "  group B {\n"
           "    C -> D\n"
           "  }\n"
           "  Z\n"
           "}\n")
    tree = parse(tokenize(str))
    nodelist, edgelist = ScreenNodeBuilder.build(tree)

    assert_pos = {'A': (0, 0), 'B': (1, 0), 'C': (0, 1),
                  'D': (1, 1), 'Z': (0, 2)}
    for node in (x for x in nodelist if x.drawable):
        assert node.xy == assert_pos[node.id]


def test_group_and_childnode_diagram():
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


def test_group_and_parentnode_diagram():
    str = ("diagram {\n"
           "  group {\n"
           "    B -> C\n"
           "  }\n"
           "  A -> B\n"
           "  Z\n"
           "}\n")
    tree = parse(tokenize(str))
    nodelist, edgelist = ScreenNodeBuilder.build(tree)

    assert_pos = {'A': (0, 0), 'B': (1, 0), 'C': (2, 0),
                  'Z': (0, 1)}
    for node in (x for x in nodelist if x.drawable):
        assert node.xy == assert_pos[node.id]


def test_large_group_and_node_diagram():
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


def test_multiple_groups_diagram():
    str = ("diagram {\n"
           "  group {\n"
           "    A;  B;  C;  D\n"
           "  }\n"
           "  group {\n"
           "    E;  F;  G\n"
           "  }\n"
           "  group {\n"
           "    H;  I\n"
           "  }\n"
           "  group {\n"
           "    J\n"
           "  }\n"
           "  A -> E -> H -> J\n"
           "  Z\n"
           "}\n")
    tree = parse(tokenize(str))
    nodelist, edgelist = ScreenNodeBuilder.build(tree)

    assert_pos = {'A': (0, 0), 'B': (0, 1), 'C': (0, 2),
                  'D': (0, 3), 'E': (1, 0), 'F': (1, 1),
                  'G': (1, 2), 'H': (2, 0), 'I': (2, 1),
                  'J': (3, 0), 'Z': (0, 4)}
    for node in (x for x in nodelist if x.drawable):
        print node.id, node.xy
        assert node.xy == assert_pos[node.id]


def test_group_as_node_decorator_diagram():
    str = ("diagram {\n"
           "  A -> B -> C\n"
           "  A -> B -> D\n"
           "  A -> E\n"
           "  group {\n"
           "    A; B; D; E\n"
           "  }\n"
           "  Z\n"
           "}\n")
    tree = parse(tokenize(str))
    nodelist, edgelist = ScreenNodeBuilder.build(tree)

    assert_pos = {'A': (0, 0), 'B': (1, 0), 'C': (3, 0),
                  'D': (2, 0), 'E': (1, 1), 'Z': (0, 2)}
    for node in (x for x in nodelist if x.drawable):
        assert node.xy == assert_pos[node.id]


def test_reversed_multiple_groups_diagram():
    str = ("diagram {\n"
           "  group {\n"
           "    A;  B;  C;  D\n"
           "  }\n"
           "  group {\n"
           "    E;  F;  G\n"
           "  }\n"
           "  group {\n"
           "    H;  I\n"
           "  }\n"
           "  group {\n"
           "    J\n"
           "  }\n"
           "  J -> H -> E -> A\n"
           "  Z\n"
           "}\n")
    tree = parse(tokenize(str))
    nodelist, edgelist = ScreenNodeBuilder.build(tree)

    assert_pos = {'A': (3, 0), 'B': (3, 1), 'C': (3, 2),
                  'D': (3, 3), 'E': (2, 0), 'F': (2, 1),
                  'G': (2, 2), 'H': (1, 0), 'I': (1, 1),
                  'J': (0, 0), 'Z': (0, 4)}
    for node in (x for x in nodelist if x.drawable):
        assert node.xy == assert_pos[node.id]
