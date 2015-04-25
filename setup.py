# -*- coding: utf-8 -*-
import sys
from setuptools import setup, find_packages

sys.path.insert(0, 'src')
import blockdiag

classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: System Administrators",
    "License :: OSI Approved :: Apache Software License",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2.6",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3.2",
    "Programming Language :: Python :: 3.3",
    "Topic :: Software Development",
    "Topic :: Software Development :: Documentation",
    "Topic :: Text Processing :: Markup",
]

requires = ['setuptools',
            'funcparserlib',
            'Pillow']
pdf_requires = ['reportlab']
test_requires = ['nose',
                 'mock',
                 'pep8>=1.3',
                 'reportlab',
                 'docutils']


# only for Python2.6
if (2, 6) < sys.version_info < (2, 7):
    requires.append('OrderedDict')
    pdf_requires[0] = 'reportlab < 3.0'
    test_requires.append('unittest2')

# webcolors
if (3, 2) < sys.version_info < (3, 3):
    requires.append('webcolors < 1.5')  # webcolors-1.5 does not support py32
else:
    requires.append('webcolors')


setup(
    name='blockdiag',
    version=blockdiag.__version__,
    description='blockdiag generates block-diagram image from text',
    long_description=open("README.rst").read(),
    classifiers=classifiers,
    keywords=['diagram', 'generator'],
    author='Takeshi Komiya',
    author_email='i.tkomiya at gmail.com',
    url='http://blockdiag.com/',
    download_url='http://pypi.python.org/pypi/blockdiag',
    license='Apache License 2.0',
    py_modules=['blockdiag_sphinxhelper'],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    package_data={'': ['buildout.cfg']},
    include_package_data=True,
    install_requires=requires,
    extras_require=dict(
        testing=test_requires,
        pdf=pdf_requires,
        rst=[
            'docutils',
        ],
    ),
    test_suite='nose.collector',
    tests_require=test_requires,
    entry_points="""
       [console_scripts]
       blockdiag = blockdiag.command:main

       [blockdiag_noderenderer]
       box = blockdiag.noderenderer.box
       square = blockdiag.noderenderer.square
       roundedbox = blockdiag.noderenderer.roundedbox
       diamond = blockdiag.noderenderer.diamond
       minidiamond = blockdiag.noderenderer.minidiamond
       mail = blockdiag.noderenderer.mail
       note = blockdiag.noderenderer.note
       cloud = blockdiag.noderenderer.cloud
       circle = blockdiag.noderenderer.circle
       ellipse = blockdiag.noderenderer.ellipse
       beginpoint = blockdiag.noderenderer.beginpoint
       endpoint = blockdiag.noderenderer.endpoint
       actor = blockdiag.noderenderer.actor
       flowchart.database = blockdiag.noderenderer.flowchart.database
       flowchart.input = blockdiag.noderenderer.flowchart.input
       flowchart.loopin = blockdiag.noderenderer.flowchart.loopin
       flowchart.loopout = blockdiag.noderenderer.flowchart.loopout
       flowchart.terminator = blockdiag.noderenderer.flowchart.terminator
       textbox = blockdiag.noderenderer.textbox
       dots = blockdiag.noderenderer.dots
       none = blockdiag.noderenderer.none

       [blockdiag_plugins]
       attributes = blockdiag.plugins.attributes
       autoclass = blockdiag.plugins.autoclass

       [blockdiag_imagedrawers]
       imagedraw_png = blockdiag.imagedraw.png
       imagedraw_svg = blockdiag.imagedraw.svg
       imagedraw_pdf = blockdiag.imagedraw.pdf
    """,
)
