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

import re
import urlutil
try:
    from PIL import Image
except ImportError:
    try:
        import Image
    except ImportError:
        class Image:
            @classmethod
            def open(cls, filename):
                return cls(filename)

            def __init__(self, filename):
                self.filename = filename

            @property
            def size(self):
                import jpeg
                import png

                try:
                    size = jpeg.JpegFile.get_size(self.filename)
                except:
                    try:
                        if isinstance(self.filename, (str, unicode)):
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
            import cStringIO
            import urllib
            try:
                uri = cStringIO.StringIO(urllib.urlopen(filename).read())
            except:
                return None

        _image_size_cache[filename] = Image.open(uri).size

    return _image_size_cache[filename]


def calc_image_size(size, bounded):
    if bounded[0] < size[0] or bounded[1] < size[1]:
        if (size[0] * 1.0 / bounded[0]) < (size[1] * 1.0 / bounded[1]):
            size = (size[0] * bounded[1] / size[1], bounded[1])
        else:
            size = (bounded[0], size[1] * bounded[0] / size[0])

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
