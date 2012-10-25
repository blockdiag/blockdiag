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


class ImageDraw(object):
    self_generative_methods = []
    nosideeffect_methods = ['textsize', 'textlinesize']
    supported_path = False

    def line(self, xy, **kwargs):
        pass

    def rectangle(self, box, **kwargs):
        pass

    def polygon(self, xy, **kwargs):
        pass

    def arc(self, xy, start, end, **kwargs):
        pass

    def ellipse(self, xy, **kwargs):
        pass

    def textsize(self, string, font, maxwidth=None, **kwargs):
        pass

    def textlinesize(self, string, font, **kwargs):
        pass

    def text(self, xy, string, font, **kwargs):
        pass

    def textarea(self, box, string, font, **kwargs):
        pass

    def image(self, box, url):
        pass

    def loadImage(self, filename, box):  # TODO: obsoleted
        return self.image(box, filename)

    def save(self, filename, size, format):
        pass
