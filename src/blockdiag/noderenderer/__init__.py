# -*- coding: utf-8 -*-
import pkg_resources

renderers = {}


def init_renderers():
    for plugin in pkg_resources.iter_entry_points('blockdiag_noderenderer'):
        module = plugin.load()
        if hasattr(module, 'setup'):
            module.setup(module)


def install_renderer(name, renderer):
    renderers[name] = renderer


def get(shape):
    if not renderers:
        init_renderers()

    return renderers[shape]
