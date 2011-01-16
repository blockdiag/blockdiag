# -*- coding: utf-8 -*-
import box
import flowchart.terminator
import flowchart.condition
import flowchart.database
import flowchart.loopin
import flowchart.loopout

shapes = {'box': box,
          'flowchart.terminator': flowchart.terminator,
	  'flowchart.condition': flowchart.condition,
	  'flowchart.loopin': flowchart.loopin,
	  'flowchart.loopout': flowchart.loopout,
	  'flowchart.database': flowchart.database}


def get(shape):
    return shapes[shape]
