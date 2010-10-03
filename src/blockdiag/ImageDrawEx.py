#!/usr/bin/python
# -*- coding: utf-8 -*-

import math
import Image
import ImageDraw
import ImageFont
import ImageFilter
from utils.XY import XY


class ImageDrawEx(ImageDraw.ImageDraw):
    def __init__(self, im, scale_ratio, mode=None):
        self.image = im
        self.scale_ratio = scale_ratio
        self.mode = mode
        ImageDraw.ImageDraw.__init__(self, im, mode)

    def rectangle(self, box, **kwargs):
        thick = kwargs.get('width', self.scale_ratio)
        fill = kwargs.get('fill')
        outline = kwargs.get('outline')

        if thick == 1:
            ImageDraw.ImageDraw.rectangle(self, box, **kwargs)
        else:
            d = math.ceil(thick / 2.0)

            ImageDraw.ImageDraw.rectangle(self, box, **kwargs)

            x1, y1, x2, y2 = box
            self.line(((x1, y1 - d), (x1, y2 + d)), fill=outline, width=thick)
            self.line(((x2, y1 - d), (x2, y2 + d)), fill=outline, width=thick)
            self.line(((x1, y1), (x2, y1)), fill=outline, width=thick)
            self.line(((x1, y2), (x2, y2)), fill=outline, width=thick)

    def setupFont(self, font, fontsize):
        if font:
            ttfont = ImageFont.truetype(font, fontsize)
        else:
            ttfont = None

        return ttfont

    def truetypeText(self, xy, string, **kwargs):
        fill = kwargs.get('fill')
        font = kwargs.get('font')
        fontsize = kwargs.get('fontsize', 11)
        ttfont = self.setupFont(font, fontsize)

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

    def text(self, box, string, **kwargs):
        fill = kwargs.get('fill')
        font = kwargs.get('font')
        fontsize = kwargs.get('fontsize', 11)
        ttfont = self.setupFont(font, fontsize)

        lineSpacing = kwargs.get('lineSpacing', 2)
        size = (box[2] - box[0], box[3] - box[1])

        lines = self._getFoldedText(size, string,
                                    font=ttfont, lineSpacing=lineSpacing)

        height = 0
        for string in lines:
            height += self.textsize(string, font=ttfont)[1] + lineSpacing

        height = (size[1] - (height - lineSpacing)) / 2
        xy = XY(box[0], box[1])
        for string in lines:
            textsize = self.textsize(string, font=ttfont)
            if ttfont:
                textspan = size[0] - textsize[0]
            else:
                textspan = size[0] - textsize[0] * self.scale_ratio

            x = int(math.ceil(textspan / 2.0))
            draw_xy = (xy.x + x, xy.y + height)
            self.truetypeText(draw_xy, string, fill=fill,
                              font=font, fontsize=fontsize)

            height += textsize[1] + lineSpacing

    def _getFoldedText(self, size, string, **kwargs):
        ttfont = kwargs.get('font')
        lineSpacing = kwargs.get('lineSpacing', 2)
        lines = []

        height = 0
        truncated = 0
        for line in string.splitlines():
            while line:
                string = string.strip()
                for i in range(0, len(string)):
                    length = len(string) - i
                    metrics = self.textsize(string[0:length], font=ttfont)

                    if metrics[0] <= size[0]:
                        break

                if size[1] < height + metrics[1]:
                    truncated = 1
                    break

                lines.append(line[0:length])
                line = line[length:]

                height += metrics[1] + lineSpacing

        # truncate last line.
        if truncated:
            string = lines.pop()
            for i in range(0, len(string)):
                if i == 0:
                    truncated = string + ' ...'
                else:
                    truncated = string[0:-i] + ' ...'

                size = self.textsize(truncated, font=ttfont)
                if size[0] <= size[0]:
                    lines.append(truncated)
                    break

        return lines

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
