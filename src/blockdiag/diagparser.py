# -*- coding: utf-8 -*-

# Copyright (c) 2008/2009 Andrey Vlasovskikh
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

r'''A DOT language parser using funcparserlib.

The parser is based on [the DOT grammar][1]. It is pretty complete with a few
not supported things:

* Ports and compass points
* XML identifiers

At the moment, the parser builds only a parse tree, not an abstract syntax tree
(AST) or an API for dealing with DOT.

  [1]: http://www.graphviz.org/doc/info/lang.html
'''

import os
import sys
import codecs
from re import MULTILINE
from pprint import pformat
from funcparserlib.util import pretty_tree
from funcparserlib.lexer import make_tokenizer, Token, LexerError
from funcparserlib.parser import (some, a, maybe, many, finished, skip,
    oneplus, forward_decl, NoParseError)
try:
    from collections import namedtuple
except ImportError:
    from utils.namedtuple import namedtuple

ENCODING = 'utf-8'

Graph = namedtuple('Graph', 'type id stmts')
SubGraph = namedtuple('SubGraph', 'id stmts')
Node = namedtuple('Node', 'id attrs')
Attr = namedtuple('Attr', 'name value')
Edge = namedtuple('Edge', 'nodes attrs')
DefAttrs = namedtuple('DefAttrs', 'object attrs')


def tokenize(str):
    'str -> Sequence(Token)'
    specs = [
        ('Comment', (r'/\*(.|[\r\n])*?\*/', MULTILINE)),
        ('Comment', (r'//.*',)),
        ('NL',      (r'[\r\n]+',)),
        ('Space',   (r'[ \t\r\n]+',)),
        ('Name',    (r'[A-Za-z\200-\377_][A-Za-z\200-\377_0-9]*',)),
        ('Op',      (r'[{};,=\[\]]|(<->)|(<-)|(--)|(->)',)),
        ('Number',  (r'-?(\.[0-9]+)|([0-9]+(\.[0-9]*)?)',)),
        ('String',  (r'(?P<quote>"|\')(?:.|\s)*?(?<!\\)(?P=quote)',)),
    ]
    useless = ['Comment', 'NL', 'Space']
    t = make_tokenizer(specs)
    return [x for x in t(str) if x.type not in useless]


def parse(seq):
    'Sequence(Token) -> object'
    unarg = lambda f: lambda args: f(*args)
    tokval = lambda x: x.value
    flatten = lambda list: sum(list, [])
    n = lambda s: a(Token('Name', s)) >> tokval
    op = lambda s: a(Token('Op', s)) >> tokval
    op_ = lambda s: skip(op(s))
    id = some(lambda t:
        t.type in ['Name', 'Number', 'String']).named('id') >> tokval
    make_graph_attr = lambda args: DefAttrs(u'graph', [Attr(*args)])
    make_edge = lambda x, x2, xs, attrs: Edge([x, x2] + xs, attrs)

    node_id = id  # + maybe(port)
    a_list = (
        id +
        maybe(op_('=') + id) +
        skip(maybe(op(',')))
        >> unarg(Attr))
    attr_list = (
        many(op_('[') + many(a_list) + op_(']'))
        >> flatten)
    attr_stmt = (
       (n('graph') | n('node') | n('edge')) +
       attr_list
       >> unarg(DefAttrs))
    graph_attr = id + op_('=') + id >> make_graph_attr
    node_stmt = node_id + attr_list >> unarg(Node)
    # We use a forward_decl becaue of circular definitions like (stmt_list ->
    # stmt -> subgraph -> stmt_list)
    subgraph = forward_decl()
    edge_rhs = (op('->') | op('--') | op('<-') | op('<->')) + node_id
    edge_stmt = (
        node_id +
        edge_rhs +
        many(edge_rhs) +
        attr_list
        >> unarg(make_edge))
    stmt = (
          attr_stmt
        | edge_stmt
        | subgraph
        | graph_attr
        | node_stmt
    )
    stmt_list = many(stmt + skip(maybe(op(';'))))
    subgraph.define(
        skip(n('group')) +
        maybe(id) +
        op_('{') +
        stmt_list +
        op_('}')
        >> unarg(SubGraph))
    graph = (
        maybe(n('diagram')) +
        maybe(id) +
        op_('{') +
        stmt_list +
        op_('}')
        >> unarg(Graph))
    dotfile = graph + skip(finished)

    return dotfile.parse(seq)


def pretty_parse_tree(x):
    'object -> str'
    Pair = namedtuple('Pair', 'first second')
    p = lambda x, y: Pair(x, y)

    def kids(x):
        'object -> list(object)'
        if isinstance(x, (Graph, SubGraph)):
            return [p('stmts', x.stmts)]
        elif isinstance(x, (Node, DefAttrs)):
            return [p('attrs', x.attrs)]
        elif isinstance(x, Edge):
            return [p('nodes', x.nodes), p('attrs', x.attrs)]
        elif isinstance(x, Pair):
            return x.second
        else:
            return []

    def show(x):
        'object -> str'
        if isinstance(x, Pair):
            return x.first
        elif isinstance(x, Graph):
            return 'Graph [id=%s, type=%s]' % (
                x.id, x.type)
        elif isinstance(x, SubGraph):
            return 'SubGraph [id=%s]' % x.id
        elif isinstance(x, Edge):
            return 'Edge'
        elif isinstance(x, Attr):
            return 'Attr [name=%s, value=%s]' % (x.name, x.value)
        elif isinstance(x, DefAttrs):
            return 'DefAttrs [object=%s]' % x.object
        elif isinstance(x, Node):
            return 'Node [id=%s]' % x.id
        else:
            return unicode(x)
    return pretty_tree(x, kids, show)


def parse_file(path):
    input = codecs.open(path, 'r', 'utf-8').read()
    return parse(tokenize(input))


def main():
    #import logging
    #logging.basicConfig(level=logging.DEBUG)
    #import funcparserlib
    #funcparserlib.parser.debug = True
    try:
        stdin = os.fdopen(sys.stdin.fileno(), 'rb')
        input = stdin.read().decode(ENCODING)
        tree = parse(tokenize(input))
        print pretty_parse_tree(tree).encode(ENCODING)
    except (NoParseError, LexerError), e:
        msg = (u'syntax error: %s' % e).encode(ENCODING)
        print >> sys.stderr, msg
        sys.exit(1)

if __name__ == '__main__':
    main()
