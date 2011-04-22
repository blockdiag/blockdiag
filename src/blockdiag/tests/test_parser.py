# -*- coding: utf-8 -*-

from blockdiag.diagparser import *
from nose.tools import raises


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


@raises(NoParseError)
def test_diagparser_parenthesis_ness():
    str = ""
    tree = parse(tokenize(str))
