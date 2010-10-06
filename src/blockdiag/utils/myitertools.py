# -*- coding: utf-8 -*-


def istep(seq, step=2):
    iterable = iter(seq)
    while True:
        yield [iterable.next() for i in range(step)]
