Mesh
----

Functions for working with CINEMA 4D's point and polygon objects.


.. function:: TogglePolySelection(obj)
   
.. function:: SelectAllPolys(obj)

.. function:: SelectPolys(li, obj, clearOldSel=True)
   
   Switch the selection state to 'selected' for a list of polygons. 
   Expects a list of polygon indices.

   If ``clearOldSel`` is True, clears the old polygon selection.
   Otherwise appends to the current selection. Default is True.

   :return: True if the selection state was changed, or False if 
      obj is not a ``c4d.PolygonObject``.
      
.. function:: SelectPoints(li, obj, clearOldSel=True)

   Switch the selection state to 'selected' for a list of points. 
   Expects a list of point indices.

   If ``clearOldSel`` is True, clears the old polygon selection.
   Otherwise appends to the current selection. Default is True.

   :return: True if the selection state was changed, or False if 
      obj is not a ``c4d.PointObject``.
   
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

.. function:: GetPointsForIndices(li, obj)

   Return a list with the actual points from a list of point indices.

   If ``li`` already is of type ``list<c4d.Vector>`` return the list untouched.
   
.. function:: GetPolysForIndices(li, obj)

   Return a list with the actual polygons from a list of polygon indices.

   If ``li`` already is of type ``list<c4d.CPolygon>`` return the list untouched.

.. function:: GetIndicesForPoints(lp, obj)

   Return a list of point indices for all points that are equal 
   to the vectors from lp.

   Warning: can be time consuming for large models, since this 
   has to check against all points each time for every element 
   in lp. 

   You are better off acquiring the list of indices another way. 
   Especially if it is just about converting a list of selected 
   points to their indices. 

   Use :py:func:`GetSelectedPoints` in that case.

   If ``lp`` already is of type ``list<int>`` return the list untouched.
   
.. function:: GetPolysForPoints(li, obj, strict=True, threshold=3)

   Returns a list of polygon indices for all polygons that have 
   points with point indices given by ``li`` as their members. 

   This is the same as converting between selections by holding
   Cmd/Ctrl when pressing the modelling mode buttons in CINEMA 4D.

   :param bool strict: if True, return only those polygons
      that are fully enclosed by all the points that make 
      up that polygon.

   :param int threshold: minimum number of points that must be
       shared to for strict mode to be considered as enclosing
       a polygon. 3 includes triangles, 4 would only include
       quads.

   If ``li`` already is of type ``list<c4d.CPolygon>`` return the 
   list untouched.

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

      # calculate average vertex normal for point selection
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

   :return: normal, or zero vector if no points selected.

.. function:: CalcThreePointNormal(a, b, c)

   Calculate the surface normal of a three point plane.
   
   Doesn't take orientation of neighboring polygons into account.
   
.. function:: CalcTriangleArea(p, obj)

   Calculate area of a triangle using ``|(v3 - v1) x (v3 - v2)|/2``.
   
.. function:: CalcPolyArea(p, obj, normalized=False)

   Calculate the area of a planar polygon.
   
.. function:: CalcBBox(e, selOnly=False, obj=None)

   Construct a :py:class:`BBox` for a ``c4d.PointObject``, a ``c4d.CPolygon``,
   or a list of polygon indices. If you have a list of point indices you can
   construct a BBox directly using the :py:func:`FromPointList` class method.

   You must supply the object the polygon list belongs to in the latter case.

   Note that if you are interested in the midpoint or radius only, you can
   use the built-in ``c4d.BaseObject.GetMp()`` and ``GetRad()`` methods 
   respectively.

   :param bool selOnly:  if True, use selected points 
      only if e is a ``c4d.PointObject``. Otherwise use 
      all points of the object.
   
.. function:: CalcGravityCenter(obj)

   Calculate the center of gravity for obj.
   
.. function:: PolyToList(p)

   Convert a ``c4d.CPolygon`` to a ``list`` of ``c4d.Vectors``, representing the points of the polygon.

.. function:: PolyToListList(p, obj)

   Convert a ``c4d.CPolygon`` to a ``list<list>`` structure. 

   ``list<list>`` represents a list of points comprised of a list of coordinate values.

.. function:: ListToPoly(li)

   Convert a ``list`` of ``int`` representing indices into an object's point list to a ``c4d.CPolygon``.

.. function:: ListListToPoly(lli)

   Convert a ``list<list>`` structure to ``c4d.CPolygon``. 

   ``list<list>`` represents a list of indices that indentify points of an object.

