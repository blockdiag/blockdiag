# -*- coding: utf-8 -*-
import box
import diamond
import flowchart.terminator
import flowchart.condition
import flowchart.database
import flowchart.loopin
import flowchart.loopout
import flowchart.input

shapes = {'box': box,
          'diamond': diamond,
          'flowchart.terminator': flowchart.terminator,
          'flowchart.condition': flowchart.condition,
          'flowchart.loopin': flowchart.loopin,
          'flowchart.loopout': flowchart.loopout,
          'flowchart.database': flowchart.database,
          'flowchart.input': flowchart.input,
          'flowchart.terminator': flowchart.terminator
          }

def get(shape):
    return shapes[shape]
