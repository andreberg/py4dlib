Mesh
----

Functions for working with CINEMA 4D's point and polygon objects.


.. function:: TogglePolySelection(obj)
   
.. function:: SelectAllPolys(obj)
   
.. function:: GetSelectedPoints(obj)
   
   Returns list of selected point indices. 
   
   To get the actual point(s), using an ``index``
   from the returned list do something like
   
   .. code::
   
      allpoints = op.GetAllPoints()
      point = allpoints[index]
   
.. function:: GetSelectedPolys(obj)

   Returns list of selected polygons indices. 
   
   To get the actual polygon(s), using an ``index``
   from the returned list do something like 
   
   .. code::

      allpolys = obj.GetAllPolygons()
      poly = allpolys[index]

.. function:: CalcPolyCentroid(e, obj)
    
   Calculate the centroid of a polygon by averaging its vertices.
        
   :param e: can be ``c4d.CPolygon``, ``list<int>`` representing 
       point indices, or ``list<c4d.Vector>`` representing a list
       of points.
   
.. function:: CalcPolyNormal(e, obj)

   Calculate the orientation of face normal using Newell's method.
   
   See :py:func:`CalcVertexNormal` for an example of usage within the calling context.
      
   :param e: can be ``c4d.CPolygon``, ``list<int>`` representing 
       point indices, or ``list<c4d.Vector>`` representing a list
       of points.

.. function:: CalcVertexNormal(v, idx, obj)

   Calculate the vertex normal by averaging surrounding face normals.
   
   Usually called from a construct like the following:

   .. code::

      # calculate the average normal of a selected points
      vtx_normals = []

      for i, point in enumerate(obj.GetAllPoints()):
          if pointsel.IsSelected(i):
              vn = CalcVertexNormal(point, i, obj)
              vtx_normals.append(vn)

      N = VAvg(vtx_normals)
      
.. function:: CalcAverageVertexNormal(obj)

   Calculate the average normal of a selection of points. 

   This gives the same normal as setting the modelling tool 
   to "Normal" mode for an arbitrary point selection.

   :return: normal or zero vector if no points selected.

.. function:: CalcThreePointNormal(a, b, c)

   Calculate the surface normal of a three point plane.
   
   Doesn't take orientation of neighboring polygons into account.
   

.. function:: CalcTriangleArea(p, obj)

   Calculate area of a triangle using ``|(v3 - v1) x (v3 - v2)|/2``.
   
.. function:: CalcPolyArea(p, obj, normalized=False)

   Calculate the area of a planar polygon.
   

.. function:: CalcBBox(e, sel_only=False)

   Construct a :py:class:`BBox` for a ``c4d.PointObject`` or a ``c4d.CPolygon``. 

   Note that if you are interested in the midpoint or radius only, you can
   use the built-in ``c4d.BaseObject.GetMp()`` and ``GetRad()`` methods 
   respectively.
   
   :param bool sel_only: if True and ``e`` is a ``c4d.PointObject``, 
      use selected points only. Otherwise use all points.
   
.. function:: CalcGravityCenter(obj)

   Calculate the center of gravity for obj.
