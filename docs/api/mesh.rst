Mesh
----

Functions for working with CINEMA 4D's point and polygon objects.


.. function:: togglePolySelection(obj)
   
.. function:: selectAllPolys(obj)
   
.. function:: getSelectedPoints(obj)
   
   Returns list of selected point indices. 
   
   To get the actual point(s) do something like 
   
      .. code::
      
         allpoints = op.GetAllPoints()
         point = allpoints[index]
   
.. function:: getSelectedPolys(obj)

   Returns list of selected polygons indices. 
   
   To get the actual polygon(s) do something like 
   
      .. code::
      
         allpolys = obj.GetAllPolygons()
         poly = allpolys[index]
   
.. function:: polyToList(p)

.. function:: listToPoly(l)

.. function:: calcPolyCentroid(p, obj)
    
   Calculate the centroid of a polygon by averaging its vertices.

.. function:: calcPolyNormal(p, obj)

   Calculate the orientation of face normal by using Newell's method.
   
   See :py:func:`calcVertexNormal` for an example of usage within the calling context.

.. function:: calcVertexNormal(v, idx, obj)

   Calculate the vertex normal by averaging surrounding face normals.
   
   Usually called from a construct like the following:
   
      .. code::
      
         for i, point in enumerate(obj.GetAllPoints()):
            vn = calcVertexNormal(point, i, obj)

.. function:: calcThreePointNormal(v1, v2, v3)

   Calculate the surface normal of a three point plane.
   
   Doesn't take orientation of neighboring polygons into account.
   

   