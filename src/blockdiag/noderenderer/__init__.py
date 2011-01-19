# -*- coding: utf-8 -*-
import pkg_resources

shapes = {}


def init():
    for plugin in pkg_resources.iter_entry_points('blockdiag_noderenderer'):
        module = plugin.load()
        if hasattr(module, 'setup'):
            module.setup(module)


def install_renderer(name, renderer):
    shapes[name] = renderer


def get(shape):
    return shapes[shape]
