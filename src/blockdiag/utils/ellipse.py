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


def circumference(a, b):
    """Return a length of a circumference of an ellipse.

    @param a, b length of two semi-axes

    reference: http://en.wikipedia.org/wiki/Ellipse#Circumference
    """
    expr = ((a - b) / (a + b)) ** 2
    return math.pi * (a + b) * \
           (1 + (3 * expr) / (10 + math.sqrt(4 - 3 * expr)))


def dots(box, cycle):
    width = box[2] - box[0]
    height = box[3] - box[1]
    center = XY(box[0] + width / 2, box[1] + height / 2)

    a = float(width) / 2
    b = float(height) / 2
    du = circumference(a, b) / DIVISION

    for i, coord in enumerate(coordinate(du, a, b)):
        i %= cycle * 2
        if i < cycle:
            dot = XY(center.x + coord[0], center.y + coord[1])
            yield dot
