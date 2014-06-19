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
from PIL import Image
from blockdiag.utils import urlutil
from blockdiag.utils.compat import u, urlopen
from blockdiag.utils.logging import warning

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


def wand_open(url, stream):
    try:
        import wand.image
    except:
        warning("unknown image type: %s", url)
        raise IOError

    try:
        png_image = io.BytesIO()
        with wand.image.Image(file=stream) as img:
            img.format = 'PNG'
            img.save(file=png_image)
            png_image.seek(0)
            return png_image
    except Exception as exc:
        warning("Fail to convert %s to PNG: %r", url, exc)
        raise IOError


def pillow_open(url, stream):
    try:
        return Image.open(stream)
    except IOError:
        stream.seek(0)
        png_stream = wand_open(url, stream)

        return Image.open(png_stream)


def open(url, mode='Pillow'):
    if not urlutil.isurl(url):
        stream = io.open(url, 'rb')
    else:
        try:
            # wrap BytesIO for rewind stream
            stream = io.BytesIO(urlopen(url).read())
        except:
            warning(u("Could not retrieve: %s"), url)
            raise IOError

    image = pillow_open(url, stream)
    if mode.lower() == 'pillow':
        # stream will be closed by GC
        return image
    else:  # mode == 'png'
        png_image = io.BytesIO()
        image.save(png_image, 'PNG')
        stream.close()

        png_image.seek(0)
        return png_image
