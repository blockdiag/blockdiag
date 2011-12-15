# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os, sys
import pkg_resources

sys.path.insert(0, 'src')
import blockdiag


def is_installed(name):
    try:
        pkg_resources.get_distribution(name)
        return True
    except:
        return False


long_description = \
        open(os.path.join("src","README.txt")).read() + \
        open(os.path.join("src","TODO.txt")).read()

classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: System Administrators",
    "License :: OSI Approved :: Apache Software License",
    "Programming Language :: Python",
    "Topic :: Software Development",
    "Topic :: Software Development :: Documentation",
    "Topic :: Text Processing :: Markup",
]

requires = ['setuptools',
            'funcparserlib',
            'webcolors']
deplinks = []

# Find imaging libraries
if is_installed('PIL'):
    requires.append('PIL')
elif is_installed('Pillow'):
    requires.append('Pillow')
elif sys.platform == 'win32':
    requires.append('Pillow')
else:
    requires.append('PIL')


# only for Python2.6
if sys.version_info > (2, 6) and sys.version_info < (2, 7):
    requires.append('OrderedDict')


setup(
     name='blockdiag',
     version=blockdiag.__version__,
     description='blockdiag generate block-diagram image file from spec-text file.',
     long_description=long_description,
     classifiers=classifiers,
     keywords=['diagram','generator'],
     author='Takeshi Komiya',
     author_email='i.tkomiya at gmail.com',
     url='http://blockdiag.com/',
     license='Apache License 2.0',
     py_modules=['blockdiag_sphinxhelper'],
     packages=find_packages('src'),
     package_dir={'': 'src'},
     package_data = {'': ['buildout.cfg']},
     include_package_data=True,
     install_requires=requires,
     extras_require=dict(
         test=[
             'Nose',
             'pep8',
             'unittest2',
         ],
         pdf=[
             'reportlab',
         ],
         rst=[
             'docutils',
         ],
     ),
     dependency_links=deplinks,
     test_suite='nose.collector',
     tests_require=['Nose','pep8'],
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
     """,
)

