`blockdiag` generate block-diagram image file from spec-text file.

Features
========

* Generate block-diagram from yaml (basic feature).
* ...

Setup
=====

Make environment (by easy_install)::

   $ easy_install blockdiag

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

Execute svnpoller command::

   $ blockdiag screen.yaml


Requirements
============

* Python 2.4 or later (not support 3.x)
* Python Imaging Library 1.1.6 or later.
* setuptools or distriubte


History
=======


0.0.1 (2010-xx-xx)
------------------
* first release


