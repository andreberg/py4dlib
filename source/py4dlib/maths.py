# -*- coding: utf-8 -*-
# 
#  maths.py
#  py4dlib
#  
#  Created by André Berg on 2013-07-29.
#  Copyright 2013 Berg Media. All rights reserved.
#
#  andre.bergmedia@googlemail.com
# 
# pylint: disable-msg=F0401

'''py4dlib.maths -- linalg etc. functions'''

import os
import sys
import math

__version__ = (0, 3)
__date__ = '2013-07-29'
__updated__ = '2013-08-02'


DEBUG = 0 or ('DebugLevel' in os.environ and os.environ['DebugLevel'] > 0)
TESTRUN = 0 or ('TestRunLevel' in os.environ and os.environ['TestRunLevel'] > 0)


try:
    import c4d  #@UnresolvedImport
    from c4d.utils import Rad, Deg
except ImportError:
    if TESTRUN == 1:
        pass


class BBox(object):
    """
    Calculate various bounding box metrics from a list of points, 
    such as min, max, midpoint, radius and size.
    """
    def __init__(self):
        super(BBox, self).__init__()
        FLOATMIN = sys.float_info[3]-1000 # workaround for underflow error
        FLOATMAX = sys.float_info[0]
        self.min = c4d.Vector(FLOATMAX, FLOATMAX, FLOATMAX)
        self.max = c4d.Vector(FLOATMIN, FLOATMIN, FLOATMIN)
        self.np = 0
    
    def __getattr__(self, attr, *args, **kwargs):
        if attr == 'max':
            return self.GetMax()
        elif attr == 'min':
            return self.GetMin()
        elif attr == 'midpoint':
            return self.GetMp()
        elif attr == 'radius':
            return self.GetRad()
        elif attr == 'size':
            return self.GetSize()
        else:
            return super(BBox, self).__getattribute__(attr, *args, **kwargs)
    
    def __str__(self):
        return ("%r\n  size = %s\n  mp = %s\n  min = %s\n  max = %s" % 
                (self, self.size, self.midpoint, self.min, self.max))
    
    def AddPoint(self, p):
        """ Add metrics from point p. """
        if p.x < self.min.x: self.min.x = p.x
        if p.x > self.max.x: self.max.x = p.x
        if p.y < self.min.y: self.min.y = p.y
        if p.y > self.max.y: self.max.y = p.y
        if p.z < self.min.z: self.min.z = p.z
        if p.z > self.max.z: self.max.z = p.z
    
    def AddPoints(self, lst):
        """ Add metrics from a list of points. """
        for p in lst:
            self.addPoint(p)
    
    @classmethod
    def FromSelectedPoints(cls, obj):
        """
        Returns a new BBox object with the 
        number of points currently selected 
        added, or None if there are no points 
        or obj doesn't exist.
        
        :raise ValueError: if the object has no points.
        """
        if not isinstance(obj, c4d.PointObject): 
            raise TypeError("E: expected c4d.PointObject, got %s" % type(obj))
        allpnts = obj.GetAllPoints()
        if len(allpnts) == 0: 
            raise ValueError("E: object has no points")
        pntsel = obj.GetPointS()
        n = 0
        bb = BBox()
        if pntsel.HostAlive():
            for i, p in enumerate(allpnts):  # IGNORE:W0612 @UnusedVariable
                if pntsel.IsSelected(i):
                    bb.AddPoint(obj.GetPoint(i))
                    n += 1
        else:
            return None
        bb.np = n
        return bb
    
    @classmethod
    def FromPoints(cls, obj):
        """
        Returns a new BBox object with all 
        points of obj added.
        
        :raise ValueError: if the object has no points.
        """
        if not isinstance(obj, c4d.PointObject): 
            raise TypeError("E: expected c4d.PointObject, got %s" % type(obj))
        allpnts = obj.GetAllPoints()
        if len(allpnts) == 0: 
            raise ValueError("E: object has no points")
        n = 0
        bb = BBox()
        for i, p in enumerate(allpnts):  # IGNORE:W0612 @UnusedVariable
            bb.AddPoint(obj.GetPoint(i))
            n += 1
        bb.np = n
        return bb

    def GetMax(self):
        """ Return max bounds vector. """
        return self.max
    
    def GetMin(self):
        """ Return min bounds vector. """
        return self.min
    
    def GetMp(self):
        """ Return midpoint vector. """
        return (self.min + self.max) * 0.5
    
    def GetRad(self):
        """ Return radius vector. """
        return (self.max - self.min) * 0.5
    
    def GetSize(self):
        """ Return size vector. """
        return self.max - self.min


def VDeg(v, isHPB=False):
    """ Convert each component of vector v to degrees. """
    if v is None:
        raise ValueError("E: v can't be None")
    if not isinstance(v, c4d.Vector): 
        raise TypeError("E: expected c4d.Vector, got %s" % type(v))
    if isHPB:
        res = c4d.Vector(0,0,0)
        res.x = Deg(v.x)
        res.y = Deg(v.y)
        res.z = Deg(v.z)
        if res.x >= 180:
            res.x -= 360
        if res.y >= 180:
            res.y -= 360
        if res.z >= 180:
            res.z -= 360
        return res
    else:
        return c4d.Vector(Deg(v.x), Deg(v.y), Deg(v.z))


def VRad(v, isHPB=False):
    """ Convert each component of vector v to radians. """
    if v is None:
        raise ValueError("E: v can't be None")
    if not isinstance(v, c4d.Vector): 
        raise TypeError("E: expected c4d.Vector, got %s" % type(v))
    if isHPB:
        if v.x >= 180:
            v.x -= 360
        if v.y >= 180:
            v.y -= 360
        if v.z >= 180:
            v.z -= 360
    return c4d.Vector(Rad(v.x), Rad(v.y), Rad(v.z))


def VAvg(lst):
    """ Calculate the average of a list of vectors. """
    if lst is None:
        raise ValueError("E: lst can't be None")
    if not isinstance(lst, list): 
        raise TypeError("E: expected list of c4d.Vectors, got %s" % type(lst))
    lstlen = len(lst)
    res = c4d.Vector(0,0,0)
    if lstlen == 0: return res
    for l in lst:
        res.x += l.x
        res.y += l.y
        res.z += l.z
    res.x = res.x / float(lstlen)
    res.y = res.y / float(lstlen)
    res.z = res.z / float(lstlen)
    return res


def VAbsMin(v):
    """ Return min component of a vector using abs(x) < abs(y) comparisons. """
    if v is None:
        raise ValueError("E: v can't be None")
    if not isinstance(v, c4d.Vector): 
        raise TypeError("E: expected c4d.Vector, got %s" % type(v))
    result = v.x
    if abs(v.y) < abs(v.x):
        result = v.y
    elif abs(v.z) < abs(v.x):
        result = v.z
    return result


def MAbs(m):
    """ ``abs()`` each component vector of matrix m. """
    return c4d.Matrix(abs(m.off), abs(m.v1), abs(m.v2), abs(m.v3))


def BuildMatrix(v, off=c4d.Vector(0), order="zyx"):
    """ Builds a new orthonormal basis from a direction 
        and (optionally) an offset vector using John F. 
        Hughes and Thomas Möller's method.
    """
    if v is None or not isinstance(v, c4d.Vector):
        raise ValueError("E: expected c4d.Vector, but got %r" % v)
    r = v.GetNormalized()
    mincomp = c4d.utils.VectorMin(v)
    if r.x == mincomp:
        s = c4d.Vector(0, -r.z, r.y)
    elif r.y == mincomp:
        s = c4d.Vector(-r.z, 0, r.x)
    else:
        s = c4d.Vector(-r.y, r.x, 0)
    s = s.GetNormalized()
    t = r.Cross(s)
    t = t.GetNormalized()
    if order == "xyz":
        return c4d.Matrix(off, r, s, t)
    elif order == "xzy":
        return c4d.Matrix(off, r, t, s)
    elif order == "yxz":
        return c4d.Matrix(off, s, r, t)        
    elif order == "yzx":
        return c4d.Matrix(off, s, t, r)        
    elif order == "zxy":
        return c4d.Matrix(off, t, r, s)        
    elif order == "zyx":
        return c4d.Matrix(off, t, s, r)
    else:
        return c4d.Matrix(off, r, s, t)


def BuildMatrix2(v, off=c4d.Vector(0), base="z"):
    """ Builds a new orthonormal basis from a direction 
        and (optionally) an offset vector using base 
        aligned cross products. 
        
        :param base:  ``str`` the base component 'v' represents.
    """
    if v is None or not isinstance(v, c4d.Vector):
        raise ValueError("E: expected c4d.Vector, but got %r" % v)
    if base == "z":
        z = v.GetNormalized()
        x = z.Cross(c4d.Vector(1, 0, 0)).GetNormalized()
        y = x.Cross(z).GetNormalized()
    elif base == "y":
        y = v.GetNormalized()
        z = y.Cross(c4d.Vector(0, 0, 1)).GetNormalized()
        x = z.Cross(y).GetNormalized()
    elif base == "x":
        x = v.GetNormalized()
        y = x.Cross(c4d.Vector(0, 1, 0)).GetNormalized()
        z = y.Cross(x).GetNormalized()
    elif base == "-z":
        z = v.GetNormalized()
        x = z.Cross(c4d.Vector(-1, 0, 0)).GetNormalized()
        y = x.Cross(z).GetNormalized()
    elif base == "-y":
        y = v.GetNormalized()
        z = y.Cross(c4d.Vector(0, 0, -1)).GetNormalized()
        x = z.Cross(y).GetNormalized()
    elif base == "-x":
        x = v.GetNormalized()
        y = x.Cross(c4d.Vector(0, -1, 0)).GetNormalized()
        z = y.Cross(x).GetNormalized()
    else:
        raise ValueError("E: base must be one of x, y, z, -x, -y, -z, but is %r" % base)
    return c4d.Matrix(off, x, y, z)


# Define these functions to ease conversion of C.O.F.F.E.E. scripts to Python.
def GetMulP(m, v):
    """ Multiply a matrix with a vector representing a point. """
    return v * m


def GetMulV(m, v):
    """ Multiply a matrix with a vector representing a direction. """
    return v ^ m


def Det(m):
    """ Determinant of a ``n x n`` matrix where ``n = 3``. 
        m can be of type ``c4d.Matrix`` or ``list<list>``.
    """
    if isinstance(m, list):
        return (m[0][0] * m[1][1] * m[2][2] +
                m[0][1] * m[1][2] * m[2][0] + 
                m[0][2] * m[1][0] * m[2][1] - 
                m[0][2] * m[1][1] * m[2][0] - 
                m[0][1] * m[1][0] * m[2][2] - 
                m[0][0] * m[1][2] * m[2][1])
    return (m.v1.x * m.v2.y * m.v3.z + 
            m.v1.y * m.v2.z * m.v3.x + 
            m.v1.z * m.v2.x * m.v3.y - 
            m.v1.z * m.v2.y * m.v3.x - 
            m.v1.y * m.v2.x * m.v3.z - 
            m.v1.x * m.v2.z * m.v3.y)


def PolyToList(p):
    if not isinstance(p, c4d.CPolygon):
        raise TypeError("E: expected c4d.CPolygon, but got %r" % type(p))
    if p.c == p.d: return [p.a,p.b,p.c]
    return [p.a,p.b,p.c,p.d]


def PolyToListList(p, obj):
    """ Convert a ``c4d.CPolygon`` to a ``list<list>`` structure. 
    
    ``list<list>`` represents a list of points comprised of a 
    list of coordinate values.
    """
    if not isinstance(p, c4d.CPolygon):
        raise TypeError("E: expected c4d.CPolygon, but got %r" % type(p))
    if not isinstance(obj, c4d.PointObject):
        raise TypeError("E: expected c4d.PointObject, but got %r" % type(obj))
    allp = obj.GetAllPoints()
    a = allp[p.a]
    b = allp[p.b]
    c = allp[p.c]
    if p.c == p.d: 
        return [[a.x, a.y, a.z], 
                [b.x, b.y, b.z],
                [c.x, c.y, c.z]]
    d = allp[p.d]
    return [[a.x, a.y, a.z], 
            [b.x, b.y, b.z],
            [c.x, c.y, c.z],
            [d.x, d.y, d.z]]


def ListToPoly(l):
    if not isinstance(l, list): 
        raise TypeError("E: expected list, but got %r" % type(l))
    for i, e in enumerate(l):
        if not isinstance(e, c4d.Vector):
            raise TypeError("E: element %d of l should be of type c4d.Vector, but is %r" % (i, type(e)))
    ln = len(l)
    if ln < 3:
        raise IndexError("list must have at least 3 indices")
    elif ln == 3:
        return c4d.CPolygon(l[0],l[1],l[2])
    else:
        return c4d.CPolygon(l[0],l[1],l[2],l[3])


def ListListToPoly(l):
    """ Convert a ``list<list>`` structure to ``c4d.CPolygon``. 
    
    ``list<list>`` represents a list of points comprised of a 
    list of coordinate values.
    """
    if not isinstance(l, list): 
        raise TypeError("E: expected list, but got %r" % type(l))
    ln = len(l)
    if ln < 3:
        raise IndexError("E: list must have at least 3 indices")
    elif ln == 3:
        return c4d.CPolygon(c4d.Vector(l[0][0], l[0][1], l[0][2]),
                            c4d.Vector(l[1][0], l[1][1], l[1][2]),
                            c4d.Vector(l[2][0], l[2][1], l[2][2]))
    else:
        return c4d.CPolygon(c4d.Vector(l[0][0], l[0][1], l[0][2]),
                            c4d.Vector(l[1][0], l[1][1], l[1][2]),
                            c4d.Vector(l[2][0], l[2][1], l[2][2]),
                            c4d.Vector(l[3][0], l[3][1], l[3][2]))


def ListListToMatrix(l):
    if not isinstance(l, list):
        raise TypeError("E: expected list of list, but got %r" % type(l))
    n = len(l)
    for i in xrange(n):
        m = len(l[i])
        if m != 3:
            raise ValueError("E: wrong dimensions. m must equal 3, but m = %d" % (m))
    if n != 4:
        raise ValueError("E: need affine matrix. n must equal 4, but n = %d" % (n))
    return c4d.Matrix(c4d.Vector(l[0][0], l[0][1], l[0][2]), 
                      c4d.Vector(l[1][0], l[1][1], l[1][2]),
                      c4d.Vector(l[2][0], l[2][1], l[2][2]),
                      c4d.Vector(l[3][0], l[3][1], l[3][2]))


def MatrixToListList(m, includeOffset=False):
    if not isinstance(m, c4d.Matrix):
        raise TypeError("E: expected c4d.Matrix, but got %r" % type(m))
    if includeOffset is True:
        return [[m.off.x, m.off.y, m.off.z], 
                [m.v1.x, m.v1.y, m.v1.z],
                [m.v2.x, m.v2.y, m.v2.z],
                [m.v3.x, m.v3.y, m.v3.z]]
    else:
        return [[m.v1.x, m.v1.y, m.v1.z],
                [m.v2.x, m.v2.y, m.v2.z],
                [m.v3.x, m.v3.y, m.v3.z]]


def UnitNormal(a, b, c):
    """ Calculate unit normal of a planar tri-facet. """
    x = Det([[1, a.y, a.z],
             [1, b.y, b.z],
             [1, c.y, c.z]])
    y = Det([[a.x, 1, a.z],
             [b.x, 1, b.z],
             [c.x, 1, c.z]])
    z = Det([[a.x, a.y, 1],
             [b.x, b.y, 1],
             [c.x, c.y, 1]])
    magnitude = (x ** 2 + y ** 2 + z ** 2) ** .5
    return c4d.Vector(x / magnitude, y / magnitude, z / magnitude).GetNormalized()


def IsPointInTriangle(p, a, b, c):
    """ Returns True if the point p is inside the triangle given by points a, b, and c. """
    if not isinstance(p, c4d.Vector):
        raise TypeError("E: expected c4d.Vector, got %r" % type(p))
    ood = (1.0 / (((a.y - c.y) * (b.x - c.x)) + 
                  ((b.y - c.y) * (c.x - a.x))))
    b1 = (ood * (((p.y - c.y) * (b.x - c.x)) + 
                 ((b.y - c.y) * (c.x - p.x))))
    b2 = (ood * (((p.y - a.y) * (c.x - a.x)) + 
                 ((c.y - a.y) * (a.x - p.x))))
    b3 = (ood * (((p.y - b.y) * (a.x - b.x)) + 
                 ((a.y - b.y) * (b.x - p.x))))
    return ((b1 > 0) and (b2 > 0) and (b3 > 0))   


# def isPointInTriangle2(p, t):
#     if not isinstance(p, c4d.Vector):
#         raise TypeError("E: expected c4d.Vector, got %r" % type(p))
#     if not isinstance(t, c4d.CPolygon):
#         raise TypeError("E: expected c4d.CPolygon, got %r" % type(p))
#     if not t.c == t.d:
#         raise ValueError("E: expected triangle, satisfying t.c == t.d")
#     return isPointInTriangle(p, t.a, t.b, t.c)


def IsZeroVector(v):
    """ Uses float tolerant component comparison to check if v is a zero vector. """
    return c4d.utils.VectorEqual(c4d.Vector(0), v)


def LineLineDistance(p1a, p1b, p2a, p2b):
    """ Computes the smallest distance between two 3D lines. 
    
    :return: ``tuple`` of two c4d.Vectors 
        which are the points on each of the two input lines that, 
        when connected, form a segment which represents the shortest 
        distance between the two lines.
    """
    
    res = (c4d.Vector(0.5 * (p1a.x + p1b.x), 
                      0.5 * (p1a.y + p1b.y), 
                      0.5 * (p1a.z + p1b.z)),
           c4d.Vector(0.5 * (p2a.x + p2b.x), 
                      0.5 * (p2a.y + p2b.y), 
                      0.5 * (p2a.z + p2b.z)))
    
    p43_x = p2b.x - p2a.x
    p43_y = p2b.y - p2a.y
    p43_z = p2b.z - p2a.z

    if (IsZeroVector(p43_x) and 
        IsZeroVector(p43_y) and 
        IsZeroVector(p43_z)):
        return res

    p21_x = p1b.x - p1a.x
    p21_y = p1b.y - p1a.y
    p21_z = p1b.z - p1a.z

    if (IsZeroVector(p21_x) and 
        IsZeroVector(p21_y) and 
        IsZeroVector(p21_z)):
        return res

    p13_x = p1a.x - p2a.x
    p13_y = p1a.y - p2a.y
    p13_z = p1a.z - p2a.z

    d1343 = p13_x * p43_x + p13_y * p43_y + p13_z * p43_z
    d4321 = p43_x * p21_x + p43_y * p21_y + p43_z * p21_z
    d1321 = p13_x * p21_x + p13_y * p21_y + p13_z * p21_z
    d4343 = p43_x * p43_x + p43_y * p43_y + p43_z * p43_z
    d2121 = p21_x * p21_x + p21_y * p21_y + p21_z * p21_z

    denom = d2121 * d4343 - d4321 * d4321

    if IsZeroVector(denom):
        return res

    mua = (d1343 * d4321 - d1321 * d4343) / denom
    mub = (d1343 + d4321 * mua) / d4343

    return (c4d.Vector(p1a.x + mua * p21_x, 
                       p1a.y + mua * p21_y, 
                       p1a.z + mua * p21_z),
            c4d.Vector(p2a.x + mub * p43_x, 
                       p2a.y + mub * p43_y, 
                       p2a.z + mub * p43_z))


# These functions are from 3D Math Primer for Graphics And Game Development
# courtesy of Fletcher Dunn and Ian Parberry.

def WrapPi(theta):
    """ Wraps an angle theta in range -pi...pi by adding the correct multiple of 2 pi. """
    twoPi = 2.0 * math.pi
    oneOver2Pi = 1.0 / twoPi
    theta += math.pi
    theta -= math.floor(theta * oneOver2Pi) * twoPi
    theta -= math.pi
    return theta


def SafeAcos(x):
    """ Same as ``math.acos(x)`` but if x is out of range, it is "clamped" to the 
        nearest valid value. The value returned is in range 0...pi, the same as 
        the standard `math.acos`_ function. 
    """
    # Check limit conditions
    if x <= -1.0:
        return math.pi
    if x >= 1.0:
        return 0.0
    # Value is in the domain - use standard acos function
    return math.acos(x)


#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
# 
#       http://www.apache.org/licenses/LICENSE-2.0
# 
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
