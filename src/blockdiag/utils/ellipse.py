# -*- coding: utf-8 -*-
import sys
import math
from XY import XY

DIVISION = 1000.0
CYCLE = 10


def angles(du, a, b, start, end):
    phi = (start / 180.0) * math.pi
    while phi <= (end / 180.0) * math.pi:
        yield phi
        phi += du / math.sqrt((a * math.sin(phi)) ** 2 + \
                              (b * math.cos(phi)) ** 2)


def coordinate(du, a, b, start, end):
    for angle in angles(du, a, b, start, end):
        yield (a * math.cos(angle), b * math.sin(angle))


def dots(box, cycle, start=0, end=360):
    width = box[2] - box[0]
    height = box[3] - box[1]
    center = XY(box[0] + width / 2, box[1] + height / 2)

    a = float(width) / 2
    b = float(height) / 2
    du = 1

    for i, coord in enumerate(coordinate(du, a, b, start, end)):
        i %= cycle * 2
        if i < cycle:
            dot = XY(center.x + coord[0], center.y + coord[1])
            yield dot
