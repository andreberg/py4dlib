Maths
-----


.. class:: BBox
   
   Calculate various bounding box metrics from a list of points,
   such as min, max, midpoint, radius and size.
      
   .. classmethod:: FromSelectedPoints(cls, obj)
      
      Returns a new BBox object with the 
      number of points currently selected 
      added, or None if there are no points 
      or obj doesn't exist.

      :raise ValueError: if the object has no points.
      
   .. classmethod:: FromPoints(cls, obj)
   
      Returns a new BBox object with all 
      points of obj added.
      
      :raise ValueError: if the object has no points.

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
   
.. function::  BuildMatrix(v, off=c4d.Vector(0), order="zyx")
   
   Builds a new orthonormal basis from a direction and (optionally) an offset vector using John F. Hughes and Thomas Möller's method.

.. function::  BuildMatrix2(v, off=c4d.Vector(0), base="z")
   
   Builds a new orthonormal basis from a direction and (optionally) an offset vector using base aligned cross products.
   
   :param base:  ``str`` the base component 'v' represents. Must be one of ``x, y, z, -x, -y, -z``

.. function:: GetMulP(m, v)
   
   Multiply a matrix with a vector representing a point.

.. function:: GetMulV(m, v)
   
   Multiply a matrix with a vector representing a direction.

.. function:: Det(m)

   Determinant of a ``n x n`` matrix where ``n = 3``. 
   m can be of type ``c4d.Matrix`` or ``list<list>``.
   
.. function:: PolyToList(p)

.. function:: PolyToListList(p, obj)
   
   Convert a ``c4d.CPolygon`` to a list of lists.
   
.. function:: ListToPoly(l)

.. function:: ListListToPoly(l)

   Convert a list of lists to ``c4d.CPolygon``.
   
.. function:: ListListToMatrix(l)

.. function:: MatrixToListList(m, includeOffset=False)

.. function:: UnitNormal(a, b, c)
   
   Calculate unit normal of a planar surface.
   
.. function:: IsPointInTriangle(p, a, b, c)
   
   Returns True if the point p is inside the triangle given by points a, b, and c.
   
.. function:: IsZeroVector(v)

   Uses float tolerant component comparison to check if v is a zero vector.
   
.. function:: LineLineDistance(p1a, p1b, p2a, p2b)
   
   Computes the smallest distance between two 3D lines. 

   :return: ``tuple`` of two ``c4d.Vectors`` 
      which are the points on each of the two input lines that, 
      when connected, form a segment which represents the shortest 
      distance between the two lines.
      
.. function:: WrapPi(theta)

   Wraps an angle theta in range ``-pi..pi`` by adding the correct multiple of 2 pi.
   
.. function:: SafeAcos(x)
   
   Same as ``math.acos(x)`` but if x is out of range, it is *clamped* to the 
   nearest valid value. The value returned is in range ``0..pi``, the same as 
   the standard `math.acos`_ function.


.. _math.acos: http://docs.python.org/2/library/math.html?highlight=math.acos#math.acos
