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

import os
from hashlib import sha1
from docutils import nodes
import blockdiag.parser
import blockdiag.builder
import blockdiag.drawer


class blockdiag(nodes.General, nodes.Element):
    name = 'blockdiag'
    processor = blockdiag

    def to_diagram(self):
        try:
            tree = self.processor.parser.parse_string(self['code'])
        except:
            code = '%s { %s }' % (self.name, self['code'])
            tree = self.processor.parser.parse_string(code)
            self['code'] = code  # replace if succeeded

        return self.processor.builder.ScreenNodeBuilder.build(tree)

    def to_drawer(self, image_format, filename, fontmap, **kwargs):
        diagram = self.to_diagram()
        return self.processor.drawer.DiagramDraw(image_format, diagram,
                                                 filename, fontmap=fontmap,
                                                 **kwargs)

    def get_path(self, **options):
        options.update(self['options'])
        hashseed = (self['code'] + str(options)).encode('utf-8')
        hashed = sha1(hashseed).hexdigest()

        filename = "%s-%s.%s" % (self.name, hashed, options['format'].lower())
        outputdir = options.get('outputdir')
        if outputdir:
            filename = os.path.join(outputdir, filename)

        return filename
