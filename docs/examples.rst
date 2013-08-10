.. _py4dlib.examples:

Examples
--------

ShowPolygonNumber
~~~~~~~~~~~~~~~~~

Example script that shows how to get point and polygon selections 
and how to create objects and attach them to polygons in local and 
global coordinate systems.


PrintObjectHierarchy
~~~~~~~~~~~~~~~~~~~~

Example script that shows how to use the :py:class:`ObjectHierarchy` class.

.. _Extract:

Extract
~~~~~~~

Example plugin that extracts selected polygons across multiple objects 
into new polygon objects. 
 
Basically, the same as selecting polygons on some objects, 
running Split, then deleting the inverse selection to keep 
only the selected polys. Plus a few extras.

PlaneProjector
~~~~~~~~~~~~~~

Example plugin that shows how to project selected points along a direction vector 
onto a planar target.

Can snap any number of points onto planar targets along local or global X, Y, Z, a manual
direction or the averaged vertex normals (basically the direction of the modelling tool's
Normal setting for a group of selected points).

Currently needs a working plane or a plane object as target. You can create a new working
plane yourself and pick it up to be the target by pressing the pick target button (<) or
you can select any number of polygons on any number of polygon objects and hit one of the 
Create buttons to create a new plane or workplane aligned to the polygons.

Note: in R14 the workplane button aligns the workplane mode to the selection instead of 
creating a workplane object.

As a future improvement it shouldn't be hard at all to use polygons of other objects as
planar targets. 
