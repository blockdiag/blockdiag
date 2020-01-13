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

from blockdiag.parser import ParseException
from blockdiag.tests.utils import BuilderTestCase


class TestBuilderError(BuilderTestCase):
    def test_unknown_diagram_default_shape_diagram(self):
        filename = 'errors/unknown_diagram_default_shape.diag'
        with self.assertRaises(AttributeError):
            self.build(filename)

    def test_unknown_diagram_edge_layout_diagram(self):
        filename = 'errors/unknown_diagram_edge_layout.diag'
        with self.assertRaises(AttributeError):
            self.build(filename)

    def test_unknown_diagram_orientation_diagram(self):
        filename = 'errors/unknown_diagram_orientation.diag'
        with self.assertRaises(AttributeError):
            self.build(filename)

    def test_unknown_node_shape_diagram(self):
        filename = 'errors/unknown_node_shape.diag'
        with self.assertRaises(AttributeError):
            self.build(filename)

    def test_unknown_node_attribute_diagram(self):
        filename = 'errors/unknown_node_attribute.diag'
        with self.assertRaises(AttributeError):
            self.build(filename)

    def test_unknown_node_style_diagram(self):
        filename = 'errors/unknown_node_style.diag'
        with self.assertRaises(AttributeError):
            self.build(filename)

    def test_unknown_node_class_diagram(self):
        filename = 'errors/unknown_node_class.diag'
        with self.assertRaises(AttributeError):
            self.build(filename)

    def test_unknown_edge_dir_diagram(self):
        filename = 'errors/unknown_edge_dir.diag'
        with self.assertRaises(AttributeError):
            self.build(filename)

    def test_unknown_edge_style_diagram(self):
        filename = 'errors/unknown_edge_style.diag'
        with self.assertRaises(AttributeError):
            self.build(filename)

    def test_unknown_edge_hstyle_diagram(self):
        filename = 'errors/unknown_edge_hstyle.diag'
        with self.assertRaises(AttributeError):
            self.build(filename)

    def test_unknown_edge_class_diagram(self):
        filename = 'errors/unknown_edge_class.diag'
        with self.assertRaises(AttributeError):
            self.build(filename)

    def test_unknown_group_shape_diagram(self):
        filename = 'errors/unknown_group_shape.diag'
        with self.assertRaises(AttributeError):
            self.build(filename)

    def test_unknown_group_class_diagram(self):
        filename = 'errors/unknown_group_class.diag'
        with self.assertRaises(AttributeError):
            self.build(filename)

    def test_unknown_group_orientation_diagram(self):
        filename = 'errors/unknown_group_orientation.diag'
        with self.assertRaises(AttributeError):
            self.build(filename)

    def test_belongs_to_two_groups_diagram(self):
        filename = 'errors/belongs_to_two_groups.diag'
        with self.assertRaises(RuntimeError):
            self.build(filename)

    def test_unknown_plugin_diagram(self):
        filename = 'errors/unknown_plugin.diag'
        with self.assertRaises(AttributeError):
            self.build(filename)

    def test_node_follows_group_diagram(self):
        filename = 'errors/node_follows_group.diag'
        with self.assertRaises(ParseException):
            self.build(filename)

    def test_group_follows_node_diagram(self):
        filename = 'errors/group_follows_node.diag'
        with self.assertRaises(ParseException):
            self.build(filename)

    def test_unknown_diagram_type(self):
        filename = 'errors/unknown_diagram_type.diag'
        with self.assertRaises(ParseException):
            self.build(filename)

    def test_lexer_error_diagram(self):
        filename = 'errors/lexer_error.diag'
        with self.assertRaises(ParseException):
            self.build(filename)
