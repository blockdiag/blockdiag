# -*- coding: utf-8 -*-
from nose.tools import eq_
from blockdiag.builder import *
from blockdiag.diagparser import parse_string


def __build_diagram(filename):
    import os
    testdir = os.path.dirname(__file__)
    pathname = "%s/diagrams/%s" % (testdir, filename)

    str = open(pathname).read()
    tree = parse_string(str)
    return ScreenNodeBuilder.build(tree)


def __validate_node_attributes(filename, **kwargs):
    diagram = __build_diagram(filename)

    for name, values in kwargs.items():
        print "[node.%s]" % name
        for node in (n for n in diagram.nodes  if n.drawable):
            print node
            value = getattr(node, name)
            eq_(values[node.id], value)
