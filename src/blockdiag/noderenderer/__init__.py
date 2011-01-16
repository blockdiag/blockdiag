# -*- coding: utf-8 -*-
import box
import diamond
import flowchart.terminator

shapes = {'box': box,
          'diamond': diamond,
          'flowchart.terminator': flowchart.terminator}


def get(shape):
    return shapes[shape]
