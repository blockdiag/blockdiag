#!/usr/bin/python
# -*- coding: utf-8 -*-

import math
from itertools import islice, izip, tee
from utils.myitertools import istep
from utils.PILTextFolder import PILTextFolder as TextFolder
import Image
import ImageDraw
import ImageFont
import ImageFilter
from utils.XY import XY


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


class ImageDrawEx(ImageDraw.ImageDraw):
    def __init__(self, size, scale_ratio, im=None, mode=None):
        if im:
            self.image = im
        else:
            self.image = Image.new('RGB', size, (256, 256, 256))

        self.scale_ratio = scale_ratio
        self.mode = mode
        ImageDraw.ImageDraw.__init__(self, self.image, mode)

    def resizeCanvas(self, size):
        image = self.image.resize(size, Image.ANTIALIAS)
        return ImageDrawEx(None, self.scale_ratio, im=image)

    def smoothCanvas(self):
        image = self.image
        for i in range(15):
            image = image.filter(ImageFilter.SMOOTH_MORE)

        return ImageDrawEx(None, self.scale_ratio, im=image)

    def arc(self, box, start, end, **kwargs):
        style = kwargs.get('style')
        if 'style' in kwargs:
            del kwargs['style']

        if style:
            if style == 'dotted':
                length = 6
            elif style == 'dashed':
                length = 3

            if end == 0:
                end = 360

            diff = (end - start) / length

            for i in range(length):
                s = start + diff * (i * 2)
                e = start + diff * (i * 2 + 1)

                if e > end:
                    continue

                ImageDraw.ImageDraw.arc(self, box, s, e, **kwargs)
        else:
            ImageDraw.ImageDraw.arc(self, box, start, end, **kwargs)

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
                ImageDraw.ImageDraw.ellipse(self, box, **kwargs2)

            if 'outline' in kwargs:
                kwargs['fill'] = kwargs['outline']
                del kwargs['outline']

            if style == 'dotted':
                length = 48
            elif style == 'dashed':
                length = 24

            start = 0
            end = 360
            diff = (end - start) / length

            for i in range(length):
                s = start + diff * (i * 2)
                e = start + diff * (i * 2 + 1)

                if e > end:
                    continue

                ImageDraw.ImageDraw.arc(self, box, s, e, **kwargs)
        else:
            ImageDraw.ImageDraw.ellipse(self, box, **kwargs)

    def line(self, xy, **kwargs):
        style = kwargs.get('style')

        if style in ('dotted', 'dashed'):
            self.dashed_line(xy, **kwargs)
        else:
            if 'style' in kwargs:
                del kwargs['style']

            ImageDraw.ImageDraw.line(self, xy, **kwargs)

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

        if fill:
            ImageDraw.ImageDraw.rectangle(self, box, fill=fill)

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
            ImageDraw.ImageDraw.polygon(self, xy, **kwargs2)

        if kwargs.get('outline'):
            kwargs['fill'] = kwargs['outline']
            del kwargs['outline']
            self.line(xy, **kwargs)

    def label(self, box, string, **kwargs):
        lines = TextFolder(box, string, adjustBaseline=True, **kwargs)

        self.rectangle(lines.outlineBox(), fill='white', outline='black')
        self.textarea(box, string, **kwargs)

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
                ImageDraw.ImageDraw.text(self, xy, string, fill=fill)
            else:
                size = self.textsize(string)
                image = Image.new('RGBA', size)
                draw = ImageDraw.Draw(image)
                draw.text((0, 0), string, fill=fill)
                del draw

                basesize = (size[0] * self.scale_ratio,
                            size[1] * self.scale_ratio)
                text_image = image.resize(basesize, Image.ANTIALIAS)

                self.image.paste(text_image, xy, text_image)
        else:
            size = self.textsize(string, font=ttfont)

            # Generate mask to support BDF(bitmap font)
            mask = Image.new('1', size)
            draw = ImageDraw.Draw(mask)
            draw.text((0, 0), string, fill='white', font=ttfont)

            # Rendering text
            filler = Image.new('RGB', size, fill)
            self.image.paste(filler, xy, mask)

            ImageDraw.ImageDraw.__init__(self, self.image, self.mode)

    def textarea(self, box, string, **kwargs):
        lines = TextFolder(box, string, scale=self.scale_ratio, **kwargs)
        for string, xy in lines.each_line():
            self.text(xy, string, **kwargs)

    def loadImage(self, filename, box):
        box_width = box[2] - box[0]
        box_height = box[3] - box[1]

        # resize image.
        image = Image.open(filename)
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
        ImageDraw.ImageDraw.__init__(self, self.image, self.mode)

    def save(self, filename, size, format):
        self.image.thumbnail(size, Image.ANTIALIAS)
        self.image.save(filename, format)
