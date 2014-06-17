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

from __future__ import division
import io
import re
from blockdiag.utils import urlutil
from blockdiag.utils.compat import u, string_types, urlopen
from blockdiag.utils.logging import warning

try:
    from PIL import Image
except ImportError:
    class Image:
        @classmethod
        def open(cls, filename):
            return cls(filename)

        def __init__(self, filename):
            self.filename = filename

        @property
        def size(self):
            from blockdiag.utils import jpeg
            import png

            try:
                size = jpeg.JpegFile.get_size(self.filename)
            except:
                try:
                    if isinstance(self.filename, string_types):
                        content = open(self.filename, 'r')
                    else:
                        self.filename.seek(0)
                        content = self.filename
                    image = png.Reader(file=content).read()
                    size = (image[0], image[1])
                except:
                    size = None

            if hasattr(self.filename, 'seek'):
                self.filename.seek(0)

            return size

_image_size_cache = {}


def get_image_size(filename):
    if filename not in _image_size_cache:
        uri = filename
        if urlutil.isurl(filename):
            try:
                uri = io.BytesIO(urlopen(filename).read())
            except IOError:
                raise RuntimeError('Could not retrieve: %s' % filename)

        try:
            _image_size_cache[filename] = Image.open(uri).size
        except:
            raise RuntimeError('Colud not get size of image: %s' % filename)

    return _image_size_cache[filename]


def calc_image_size(size, bounded):
    if bounded[0] < size[0] or bounded[1] < size[1]:
        if (size[0] * 1.0 // bounded[0]) < (size[1] * 1.0 // bounded[1]):
            size = (size[0] * bounded[1] // size[1], bounded[1])
        else:
            size = (bounded[0], size[1] * bounded[0] // size[0])

    return size


def color_to_rgb(color):
    import webcolors
    if color == 'none' or isinstance(color, (list, tuple)):
        rgb = color
    elif re.match('#', color):
        rgb = webcolors.hex_to_rgb(color)
    else:
        rgb = webcolors.name_to_rgb(color)

    return rgb


def convert_svg_to_png(filename, stream):
    if filename.lower().endswith('.svg'):
        try:
            import io
            import wand.image

            png_image = io.BytesIO()
            with wand.image.Image(file=stream) as img:
                img.format = 'PNG'
                img.save(file=png_image)
                png_image.seek(0)
                return png_image
        except ImportError:
            warning("wand library is required to embed SVG image.")
            raise IOError
        except Exception as exc:
            warning("Fail to convert SVG to PNG: %r", exc)
            raise IOError
    else:
        return stream


def open(url):
    if not urlutil.isurl(url):
        fd = io.open(url, 'rb')
    else:
        try:
            fd = io.BytesIO(urlopen(url).read())
        except:
            warning(u("Could not retrieve: %s"), url)
            raise IOError

    if url.lower().endswith('.svg'):
        svg = convert_svg_to_png(url, fd)
        fd.close()
        return svg
    else:
        return fd
