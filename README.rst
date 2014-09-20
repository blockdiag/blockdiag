`blockdiag` generate block-diagram image file from spec-text file.

.. image:: https://drone.io/bitbucket.org/blockdiag/blockdiag/status.png
   :target: https://drone.io/bitbucket.org/blockdiag/blockdiag
   :alt: drone.io CI build status

.. image:: https://pypip.in/v/blockdiag/badge.png
   :target: https://pypi.python.org/pypi/blockdiag/
   :alt: Latest PyPI version

.. image:: https://pypip.in/d/blockdiag/badge.png
   :target: https://pypi.python.org/pypi/blockdiag/
   :alt: Number of PyPI downloads


Features
========
* Generate block-diagram from dot like text (basic feature).
* Multilingualization for node-label (utf-8 only).

You can get some examples and generated images on
`blockdiag.com <http://blockdiag.com/blockdiag/build/html/index.html>`_ .

Setup
=====

Use easy_install or pip::

   $ sudo easy_install blockdiag

   Or

   $ sudo pip install blockdiag

If you want to export as PDF format, give pdf arguments::

   $ sudo easy_install "blockdiag[pdf]"


Copy and modify ini file. example::

   $ cp <blockdiag installed path>/blockdiag/examples/simple.diag .
   $ vi simple.diag

Please refer to `spec-text setting sample`_ section for the format of the
`simpla.diag` configuration file.

spec-text setting sample
========================
Few examples are available.
You can get more examples at
`blockdiag.com`_ .

simple.diag
------------
simple.diag is simply define nodes and transitions by dot-like text format::

    diagram admin {
      top_page -> config -> config_edit -> config_confirm -> top_page;
    }

screen.diag
------------
screen.diag is more complexly sample. diaglam nodes have a alternative label
and some transitions::

    diagram admin {
      top_page [label = "Top page"];

      foo_index [label = "List of FOOs"];
      foo_detail [label = "Detail FOO"];
      foo_add [label = "Add FOO"];
      foo_add_confirm [label = "Add FOO (confirm)"];
      foo_edit [label = "Edit FOO"];
      foo_edit_confirm [label = "Edit FOO (confirm)"];
      foo_delete_confirm [label = "Delete FOO (confirm)"];

      bar_detail [label = "Detail of BAR"];
      bar_edit [label = "Edit BAR"];
      bar_edit_confirm [label = "Edit BAR (confirm)"];

      logout;

      top_page -> foo_index;
      top_page -> bar_detail;

      foo_index -> foo_detail;
                   foo_detail -> foo_edit;
                   foo_detail -> foo_delete_confirm;
      foo_index -> foo_add -> foo_add_confirm -> foo_index;
      foo_index -> foo_edit -> foo_edit_confirm -> foo_index;
      foo_index -> foo_delete_confirm -> foo_index;

      bar_detail -> bar_edit -> bar_edit_confirm -> bar_detail;
    }


Usage
=====
Execute blockdiag command::

   $ blockdiag simple.diag
   $ ls simple.png
   simple.png


Requirements
============
* Python 2.6, 2.7, 3.2, 3.3, 3.4
* Pillow 2.2.1 or later
* funcparserlib 0.3.6 or later
* reportlab (optional)
* wand and imagemagick (optional)
* setuptools


License
=======
Apache License 2.0
