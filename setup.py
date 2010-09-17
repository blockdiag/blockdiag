# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os, sys

version = '0.0.1'
long_description = \
        open(os.path.join("src","README.txt")).read() + \
        open(os.path.join("src","TODO.txt")).read()

classifiers = [
    "Development Status :: 2 - Pre-Alpha",
    #"Development Status :: 3 - Alpha",
    #"Development Status :: 4 - Beta",
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
     description='blockdiag generate block-diagram image file from spec-text file..',
     long_description=long_description,
     classifiers=classifiers,
     keywords=['diagram','generator','yaml'],
     author='Takeshi Komiya',
     author_email='tk0miya at gmail.com',
     url='http://bitbucket.org/tk0miya/blockdiag',
     license='PSL',
     packages=find_packages('src'),
     package_dir={'': 'src'},
     package_data = {'': ['buildout.cfg']},
     include_package_data=True,
     install_requires=[
        'setuptools',
        'PIL',
        'PyYAML',
         # -*- Extra requirements: -*-
     ],
     extras_require=dict(
         test=[
             'Nose',
             'minimock',
         ],
     ),
     test_suite='nose.collector',
     tests_require=['Nose','minimock'],
     entry_points="""
        [console_scripts]
        blockdiag = blockdiag:main
     """,
)

