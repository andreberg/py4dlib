Maths
-----


.. class:: BBox
   
   Calculate various bounding box metrics from a list of points,
   such as min, max, midpoint, radius and size.
      
   .. classmethod:: FromObject(cls, obj, selOnly=False)
      
      Returns a new BBox object with all points from the passed object.
      
      :param bool selOnly: use selected points only instead of all points.
      
      :raise ValueError: if the object has no points.
      
   .. classmethod:: FromPointList(cls, lst)
      
      Returns a new BBox object with all points from a list added.
      
      Elements of lst must be of type ``c4d.Vector``.
      
      :raise ValueError: if the list is empty.
      
   .. classmethod:: FromPolygon(cls, poly, obj)
      
      Returns a new BBox object with all points from the passed polygon.

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

.. class:: Plane(pos, n)
   
   Represents a plane defined by positional offset and normal direction.
   
   .. function:: SetN(self, newN)
   
      Sets the normal of the plane to ``newN``.
      
   .. function:: SetPos(self, newPos)
      
      Sets the positional offset of the plane to ``newPos``.
      
   .. function:: SideAsString(self, d)
      
      Given distance ``d`` return a string indicating the residence
      of the point that correlates to the given distance.
      
      Used together with :py:func:`PointResidence`::
      
         SideAsString(PointResidence(self, p))
      
      :return: either ``front``, ``back`` or ``onplane``
   
   .. function:: PointResidence(self, p)
   
      Define the resident direction of a point with respect
      to the plane.
      
      The point can be either in front of the plane (+1), on the
      plane (0) or at the back of the plane (-1).


   .. function:: PointDistance(self, p, signed=True)
      
      Calculate distance from a point p to the plane.
      
      :param bool signed: set to True if you want the signed distance.
      
      A signed distance can be useful to determine if the point is located 
      in the half space from the backside of the plane or in the half space 
      on the front.
      
   .. function:: LineIntersection(self, p, d=None)
   
      Calculate intersection point with a line starting at position p
      and pointing in the direction d. 
              
      :param c4d.Vector d: direction of the line. If None, the normal 
         of the plane will be used instead.
          
      :return: ``c4d.Vector`` representing the intersection point, or 
         None if an intersection isn't possible (parallel directions).
      

.. function:: FloatEqual(a, b, places=8)

   Same as ``c4d.utils.FloatTolerantCompare`` just a shorter function name.

.. function:: MAbs(m)

   ``abs()`` each component vector of matrix m.
   
.. function:: VDeg(v, isHPB=False)

   Convert each component of vector v to degrees.
   
.. function::  VRad(v, isHPB=False)
   
   Convert each component of vector v to radians.

.. function:: VAvg(lv)

   Calculate the average of a list of vectors.
   
.. function:: VAbsMin(v)
   
   Return min component of a vector using ``abs(x) < abs(y)`` comparisons.

.. function:: VAbsMax(v)

   Return max component of a vector using ``abs(x) > abs(y)`` comparisons.
   
.. function:: VBoundaryLerp(lv, t=0.5)
   
   Interpolate linearily between a list of vectors, such that 
   the resulting vector points to the weighted midpoint in the
   vector space defined by the boundaries max X to min X and 
   max Y to min Y.

   :param float t: the weighting coefficient.

   :return: None if len(lst) is 0 or if the angle between 
      the two max/min vectors is greater than 180 degrees.

.. function:: VLerp(startv, endv, t=0.5)
   
   Linear interpolation between 2 vectors.
   
   Same as ``c4d.utils.VectorMix``.

.. function:: VNLerp(startv, endv, t=0.5)
   
   Normalized linear interpolation between 2 vectors.
   
.. function:: VSLerp(startv, endv, t=0.5)
   
   Spherical linear interpolation between 2 vectors.

.. function:: BuildMatrix(v, off=None, order="zyx")
   
   Builds a new orthonormal basis from a direction and (optionally) an offset vector using John F. Hughes and Thomas Möller's method.
   
   If ``off`` is None, off will default to a zero vector.

.. function:: BuildMatrix2(v, off=None, base="z")
   
   Builds a new orthonormal basis from a direction and (optionally) an offset vector using base aligned cross products.
   
   If ``off`` is None, off will default to a zero vector.
   
   :param str base: the base component 'v' represents. Must be one of ``x, y, z, -x, -y, -z``


.. function:: BuildMatrix3(v, v2, off=None, base="z")
   
   Builds a new orthonormal basis from 2 direction 
   and (optionally) an offset vector using cross products. 

   :param str base: the base component 'v' represents.
   
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

.. function:: ListToMatrix(lv)

   Convert a list of 3 or 4 ``c4d.Vector`` to ``c4d.Matrix``.
   
.. function:: ListListToMatrix(lli)

   Convert a ``list<list>`` structure, representing a list of list 
   of coordinate values to a ``c4d.Matrix``. 

   See :py:func:`MatrixToListList` to find out which list corresponds
   to which matrix component.

.. function:: MatrixToListList(m, inclOff=False)
   
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

.. function:: IsColinear(lv)

   Given a list of vectors check if they all share the same coordinates 
   in at least 2 dimensions. 
        
   :return: True if all the vectors in the list are co-linear.
  
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
