#!/usr/bin/python
# -*- coding: utf-8 -*-

from types import MethodType
from utils.XY import XY
from DiagramMetrix import *
import noderenderer


class Scaler:
    def scale(self, value):
        ratio = self.scale_ratio

        if isinstance(value, XY):
            ret = XY(value.x * ratio, value.y * ratio)
        elif isinstance(value, tuple):
            ret = tuple([self.scale(x) for x in value])
        elif isinstance(value, list):
            ret = [self.scale(x) for x in value]
        elif isinstance(value, int):
            ret = value * ratio
        else:
            ret = value

        return ret

    def define_proxy_attribute(self, name):
        value = getattr(self.metrix, name)
        setattr(self, name, value)

    def define_scale_attribute(self, name):
        if hasattr(self.metrix, name):
            value = getattr(self.metrix, name)
            setattr(self, name, self.scale(value))

    def define_scale_method(self, name):
        def scale_method(self, *args, **kwargs):
            func = getattr(self.metrix, name)
            ret = func(*args, **kwargs)

            return self.scale(ret)

        method = MethodType(scale_method, self, self.__class__)
        setattr(self, name, method)


class PngDiagramMetrix(Scaler):
    def __init__(self, diagram, scale, **kwargs):
        self.scale_ratio = scale
        self.metrix = DiagramMetrix(diagram, **kwargs)

        # variables
        self.define_scale_attribute('cellSize')
        self.define_scale_attribute('nodePadding')
        self.define_scale_attribute('lineSpacing')
        self.define_scale_attribute('shadowOffsetX')
        self.define_scale_attribute('shadowOffsetY')
        self.define_scale_attribute('nodeWidth')
        self.define_scale_attribute('nodeHeight')
        self.define_scale_attribute('spanWidth')
        self.define_scale_attribute('spanHeight')
        self.define_scale_attribute('fontSize')
        self.define_scale_attribute('pageMargin')

        # methods
        self.define_scale_method('pageSize')

    def originalMetrix(self):
        return self.metrix

    def cell(self, node):
        base = NodeMetrix(node, self.originalMetrix())
        return PngNodeMetrix(node, self, base)

    def node(self, node):
        metrix = self.originalMetrix()
        renderer = noderenderer.get(node.shape)

        if hasattr(renderer, 'NodeMetrix'):
            base = getattr(renderer, 'NodeMetrix')(node, metrix)
        elif hasattr(renderer, 'render'):
            return renderer(node, metrix)
        else:
            base = NodeMetrix(node, metrix)

        return PngNodeMetrix(node, self, base)

    def group(self, group):
        return PngNodeMetrix(group, self)

    def edge(self, edge):
        return PngEdgeMetrix(edge, self)


class PngNodeMetrix(Scaler):
    def __init__(self, node, metrix, base_metrix):
        self.scale_ratio = metrix.scale_ratio
        self.metrix = base_metrix

        # variables
        self.define_scale_attribute('x')
        self.define_scale_attribute('y')

        # methods
        self.define_scale_method('box')
        self.define_scale_method('marginBox')
        self.define_scale_method('coreBox')
        self.define_scale_method('groupLabelBox')

        self.define_scale_method('topLeft')
        self.define_scale_method('topCenter')
        self.define_scale_method('topRight')
        self.define_scale_method('bottomLeft')
        self.define_scale_method('bottomCenter')
        self.define_scale_method('bottomRight')
        self.define_scale_method('leftCenter')
        self.define_scale_method('rightCenter')
        self.define_scale_method('center')

        self.define_scale_method('top')
        self.define_scale_method('bottom')
        self.define_scale_method('right')
        self.define_scale_method('left')


class PngEdgeMetrix(EdgeMetrix):
    pass
