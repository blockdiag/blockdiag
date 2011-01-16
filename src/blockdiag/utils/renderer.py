# -*- coding: utf-8 -*-


def shift_box(box, x, y):
    shifted = (box[0] + x, box[1] + y,
               box[2] + x, box[3] + y)

    return shifted

def shift_polygon(polygon, x, y):
    return [(p[0]+x, p[1]+y) for p in polygon]
