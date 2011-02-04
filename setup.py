# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os, sys

version = '0.6.6'
long_description = \
        open(os.path.join("src","README.txt")).read() + \
        open(os.path.join("src","TODO.txt")).read()

classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: System Administrators",
    "License :: OSI Approved :: Python Software Foundation License",
    "Programming Language :: Python",
    "Topic :: Software Development",
    "Topic :: Software Development :: Documentation",
    "Topic :: Text Processing :: Markup",
]

setup(
     name='blockdiag',
     version=version,
     description='blockdiag generate block-diagram image file from spec-text file.',
     long_description=long_description,
     classifiers=classifiers,
     keywords=['diagram','generator'],
     author='Takeshi Komiya',
     author_email='i.tkomiya at gmail.com',
     url='http://tk0miya.bitbucket.org/blockdiag/build/html/index.html',
     license='PSL',
     py_modules=['blockdiag_sphinxhelper'],
     packages=find_packages('src'),
     package_dir={'': 'src'},
     package_data = {'': ['buildout.cfg']},
     include_package_data=True,
     install_requires=[
        'setuptools',
        'PIL',
        'funcparserlib',
         # -*- Extra requirements: -*-
     ],
     extras_require=dict(
         test=[
             'Nose',
             'minimock',
             'pep8',
         ],
     ),
     test_suite='nose.collector',
     tests_require=['Nose','minimock','pep8'],
     entry_points="""
        [console_scripts]
        blockdiag = blockdiag:main

        [blockdiag_noderenderer]
        box = blockdiag.noderenderer.box
        roundedbox = blockdiag.noderenderer.roundedbox
        diamond = blockdiag.noderenderer.diamond
        minidiamond = blockdiag.noderenderer.minidiamond
        mail = blockdiag.noderenderer.mail
        note = blockdiag.noderenderer.note
        cloud = blockdiag.noderenderer.cloud
        ellipse = blockdiag.noderenderer.ellipse
        beginpoint = blockdiag.noderenderer.beginpoint
        endpoint = blockdiag.noderenderer.endpoint
        actor = blockdiag.noderenderer.actor
        flowchart.database = blockdiag.noderenderer.flowchart.database
        flowchart.input = blockdiag.noderenderer.flowchart.input
        flowchart.loopin = blockdiag.noderenderer.flowchart.loopin
        flowchart.loopout = blockdiag.noderenderer.flowchart.loopout
        flowchart.terminator = blockdiag.noderenderer.flowchart.terminator
     """,
)

