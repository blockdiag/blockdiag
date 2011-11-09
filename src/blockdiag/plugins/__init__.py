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

from pkg_resources import iter_entry_points

node_handlers = []


def load(plugins, diagram, **kwargs):
    for name in plugins:
        for ep in iter_entry_points('blockdiag_plugins', name):
            module = ep.load()
            if hasattr(module, 'setup'):
                module.setup(module, diagram, **kwargs)
            break
        else:
            msg = "WARNING: unknown plugin: %s\n" % name
            raise AttributeError(msg)


def install_node_handler(handler):
    if handler not in node_handlers:
        node_handlers.append(handler)


def fire_node_event(node, name, *args):
    method = "on_" + name
    for handler in node_handlers:
        getattr(handler, method)(node, *args)


class NodeHandler(object):
    def __init__(self, diagram, **kwargs):
        self.diagram = diagram

    def on_created(self, node):
        pass

    def on_attr_changed(self, node, attr):
        pass
