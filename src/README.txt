`blockdiag` generate block-diagram image file from spec-text file.

Features
========
* Generate block-diagram from dot like text (basic feature).
* Multilingualization for node-label (utf-8 only).

You can get some examples and generated images on 
`blockdiag.com <http://blockdiag.com/blockdiag/build/html/index.html>`_ .

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
`blockdiag.com <http://blockdiag.com/blockdiag/build/html/index.html>`_ .

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
* Python Imaging Library 1.1.5 or later.
* funcparserlib 0.3.4 or later.
* setuptools or distribute.


License
=======
Apache License 2.0


History
=======

1.1.3 (2012-02-13)
------------------
* Add new edge type for data-models (thanks to David Lang)
* Add --no-transparency option
* Fix bugs

1.1.2 (2011-12-26)
------------------
* Support font-index for TrueType Font Collections (.ttc file)
* Allow to use reST syntax in descriptions of nodes
* Fix bugs

1.1.1 (2011-11-27)
------------------
* Add node attribute: href (thanks to @r_rudi!)
* Fix bugs

1.1.0 (2011-11-19)
------------------
* Add shape: square and circle
* Add fontfamily attribute for switching fontface
* Fix bugs

1.0.3 (2011-11-13)
------------------
* Add plugin: attributes
* Change plugin syntax; (cf. plugin attributes [attr = value, attr, value])
* Fix bugs

1.0.2 (2011-11-07)
------------------
* Fix bugs

1.0.1 (2011-11-06)
------------------
* Add group attribute: shape
* Fix bugs

1.0.0 (2011-11-04)
------------------
* Add node attribute: linecolor
* Rename diagram attributes:
   * fontsize -> default_fontsize
   * default_line_color -> default_linecolor
   * default_text_color -> default_textcolor
* Add docutils extention
* Fix bugs

0.9.7 (2011-11-01)
------------------
* Add node attribute: fontsize
* Add edge attributes: thick, fontsize
* Add group attribute: fontsize
* Change color of shadow in PDF mode
* Add class feature (experimental)
* Add handler-plugin framework (experimental)

0.9.6 (2011-10-22)
------------------
* node.style supports dashed_array format style
* Fix bugs

0.9.5 (2011-10-19)
------------------
* Add node attributes: width and height
* Fix bugs

0.9.4 (2011-10-07)
------------------
* Fix bugs

0.9.3 (2011-10-06)
------------------
* Replace SVG core by original's (simplesvg.py)
* Refactored
* Fix bugs

0.9.2 (2011-09-30)
------------------
* Add node attribute: textcolor
* Add group attribute: textcolor
* Add edge attribute: textcolor
* Add diagram attributes: default_text_attribute
* Fix beginpoint shape and endpoint shape were reversed
* Fix bugs

0.9.1 (2011-09-26)
------------------
* Add diagram attributes: default_node_color, default_group_color and default_line_color
* Fix bugs

0.9.0 (2011-09-25)
------------------
* Add icon attribute to node
* Make transparency to background of PNG images 
* Fix bugs

0.8.9 (2011-08-09)
------------------
* Fix bugs

0.8.8 (2011-08-08)
------------------
* Fix bugs

0.8.7 (2011-08-06)
------------------
* Fix bugs

0.8.6 (2011-08-01)
------------------
* Support Pillow as replacement of PIL (experimental)
* Fix bugs

0.8.5 (2011-07-31)
------------------
* Allow dot characters in node_id
* Fix bugs

0.8.4 (2011-07-05)
------------------
* Fix bugs

0.8.3 (2011-07-03)
------------------
* Support input from stdin
* Fix bugs

0.8.2 (2011-06-29)
------------------
* Add node.stacked
* Add node shapes: dots, none
* Add hiragino-font to font search list
* Support background image fetching from web
* Add diagram.edge_layout (experimental)
* Fix bugs

0.8.1 (2011-05-14)
------------------
* Change license to Apache License 2.0
* Fix bugs

0.8.0 (2011-05-04)
------------------
* Add --separate option and --version option
* Fix bugs

0.7.8 (2011-04-19)
------------------
* Update layout engine
* Update requirements: PIL >= 1.1.5
* Update parser for tokenize performance
* Add --nodoctype option
* Fix bugs
* Add many testcases

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

