# -*- coding: utf-8 -*-
import box
import roundedbox
import note
import diamond
import ellipse
import flowchart.terminator
import flowchart.database
import flowchart.loopin
import flowchart.loopout
import flowchart.input

shapes = {'box': box,
          'roundedbox': roundedbox,
          'note': note,
          'diamond': diamond,
          'ellipse': ellipse,
          'flowchart.terminator': flowchart.terminator,
          'flowchart.condition': diamond,
          'flowchart.loopin': flowchart.loopin,
          'flowchart.loopout': flowchart.loopout,
          'flowchart.database': flowchart.database,
          'flowchart.input': flowchart.input,
          'flowchart.terminator': flowchart.terminator
          }


def get(shape):
    return shapes[shape]
