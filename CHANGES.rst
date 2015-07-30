Changelog
=========

1.5.3 (2015-07-30)
------------------
* Fix bug

  - Fix #67 Group overlaps with nodes having href

1.5.2 (2015-05-17)
------------------
* Fix dependency; webcolors-1.5 does not support py32
* Fix bug

  - Fix images.open() failed with PIL

1.5.1 (2015-02-21)
------------------
* Fix bug

  - Fix labels are overwrapped on antialias mode

1.5.0 (2015-01-01)
------------------
* Refactor cleanup procedures
* Fix bugs

  - Fix get_image_size() closes Image object automatically
  - Fix pasting Image object failed on SVG mode
  - Fix #61 images.urlopen() got PermissionError on Windows
  - Fix #61 images.open() raises exception if ghostscript not found
  - Fix #62 Use "sans-serif" to font-family property on SVG output ("sansserif" is invalid)
  - Fix #63 AttributeError on get_image_size(); Pillow (<= 2.4.x) does not have Image#close()

1.4.7 (2014-10-21)
------------------
* Fix bugs

  - Fix RuntimeError on unloading plugins

1.4.6 (2014-10-14)
------------------
* Show warnings on loading plugin multiple times
* Unload all plugins on shutdown
* Fix bugs

  - Fix caption is wrapped by paragraph node in reST parser

1.4.5 (2014-10-04)
------------------
* Add node event: build_finished
* Take config object to plugins
* Fix bugs

  - Fix utils.images.get_image_size() does not close an image descriptor

1.4.4 (2014-09-20)
------------------
* :caption: option of blockdiag directive recognizes inline markups
* Fix bugs

  - Fix #58 failed to handle diagram definitions from stdin in py3

1.4.3 (2014-07-30)
------------------
* Show warnings on loading imagedrawers in debug mode
* ImageDraw#image() accepts Image objects
* Fix bugs

  - PNG: could not load png imagedrawer if could not access PIL.PILLOW_VERSION

1.4.2 (2014-07-12)
------------------
* SVG: Adjust text alignment precisely
* Add plugin events: node.changing and cleanup
* ImageDraw#image() accepts image from IO objects
* Fix bugs

  - PDF: Fix failure text rotating
  - PDF: Fix failure pasting PNG images (256 palette/transparency)
  - PNG: Fix background of node was transparent on pasting transparent images

1.4.1 (2014-07-02)
------------------
* Change interface of docutils node (for sphinxcontrib module)
* Fix bugs

1.4.0 (2014-06-23)
------------------
* Support embedding SVG/EPS images as background
* Use wand to paste background images that is not supported by Pillow (if installed)
* Add options to blockdiag directive (docutils extension)

  - \:width:
  - \:height:
  - \:scale:
  - \:align:
  - \:name:
  - \:class:
  - \:figwidth:
  - \:figclass:

* actor shape supports label rendering

1.3.3 (2014-04-26)
------------------
* Add diagram attribute: default_node_style
* Fix bugs

1.3.2 (2013-11-19)
------------------
* Fix bugs

1.3.1 (2013-10-22)
------------------
* Fix bugs

1.3.0 (2013-10-05)
------------------
* Support python 3.2 and 3.3 (thanks to @masayuko)
* Drop supports for python 2.4 and 2.5
* Replace dependency: PIL -> Pillow

1.2.4 (2012-11-21)
------------------
* Fix bugs

1.2.3 (2012-11-05)
------------------
* Fix bugs

1.2.2 (2012-10-28)
------------------
* Fix bugs

1.2.1 (2012-10-28)
------------------
* Add external imagedraw plugin supports
* Add node attribute: label_orientation*
* Fix bugs

1.2.0 (2012-10-22)
------------------
* Optimize algorithm for rendering shadow
* Add options to docutils directive
* Fix bugs

1.1.8 (2012-09-28)
------------------
* Add --ignore-pil option
* Fix bugs

1.1.7 (2012-09-20)
------------------
* Add diagram attribute: shadow_style
* Add font path for centos 6.2
* Add a setting 'antialias' in the configuration file
* Fix bugs

1.1.6 (2012-06-06)
------------------
* Support for readthedocs.org
* reST directive supports :caption: option
* Fix bugs

1.1.5 (2012-04-22)
------------------
* Embed source code to SVG document as description
* Fix bugs

1.1.4 (2012-03-15)
------------------
* Add new edge.hstyles: oneone, onemany, manyone, manymany
* Add edge attribute: description (for build description-tables)
* Fix bugs

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
