# -*- coding: utf-8 -*-

import os
import pep8

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(CURRENT_DIR)


def test_pep8():
    arglist = [
        '--statistics',
        '--filename=*.py',
        '--show-source',
        '--repeat',
        #'--show-pep8',
        #'-qq',
        #'-v',
        BASE_DIR,
    ]

    options, args = pep8.process_options(arglist)
    runner = pep8.input_file

    for path in args:
        if os.path.isdir(path):
            pep8.input_dir(path, runner=runner)
        elif not pep8.excluded(path):
            options.counters['files'] += 1
            runner(path)

    pep8.print_statistics()
    count = pep8.get_count()
    assert count == 0
