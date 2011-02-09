# -*- coding: utf-8 -*-
import sys
import math
from XY import XY

DIVISION = 1000.0
CYCLE = 10


def angles(du, a, b):
    phi = 0
    while phi <= 2 * math.pi:
        yield phi
        phi += du / math.sqrt((a * math.sin(phi)) ** 2 + \
                              (b * math.cos(phi)) ** 2)


def coordinate(du, a, b):
    for angle in angles(du, a, b):
        yield (a * math.cos(angle), b * math.sin(angle))


def dots(box, cycle):
    width = box[2] - box[0]
    height = box[3] - box[1]
    center = XY(box[0] + width / 2, box[1] + height / 2)

    a = float(width) / 2
    b = float(height) / 2
    du = 1

    for i, coord in enumerate(coordinate(du, a, b)):
        i %= cycle * 2
        if i < cycle:
            dot = XY(center.x + coord[0], center.y + coord[1])
            yield dot
