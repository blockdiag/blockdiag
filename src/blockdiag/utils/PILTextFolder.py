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

try:
    from PIL import Image
    from PIL import ImageDraw
    from PIL import ImageFont
except ImportError:
    import Image
    import ImageDraw
    import ImageFont
from TextFolder import TextFolder
from fontmap import parse_fontpath


class PILTextFolder(TextFolder):
    def __init__(self, box, string, font, **kwargs):
        if font.path:
            path, index = parse_fontpath(font.path)
            if index:
                self.ttfont = ImageFont.truetype(path, font.size, index=index)
            else:
                self.ttfont = ImageFont.truetype(path, font.size)
        else:
            self.ttfont = None

        image = Image.new('1', (1, 1))
        self.draw = ImageDraw.Draw(image)

        super(PILTextFolder, self).__init__(box, string, font, **kwargs)

    def textsize(self, string):
        return self.draw.textsize(string, font=self.ttfont)
