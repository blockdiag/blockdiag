# -*- coding: utf-8 -*-
import re
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
        if re.match('edge_', name):
            print "[%s]" % name
            name = re.sub('edge_', '', name)
            for (id1, id2), value in values.items():
                found = False
                for edge in diagram.edges:
                    if edge.node1.id == id1 and edge.node2.id == id2:
                        print edge
                        eq_(value, getattr(edge, name))
                        found = True

                if not found:
                    raise RuntimeError('edge (%s -> %s) is not found' % \
                                       (id1, id2))
        else:
            print "[node.%s]" % name
            for node in (n for n in diagram.nodes  if n.drawable):
                print node
                value = getattr(node, name)
                eq_(values[node.id], value)
