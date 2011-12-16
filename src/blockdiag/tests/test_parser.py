# -*- coding: utf-8 -*-

from blockdiag.parser import *
from nose.tools import raises


def test_parser_basic():
    # basic digram
    str = """
          diagram test {
             A -> B -> C, D;
          }
          """

    tree = parse_string(str)
    assert isinstance(tree, Graph)


def test_parser_without_diagram_id():
    str = """
          diagram {
             A -> B -> C, D;
          }
          """
    tree = parse_string(str)
    assert isinstance(tree, Graph)

    str = """
          {
             A -> B -> C, D;
          }
          """
    tree = parse_string(str)
    assert isinstance(tree, Graph)


def test_parser_empty_diagram():
    str = """
          diagram {
          }
          """
    tree = parse_string(str)
    assert isinstance(tree, Graph)

    str = """
          {
          }
          """
    tree = parse_string(str)
    assert isinstance(tree, Graph)


def test_parser_diagram_includes_nodes():
    str = """
          diagram {
            A;
            B [label = "foobar"];
            C [color = "red"];
          }
          """
    tree = parse_string(str)
    assert isinstance(tree, Graph)
    assert len(tree.stmts) == 3
    assert isinstance(tree.stmts[0], Statements)
    assert isinstance(tree.stmts[0].stmts[0], Node)
    assert isinstance(tree.stmts[1], Statements)
    assert isinstance(tree.stmts[1].stmts[0], Node)
    assert isinstance(tree.stmts[2], Statements)
    assert isinstance(tree.stmts[2].stmts[0], Node)


def test_parser_diagram_includes_edges():
    str = """
          diagram {
            A -> B -> C;
          }
          """
    tree = parse_string(str)
    assert isinstance(tree, Graph)
    print tree.stmts
    assert len(tree.stmts) == 1
    assert isinstance(tree.stmts[0], Edge)

    str = """
          diagram {
            A -> B -> C [style = dotted];
            D -> E, F;
          }
          """
    tree = parse_string(str)
    assert isinstance(tree, Graph)
    print tree.stmts
    assert len(tree.stmts) == 2
    assert isinstance(tree.stmts[0], Edge)
    assert isinstance(tree.stmts[1], Edge)


def test_parser_diagram_includes_groups():
    str = """
          diagram {
            group {
              A; B;
            }
            group {
              C -> D;
            }
          }
          """
    tree = parse_string(str)
    assert isinstance(tree, Graph)
    assert len(tree.stmts) == 2

    assert isinstance(tree.stmts[0], SubGraph)
    assert len(tree.stmts[0].stmts) == 2
    assert isinstance(tree.stmts[0].stmts[0], Statements)
    assert isinstance(tree.stmts[0].stmts[0].stmts[0], Node)
    assert isinstance(tree.stmts[0].stmts[1], Statements)
    assert isinstance(tree.stmts[0].stmts[1].stmts[0], Node)

    assert isinstance(tree.stmts[1], SubGraph)
    assert len(tree.stmts[1].stmts) == 1
    assert isinstance(tree.stmts[1].stmts[0], Edge)


def test_parser_diagram_includes_diagram_attributes():
    str = """
          diagram {
            fontsize = 12;
            node_width = 80;
          }
          """
    tree = parse_string(str)
    assert isinstance(tree, Graph)
    assert len(tree.stmts) == 2


@raises(ParseException)
def test_parser_parenthesis_ness():
    str = ""
    tree = parse_string(str)
