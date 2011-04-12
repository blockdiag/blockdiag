`blockdiag` generate block-diagram image file from spec-text file.

Features
========

* Generate block-diagram from dot like text (basic feature).
* Multilingualization for node-label (utf-8 only).

You can get some examples and generated images on 
`tk0miya.bitbucket.org <http://tk0miya.bitbucket.org/blockdiag/build/html/index.html>`_ .

Setup
=====

by easy_install
----------------
Make environment::

   $ easy_install blockdiag

If you want to export as PDF format, give pdf arguments::

   $ easy_install "blockdiag[pdf]"

by buildout
------------
Make environment::

   $ hg clone http://bitbucket.org/tk0miya/blockdiag
   $ cd blockdiag
   $ python bootstrap.py
   $ bin/buildout

Copy and modify ini file. example::

   $ cp <blockdiag installed path>/blockdiag/examples/simple.diag .
   $ vi simple.diag

Please refer to `spec-text setting sample`_ section for the format of the
`simpla.diag` configuration file.

spec-text setting sample
========================

Few examples are available.
You can get more examples at
`tk0miya.bitbucket.org <http://tk0miya.bitbucket.org/blockdiag/build/html/index.html>`_ .

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

* Python 2.4 or later (not support 3.x)
* Python Imaging Library 1.1.6 or later.
* funcparserlib 0.3.4 or later.
* setuptools or distriubte.


License
=======
Python Software Foundation License.


History
=======

0.7.7 (2011-03-29)
------------------
* Fix bugs

0.7.6 (2011-03-26)
------------------
* Add new layout manager for portrait edges
* Fix bugs

0.7.5 (2011-03-20)
------------------
* Support multiple nodes relations (cf. A -> B, C)
* Support node group declaration at attribute of nodes
* Fix bugs

0.7.4 (2011-03-08)
------------------
* Fix bugs

0.7.3 (2011-03-02)
------------------
* Use UTF-8 characters as Name token (by @swtw7466)
* Fix htmlentities included in labels was not escaped on SVG images
* Fix bugs

0.7.2 (2011-02-28)
------------------
* Add default_shape attribute to diagram

0.7.1 (2011-02-27)
------------------
* Fix edge has broken with antialias option

0.7.0 (2011-02-25)
------------------
* Support node shape

0.6.7 (2011-02-12)
------------------
* Change noderenderer interface to new style
* Render dashed ellipse more clearly (contributed by @cocoatomo)
* Support PDF exporting

0.6.6 (2011-01-31)
------------------
* Support diagram.shape_namespace
* Add new node shapes; mail, cloud, beginpoint, endpoint, minidiamond, actor
* Support plug-in structure to install node shapes
* Fix bugs

0.6.5 (2011-01-18)
------------------
* Support node shape (experimental)

0.6.4 (2011-01-17)
------------------
* Fix bugs

0.6.3 (2011-01-15)
------------------
* Fix bugs

0.6.2 (2011-01-08)
------------------
* Fix bugs

0.6.1 (2011-01-07)
------------------
* Implement 'folded' attribute for edge
* Refactor layout engine

0.6 (2011-01-02)
------------------
* Support nested groups.

0.5.5 (2010-12-24)
------------------
* Specify direction of edges as syntax (->, --, <-, <->)
* Fix bugs.

0.5.4 (2010-12-23)
------------------
* Remove debug codes.

0.5.3 (2010-12-23)
------------------
* Support NodeGroup.label.
* Implement --separate option (experimental)
* Fix right-up edge overrapped on other nodes.
* Support configration file: .blockdiagrc

0.5.2 (2010-11-06)
------------------
* Fix unicode errors for UTF-8'ed SVG exportion.
* Refactoring codes for running on GAE.

0.5.1 (2010-10-26)
------------------
* Fix license text on diagparser.py
* Update layout engine.

0.5 (2010-10-15)
------------------
* Support background-image of node (SVG)
* Support labels for edge.
* Fix bugs.

0.4.2 (2010-10-10)
------------------
* Support background-color of node groups.
* Draw edge has jumped at edge's cross-points.
* Fix bugs.

0.4.1 (2010-10-07)
------------------
* Fix bugs.

0.4 (2010-10-07)
------------------
* Support SVG exporting.
* Support dashed edge drawing.
* Support background image of nodes (PNG only)

0.3.1 (2010-09-29)
------------------
* Fasten anti-alias process.
* Fix text was broken on windows.

0.3 (2010-09-26)
------------------
* Add --antialias option.
* Fix bugs.

0.2.2 (2010-09-25)
------------------
* Fix edge bugs.

0.2.1 (2010-09-25)
------------------
* Fix bugs.
* Fix package style.

0.2 (2010-09-23)
------------------
* Update layout engine.
* Support group { ... } sentence for create Node-Groups.
* Support numbered badge on node (cf. A [numbered = 5])

0.1 (2010-09-20)
-----------------
* first release

