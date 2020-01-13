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

import os
import unittest

from blockdiag.command import BlockdiagApp
from blockdiag.tests.utils import TemporaryDirectory


class TestBlockdiagApp(unittest.TestCase):
    def test_app_cleans_up_images(self):
        testdir = os.path.dirname(__file__)
        diagpath = os.path.join(testdir,
                                'diagrams',
                                'background_url_image.diag')
        urlopen_cache = {}

        def cleanup():
            from blockdiag.utils import images
            urlopen_cache.update(images.urlopen_cache)

        try:
            tmpdir = TemporaryDirectory()
            fd, tmpfile = tmpdir.mkstemp()
            os.close(fd)

            args = ['-T', 'SVG', '-o', tmpfile, diagpath]
            app = BlockdiagApp()
            app.register_cleanup_handler(cleanup)  # to get internal state
            app.run(args)

            self.assertTrue(urlopen_cache)  # check images were cached
            for path in urlopen_cache.values():
                self.assertFalse(os.path.exists(path))  # and removed finally
        finally:
            tmpdir.clean()

    def test_app_cleans_up_plugins(self):
        testdir = os.path.dirname(__file__)
        diagpath = os.path.join(testdir,
                                'diagrams',
                                'plugin_autoclass.diag')
        loaded_plugins = []

        def cleanup():
            from blockdiag import plugins
            loaded_plugins.extend(plugins.loaded_plugins)

        try:
            tmpdir = TemporaryDirectory()
            fd, tmpfile = tmpdir.mkstemp()
            os.close(fd)

            args = ['-T', 'SVG', '-o', tmpfile, diagpath]
            app = BlockdiagApp()
            app.register_cleanup_handler(cleanup)  # to get internal state
            app.run(args)

            from blockdiag import plugins
            self.assertTrue(loaded_plugins)  # check plugins were loaded
            self.assertFalse(plugins.loaded_plugins)  # and unloaded finally
        finally:
            tmpdir.clean()
