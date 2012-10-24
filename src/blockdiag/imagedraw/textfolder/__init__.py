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


def gen_factory(klass):
    def factory(box, string, font, **kwargs):
        if font is None:
            from base import TextFolder
            return TextFolder(box, string, font, **kwargs)
        else:
            return klass(box, string, font, **kwargs)

    return factory


def get(*args, **kwargs):
    try:
        if kwargs.get('format') == 'pdf' and kwargs.get('canvas'):
            import pdf
            TextFolder = gen_factory(pdf.TextFolder)
        else:
            if kwargs.get('ignore_pil'):
                from base import TextFolder
            else:
                import pil
                TextFolder = gen_factory(pil.TextFolder)
    except ImportError:
        from base import TextFolder

    return TextFolder(*args, **kwargs)
