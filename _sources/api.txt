API docs
--------

A word about the style of the API. I tried to mirror the format and style
used by the original Py4D SDK so using methods from **py4dlib** should 
hopefully feel familiar.

Concerning function/method paramaters, I also try to avoid ambiguity by using
the same argument names for the same type of data. 

This is especially apparent for functions that expect points or polygons. 
I usually try set the functions up in a general way, so that you don't have to 
remember that you have to call the version of the function that expects a list 
of point indices instead of a list of points (``c4d.Vector``, to be exact). 

A polymorphic nature like that is usually indicated by using the parameter name ``e``
(for *element* or *entity*) whenever you can pass either. 

In all other cases it should be apparent if you need to pass a point, a list of 
points, a list of point indices, an object, a matrix, vector or whatever else have you.

Here's an overview of some of the default parameter names and their meaning:

+---------+---------------------------------------------------------------------------+
| e       | the ``any`` value. stands for *element*. Refer to the function docs what  |
|         | any means in the function's context.                                      |
+---------+---------------------------------------------------------------------------+
| obj     | any descendant of ``c4d.BaseObject`` incl. ``c4d.PointObject`` + children |
+---------+---------------------------------------------------------------------------+
| m       | ``c4d.Matrix``                                                            |
+---------+---------------------------------------------------------------------------+
| v       | ``c4d.Vector``                                                            |
+---------+---------------------------------------------------------------------------+
| p       | ``c4d.Vector`` representing a point, or a polygon as ``c4d.CPolygon``     |
+---------+---------------------------------------------------------------------------+
| l       | ``list``                                                                  |
+---------+---------------------------------------------------------------------------+
| li      | ``list`` of ``int``, which usually represents indices into an object's    |
|         | point list                                                                |
+---------+---------------------------------------------------------------------------+
| lv      | ``list`` of vectors                                                       |
+---------+---------------------------------------------------------------------------+
| lp      | ``list`` of points                                                        |
+---------+---------------------------------------------------------------------------+
| lli     | ``list`` of ``list`` of ``int``                                           |
+---------+---------------------------------------------------------------------------+
| llf     | ``list`` of ``list`` of ``float``                                         |
+---------+---------------------------------------------------------------------------+
| x, n, w | ``float`` sometimes can be called other traditional names, like *theta*   |
| ...     | if for example an angle is represented (w for greek omega, n for number)  |
+---------+---------------------------------------------------------------------------+
| a, b, c | a name series usually represents a series of vectors.                     |
| ...     |                                                                           |
+---------+---------------------------------------------------------------------------+

Contents:

.. toctree:: 
   
	api/maths
	api/mesh
	api/objects
	api/plugins
	api/utils
   