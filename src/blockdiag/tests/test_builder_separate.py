# -*- coding: utf-8 -*-
#  Copyright 2011 Takeshi KOMIYA
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from __future__ import print_function

from blockdiag.builder import SeparateDiagramBuilder
from blockdiag.elements import DiagramNode
from blockdiag.tests.utils import BuilderTestCase


class TestBuilderSeparated(BuilderTestCase):
    def _build(self, tree):
        return SeparateDiagramBuilder.build(tree)

    def test_separate1_diagram(self):
        diagram = self.build('separate1.diag')

        assert_pos = {0: {'B': (0, 0), 'C': (1, 0), 'D': (4, 0),
                          'E': (2, 0), 'F': (3, 0)},
                      1: {'A': (0, 0), 'B': (1, 0), 'D': (3, 0)},
                      2: {'A': (0, 0), 'Z': (0, 1)}}

        for i, diagram in enumerate(diagram):
            for node in diagram.traverse_nodes():
                if isinstance(node, DiagramNode):
                    print(node)
                    self.assertEqual(assert_pos[i][node.id], node.xy)

    def test_separate2_diagram(self):
        diagram = self.build('separate2.diag')

        assert_pos = {0: {'A': (0, 0), 'C': (1, 0), 'D': (2, 0),
                          'E': (0, 2), 'G': (3, 0), 'H': (3, 1)},
                      1: {'A': (0, 0), 'B': (1, 0), 'E': (2, 0),
                          'F': (4, 2), 'G': (4, 0), 'H': (4, 1)},
                      2: {'A': (0, 0), 'F': (2, 2), 'G': (2, 0),
                          'H': (2, 1), 'Z': (0, 3)}}

        for i, diagram in enumerate(diagram):
            for node in diagram.traverse_nodes():
                if isinstance(node, DiagramNode):
                    print(node)
                    self.assertEqual(assert_pos[i][node.id], node.xy)
