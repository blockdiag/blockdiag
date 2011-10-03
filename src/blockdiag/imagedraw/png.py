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
from itertools import islice, izip, tee
from blockdiag.utils.myitertools import istep
from blockdiag.utils.PILTextFolder import PILTextFolder as TextFolder
try:
    from PIL import Image
    from PIL import ImageDraw
    from PIL import ImageFont
    from PIL import ImageFilter
except ImportError:
    import Image
    import ImageDraw
    import ImageFont
    import ImageFilter
from blockdiag.utils.XY import XY
from blockdiag.utils import ellipse
from blockdiag.utils import urlutil


def point_pairs(xylist):
    iterable = iter(xylist)
    for pt in iterable:
        if isinstance(pt, int):
            yield (pt, iterable.next())
        else:
            yield pt


def line_segments(xylist):
    p1, p2 = tee(point_pairs(xylist))
    p2.next()
    return izip(p1, p2)


def dashize_line(line, length):
    pt1, pt2 = line
    if pt1[0] == pt2[0]:  # holizonal
        if pt1[1] > pt2[1]:
            pt2, pt1 = line

        r = range(pt1[1], pt2[1], length)
        for y1, y2 in istep(r):
            yield [(pt1[0], y1), (pt1[0], y2)]

    elif pt1[1] == pt2[1]:  # vertical
        if pt1[0] > pt2[0]:
            pt2, pt1 = line

        r = range(pt1[0], pt2[0], length)
        for x1, x2 in istep(r):
            yield [(x1, pt1[1]), (x2, pt1[1])]
    else:  # diagonal
        if pt1[0] > pt2[0]:
            pt2, pt1 = line

        # DDA (Digital Differential Analyzer) Algorithm
        locus = []
        m = float(pt2[1] - pt1[1]) / float(pt2[0] - pt1[0])
        x = pt1[0]
        y = pt1[1]

        while x <= pt2[0]:
            locus.append((int(x), int(round(y))))
            x += 1
            y += m

        for p1, p2 in istep(islice(locus, None, None, length)):
            yield (p1, p2)


class ImageDrawEx(object):
    def __init__(self, filename, size, **kwargs):
        if kwargs.get('im'):
            self.image = kwargs.get('im')
        else:
            self.image = Image.new('RGB', size, (256, 256, 256))

            # set transparency to background
            alpha = Image.new('L', size, 1)
            self.image.putalpha(alpha)

        self.filename = filename
        self.scale_ratio = kwargs.get('scale_ratio', 1)
        self.mode = kwargs.get('mode')
        self.draw = ImageDraw.ImageDraw(self.image, self.mode)

    def resizeCanvas(self, size):
        image = self.image.resize(size, Image.ANTIALIAS)
        self.image = self.image.resize(size, Image.ANTIALIAS)
        self.draw = ImageDraw.ImageDraw(self.image, self.mode)

    def smoothCanvas(self):
        for i in range(15):
            self.image = self.image.filter(ImageFilter.SMOOTH_MORE)

        self.draw = ImageDraw.ImageDraw(self.image, self.mode)

    def arc(self, box, start, end, **kwargs):
        style = kwargs.get('style')
        if 'style' in kwargs:
            del kwargs['style']

        if style:
            if style == 'dotted':
                length = 2
            elif style == 'dashed':
                length = 4

            while start > end:
                end += 360

            for pt in ellipse.dots(box, length, start, end):
                self.draw.line([pt, pt], fill=kwargs['fill'])
        else:
            self.draw.arc(box, start, end, **kwargs)

    def ellipse(self, box, **kwargs):
        if 'filter' in kwargs:
            del kwargs['filter']

        style = kwargs.get('style')
        if 'style' in kwargs:
            del kwargs['style']

        if style:
            if kwargs.get('fill') != 'none':
                kwargs2 = dict(kwargs)
                if 'outline' in kwargs2:
                    del kwargs2['outline']
                self.draw.ellipse(box, **kwargs2)

            if 'outline' in kwargs:
                kwargs['fill'] = kwargs['outline']
                del kwargs['outline']

            if style == 'dotted':
                length = 2
            elif style == 'dashed':
                length = 4

            for pt in ellipse.dots(box, length):
                self.draw.line([pt, pt], fill=kwargs['fill'])
        else:
            if kwargs.get('fill') == 'none':
                del kwargs['fill']

            self.draw.ellipse(box, **kwargs)

    def line(self, xy, **kwargs):
        if 'jump' in kwargs:
            del kwargs['jump']

        style = kwargs.get('style')
        if kwargs.get('fill') == 'none':
            pass
        elif style in ('dotted', 'dashed'):
            self.dashed_line(xy, **kwargs)
        else:
            if 'style' in kwargs:
                del kwargs['style']

            self.draw.line(xy, **kwargs)

    def dashed_line(self, xy, **kwargs):
        style = kwargs.get('style')
        del kwargs['style']

        if style == 'dotted':
            length = 2
        elif style == 'dashed':
            length = 4

        for line in line_segments(xy):
            for subline in dashize_line(line, length):
                self.line(subline, **kwargs)

    def rectangle(self, box, **kwargs):
        thick = kwargs.get('width', self.scale_ratio)
        fill = kwargs.get('fill')
        outline = kwargs.get('outline')
        style = kwargs.get('style')

        if thick == 1:
            d = 0
        else:
            d = int(math.ceil(thick / 2.0))

        if fill and fill != 'none':
            self.draw.rectangle(box, fill=fill)

        x1, y1, x2, y2 = box
        lines = (((x1, y1), (x2, y1)), ((x1, y2), (x2, y2)),  # horizonal
                 ((x1, y1 - d), (x1, y2 + d)),  # vettical (left)
                 ((x2, y1 - d), (x2, y2 + d)))  # vertical (right)

        for line in lines:
            self.line(line, fill=outline, width=thick, style=style)

    def polygon(self, xy, **kwargs):
        if 'filter' in kwargs:
            del kwargs['filter']

        if kwargs.get('fill') != 'none':
            kwargs2 = dict(kwargs)

            if 'style' in kwargs2:
                del kwargs2['style']
            if 'outline' in kwargs2:
                del kwargs2['outline']
            self.draw.polygon(xy, **kwargs2)

        if kwargs.get('outline'):
            kwargs['fill'] = kwargs['outline']
            del kwargs['outline']
            self.line(xy, **kwargs)

    def text(self, xy, string, **kwargs):
        fill = kwargs.get('fill')
        font = kwargs.get('font')
        fontsize = kwargs.get('fontsize', 11)

        if font:
            ttfont = ImageFont.truetype(font, fontsize)
        else:
            ttfont = None

        if ttfont is None:
            if self.scale_ratio == 1:
                self.draw.text(xy, string, fill=fill)
            else:
                size = self.draw.textsize(string)
                image = Image.new('RGBA', size)
                draw = ImageDraw.Draw(image)
                draw.text((0, 0), string, fill=fill)
                del draw

                basesize = (size[0] * self.scale_ratio,
                            size[1] * self.scale_ratio)
                text_image = image.resize(basesize, Image.ANTIALIAS)

                self.image.paste(text_image, xy, text_image)
        else:
            size = self.draw.textsize(string, font=ttfont)

            # Generate mask to support BDF(bitmap font)
            mask = Image.new('1', size)
            draw = ImageDraw.Draw(mask)
            draw.text((0, 0), string, fill='white', font=ttfont)

            # Rendering text
            filler = Image.new('RGB', size, fill)
            self.image.paste(filler, xy, mask)

            self.draw = ImageDraw.ImageDraw(self.image, self.mode)

    def textarea(self, box, string, **kwargs):
        lines = TextFolder(box, string, scale=self.scale_ratio, **kwargs)

        if kwargs.get('outline'):
            outline = kwargs.get('outline')
            self.rectangle(lines.outlineBox(), fill='white', outline=outline)

        for string, xy in lines.each_line():
            self.text(xy, string, **kwargs)

    def loadImage(self, filename, box):
        box_width = box[2] - box[0]
        box_height = box[3] - box[1]

        if urlutil.isurl(filename):
            import cStringIO
            import urllib
            try:
                filename = cStringIO.StringIO(urllib.urlopen(filename).read())
            except:
                import sys
                msg = "WARNING: Could not retrieve: %s\n" % filename
                sys.stderr.write(msg)
                return
        image = Image.open(filename)

        # resize image.
        w = min([box_width, image.size[0] * self.scale_ratio])
        h = min([box_height, image.size[1] * self.scale_ratio])
        image.thumbnail((w, h), Image.ANTIALIAS)

        # centering image.
        w, h = image.size
        if box_width > w:
            x = box[0] + (box_width - w) / 2
        else:
            x = box[0]

        if box_height > h:
            y = box[1] + (box_height - h) / 2
        else:
            y = box[1]

        self.image.paste(image, (x, y))
        self.draw = ImageDraw.ImageDraw(self.image, self.mode)

    def save(self, filename, size, format):
        if filename:
            self.filename = filename

        if size is None:
            x = int(self.image.size[0] / self.scale_ratio)
            y = int(self.image.size[1] / self.scale_ratio)
            size = (x, y)

        self.image.thumbnail(size, Image.ANTIALIAS)

        if self.filename:
            self.image.save(self.filename, format)
            image = None
        else:
            import cStringIO
            tmp = cStringIO.StringIO()
            self.image.save(tmp, format)
            image = tmp.getvalue()

        return image
