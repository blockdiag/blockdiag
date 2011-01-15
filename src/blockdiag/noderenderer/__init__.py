# -*- coding: utf-8 -*-
import box
import flowchart.terminator

shapes = {'box': box,
          'flowchart.terminator': flowchart.terminator}


def get(shape):
    return shapes[shape]
