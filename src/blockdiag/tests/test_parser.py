# -*- coding: utf-8 -*-

from blockdiag.diagparser import *
from nose.tools import raises


def test_diagparser_basic():
    # basic digram
    str = """
          diagram test {
             A -> B -> C, D;
          }
          """

    tree = parse(tokenize(str))
    assert isinstance(tree, Graph)


def test_diagparser_without_diagram_id():
    str = """
          diagram {
             A -> B -> C, D;
          }
          """
    tree = parse(tokenize(str))
    assert isinstance(tree, Graph)

    str = """
          {
             A -> B -> C, D;
          }
          """
    tree = parse(tokenize(str))
    assert isinstance(tree, Graph)


def test_diagparser_empty_diagram():
    str = """
          diagram {
          }
          """
    tree = parse(tokenize(str))
    assert isinstance(tree, Graph)

    str = """
          {
          }
          """
    tree = parse(tokenize(str))
    assert isinstance(tree, Graph)


def test_diagparser_diagram_includes_nodes():
    str = """
          diagram {
            A;
            B [label = "foobar"];
            C [color = "red"];
          }
          """
    tree = parse(tokenize(str))
    assert isinstance(tree, Graph)
    assert len(tree.stmts) == 3
    assert isinstance(tree.stmts[0], Node)
    assert isinstance(tree.stmts[1], Node)
    assert isinstance(tree.stmts[2], Node)


def test_diagparser_diagram_includes_edges():
    str = """
          diagram {
            A -> B -> C;
          }
          """
    tree = parse(tokenize(str))
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
    tree = parse(tokenize(str))
    assert isinstance(tree, Graph)
    print tree.stmts
    assert len(tree.stmts) == 2
    assert isinstance(tree.stmts[0], Edge)
    assert isinstance(tree.stmts[1], Edge)


def test_diagparser_diagram_includes_groups():
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
    tree = parse(tokenize(str))
    assert isinstance(tree, Graph)
    assert len(tree.stmts) == 2

    assert isinstance(tree.stmts[0], SubGraph)
    assert len(tree.stmts[0].stmts) == 2
    assert isinstance(tree.stmts[0].stmts[0], Node)
    assert isinstance(tree.stmts[0].stmts[1], Node)

    assert isinstance(tree.stmts[1], SubGraph)
    assert len(tree.stmts[1].stmts) == 1
    assert isinstance(tree.stmts[1].stmts[0], Edge)


def test_diagparser_diagram_includes_diagram_attributes():
    str = """
          diagram {
            fontsize = 12;
            node_width = 80;
          }
          """
    tree = parse(tokenize(str))
    assert isinstance(tree, Graph)
    assert len(tree.stmts) == 2


@raises(NoParseError)
def test_diagparser_parenthesis_ness():
    str = ""
    tree = parse(tokenize(str))
