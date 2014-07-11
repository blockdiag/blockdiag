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

import re
from blockdiag import plugins


class AutoClass(plugins.NodeHandler):
    def on_created(self, node):
        if node.id is None:
            return True

        for name, klass in self.diagram.classes.items():
            pattern = "_%s$" % re.escape(name)

            if re.search(pattern, node.id):
                node.label = re.sub(pattern, '', node.id)
                node.set_attributes(klass.attrs)

        return True


def setup(self, diagram, **kwargs):
    plugins.install_node_handler(AutoClass(diagram, **kwargs))
