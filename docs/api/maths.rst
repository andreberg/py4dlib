Maths
-----


.. class:: BBox
   
   Calculate various bounding box metrics from a list of points,
   such as min, max, midpoint, radius and size.
      
   .. classmethod:: FromObject(cls, obj, sel_only=False)
      
      Returns a new BBox object with all 
      points from the passed object.
      
      :param bool sel_only: use selected points only instead of all points.
      
      :raise ValueError: if the object has no points.
      
   .. classmethod:: FromPointList(cls, lst)
      
      Returns a new BBox object with all 
      points from a list added.
      
      Elements of lst must be of type ``c4d.Vector``.
      
      :raise ValueError: if the list is empty.

   .. function:: AddPoint(p)
      
      Add metrics from point p.

   .. function:: AddPoints(lst)
      
      Add metrics from a list of points.
            
   .. function:: GetMax()
      
      Return max bounds vector.
   
   .. function:: GetMin()
      
      Return min bounds vector.

   .. function:: GetMp()
   
      Return midpoint vector.

   .. function:: GetRad()
   
      Return radius vector.

   .. function:: GetSize()
   
      Return size vector.

      
.. function:: MAbs(m)

   ``abs()`` each component vector of matrix m.
   
.. function:: VDeg(v, isHPB=False)

   Convert each component of vector v to degrees.
   
.. function::  VRad(v, isHPB=False)
   
   Convert each component of vector v to radians.

.. function:: VAvg(lst)

   Calculate the average of a list of vectors.
   
.. function:: VAbsMin(v)
   
   Return min component of a vector using ``abs(x) < abs(y)`` comparisons.
   
.. function:: BuildMatrix(v, off=None, order="zyx")
   
   Builds a new orthonormal basis from a direction and (optionally) an offset vector using John F. Hughes and Thomas Möller's method.
   
   If ``off`` is None, off will default to a zero vector.

.. function:: BuildMatrix2(v, off=None, base="z")
   
   Builds a new orthonormal basis from a direction and (optionally) an offset vector using base aligned cross products.
   
   If ``off`` is None, off will default to a zero vector.
   
   :param str base: the base component 'v' represents. Must be one of ``x, y, z, -x, -y, -z``

.. function:: GetMulP(m, v)
   
   Multiply a matrix with a vector representing a point. 
   
   Same as ``c4d.Matrix.Mul(v)``.

.. function:: GetMulV(m, v)
   
   Multiply a matrix with a vector representing a direction. 
   
   Same as ``c4d.Matrix.MulV(v)``

.. function:: Det(m)

   Determinant of an ``n x n`` matrix.

   m can be of type ``c4d.Matrix`` when ``n = 3`` 
   or ``list<list>`` when ``n = 3`` or ``n = 4`` .

.. function:: Transpose(e)
   
   Transpose matrix e in row-major format to column-major.
   
   ``e`` can be of type ``list<list>`` structure or ``c4d.Matrix``.

.. function:: PolyToList(p)

.. function:: PolyToListList(p, obj)
   
   Convert a ``c4d.CPolygon`` to a ``list<list>`` structure. 

   ``list<list>`` represents a list of points comprised of a list of coordinate values.
   
.. function:: ListToPoly(l)

.. function:: ListListToPoly(l)
   
   Convert a list of lists to ``c4d.CPolygon``.
   
   ``list<list>`` represents a list of points comprised of a list of coordinate values.
   
.. function:: ListListToMatrix(l)

.. function:: MatrixToListList(m, incl_off=False)
   
   Convert a ``c4d.Matrix`` to a ``list<list>`` structure. 
   
   The structure layout is generally in row-major format, 
   and the ordering the same as the order required for 
   constructing a ``c4d.Matrix`` by hand:

   .. code::
   
      [[off.x, off.y, off.z],
       [v1.x,   v1.y,  v1.z], 
       [v2.x,   v2.y,  v2.z],
       [v3.x,   v3.y,  v3.z]]
   
.. function:: UnitNormal(a, b, c)
   
   Calculate unit normal of a planar surface.
   
   :raise ValueError: if magnitude <= 0.0
   
.. function:: IsPointInTriangle(p, a, b, c)
   
   Returns True if the point p is inside the triangle given by points a, b, and c.
   
.. function:: IsZeroVector(v)

   Uses float tolerant component comparison to check if v is a zero vector.
   
.. function:: LineLineDistance(p1a, p1b, p2a, p2b)
   
   Computes the smallest distance between two 3D lines. 

   :return: ``tuple`` of two ``c4d.Vectors`` which are the points on each of the 
      two input lines that, when connected, form a segment which represents the 
      shortest distance between the two lines.
      
.. function:: WrapPi(theta)

   Wraps an angle theta in range ``-pi..pi`` by adding the correct multiple of 2 pi.
   
.. function:: SafeAcos(x)
   
   Same as ``math.acos(x)`` but if x is out of range, it is *clamped* to the 
   nearest valid value. The value returned is in range ``0..pi``, the same as 
   the standard `math.acos`_ function.


.. _math.acos: http://docs.python.org/2/library/math.html?highlight=math.acos#math.acos
