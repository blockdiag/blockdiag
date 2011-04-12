# -*- coding: utf-8 -*-

import math
from TextFolder import TextFolder


class PDFTextFolder(TextFolder):
    def __init__(self, box, string, **kwargs):
        self.canvas = kwargs.get('canvas')
        self.font = kwargs.get('font')
        self.fontsize = kwargs.get('fontsize', 11)

        TextFolder.__init__(self, box, string, **kwargs)

    def textsize(self, string):
        width = self.canvas.stringWidth(string, self.font, self.fontsize)
        return (int(math.ceil(width)), self.fontsize)
