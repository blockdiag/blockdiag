# -*- coding: utf-8 -*-

import Image
import ImageDraw
import ImageFont
from TextFolder import TextFolder


class PILTextFolder(TextFolder):
    def __init__(self, box, string, **kwargs):
        font = kwargs.get('font')
        if font:
            fontsize = kwargs.get('fontsize', 11)
            self.ttfont = ImageFont.truetype(font, fontsize)
            self.scale = 1
        else:
            self.ttfont = None
            self.scale = kwargs.get('scale', 1)

        image = Image.new('1', (1, 1))
        self.draw = ImageDraw.Draw(image)

        TextFolder.__init__(self, box, string, **kwargs)

    def textsize(self, string):
        return self.draw.textsize(string, font=self.ttfont)
