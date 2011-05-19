# -*- coding: utf-8 -*-
#  Copyright 2011 Takeshi KOMIYA
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

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
