`blockdiag` generate block-diagram image file from spec-text file.

Features
========

* Generate block-diagram from yaml (basic feature).
* ...

Setup
=====

by easy_install
----------------
Make environment::

   $ easy_install blockdiag

by buildout
------------
Make environment::

   $ hg clone http://bitbucket.org/tk0miya/blockdiag
   $ cd blockdiag
   $ python bootstrap.py
   $ bin/buildout

Copy and modify ini file. example::

   $ cp <blockdiag installed path>/blockdiag/examples/screen.yaml .
   $ vi screen.yaml

Please refer to `spec-text setting sample`_ section for the format of the
`screen.yaml` configuration file.

spec-text setting sample
========================

screen.yaml::

    ---
    - ほげほげ一覧画面:
      - ほげほげ詳細画面:
        - ほげほげ設定画面
        - ほげほげ編集画面
      - ほげほげ削除確認画面
    - ふがふが一覧画面:
      - ふがふが設定画面

Usage
=====

Execute blockdiag command::

   $ blockdiag screen.yaml


Requirements
============

* Python 2.4 or later (not support 3.x)
* Python Imaging Library 1.1.6 or later.
* setuptools or distriubte

History
=======

0.0.1 (unreleased)
------------------
* first release


