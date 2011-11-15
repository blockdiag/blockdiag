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

import math
from TextFolder import TextFolder


class PDFTextFolder(TextFolder):
    def __init__(self, box, string, font, **kwargs):
        self.canvas = kwargs.get('canvas')
        self.font = font

        TextFolder.__init__(self, box, string, font, **kwargs)

    def textsize(self, string):
        width = self.canvas.stringWidth(string, self.font.path, self.font.size)
        return (int(math.ceil(width)), self.font.size)
