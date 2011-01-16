# -*- coding: utf-8 -*-

from XY import XY


def shift_box(box, x, y):
    shifted = (box[0] + x, box[1] + y,
               box[2] + x, box[3] + y)

    return shifted


def shift_points(points, x, y):
    shifted = []
    for pt in points:
        shifted.append(XY(pt[0] + x, pt[1] + y))

    return shifted
