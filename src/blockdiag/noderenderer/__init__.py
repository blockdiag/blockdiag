# -*- coding: utf-8 -*-
import box
import flowchart.terminator
import flowchart.condition
import flowchart.database

shapes = {'box': box,
          'flowchart.terminator': flowchart.terminator,
	  'flowchart.condition': flowchart.condition,
	  'flowchart.database': flowchart.database}


def get(shape):
    return shapes[shape]
