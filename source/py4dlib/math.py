# -*- coding: utf-8 -*-
# 
#  math.py
#  py4dlib
#  
#  Created by André Berg on 2013-07-29.
#  Copyright 2013 Berg Media. All rights reserved.
#
#  andre.bergmedia@googlemail.com
# 
# pylint: disable-msg=F0401

'''py4dlib.math -- linalg etc. functions'''

import os
import sys

__version__ = (0, 2)
__date__ = '2013-07-29'
__updated__ = '2013-07-31'


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
    Calculate various area metrics from a list of points,
    such as min, max, midpoint, radius and size.
    """
    def __init__(self):
        super(BBox, self).__init__()
        FLOATMIN = sys.float_info[3]-1000 # workaround for underflow error
        FLOATMAX = sys.float_info[0]
        self.min = c4d.Vector(FLOATMAX, FLOATMAX, FLOATMAX)
        self.max = c4d.Vector(FLOATMIN, FLOATMIN, FLOATMIN)
    
    def __getattr__(self, attr, *args, **kwargs):
        if attr == 'max':
            return self.getMax()
        elif attr == 'min':
            return self.getMin()
        elif attr == 'midpoint':
            return self.getMp()
        elif attr == 'radius':
            return self.getRad()
        elif attr == 'size':
            return self.getSize()
        else:
            return super(BBox, self).__getattribute__(attr, *args, **kwargs)
    
    def __str__(self):
        return ("%r\n  size = %s\n  mp = %s\n  min = %s\n  max = %s" % 
                (self, self.getSize(), self.getMp(), self.min, self.max))
    
    def addPoint(self, p):
        if p.x < self.min.x: self.min.x = p.x
        if p.x > self.max.x: self.max.x = p.x
        if p.y < self.min.y: self.min.y = p.y
        if p.y > self.max.y: self.max.y = p.y
        if p.z < self.min.z: self.min.z = p.z
        if p.z > self.max.z: self.max.z = p.z
    
    def addPoints(self, lst):
        for p in lst:
            self.addPoint(p)
    
    @classmethod
    def fromSelectedPoints(cls, obj):
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
                    bb.addPoint(obj.GetPoint(i))
                    n += 1
        else:
            return None
        return bb
    
    @classmethod
    def fromPoints(cls, obj):
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
            bb.addPoint(obj.GetPoint(i))
            n += 1
        return bb

    def getMax(self):
        return self.max
    
    def getMin(self):
        return self.min
    
    def getMp(self):
        return (self.min + self.max) * 0.5
    
    def getRad(self):
        return (self.max - self.min) * 0.5
    
    def getSize(self):
        return self.max - self.min


def vDeg(v, isHPB=False):
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


def vRad(v, isHPB=False):
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


def vAvg(lst):
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


def vAbsMin(v):
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


def mAbs(m):
    """ ``abs()`` each component vector of matrix m. """
    return c4d.Matrix(abs(m.off), abs(m.v1), abs(m.v2), abs(m.v3))


def buildMatrix(v, off=c4d.Vector(0), order="zyx"):
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


def buildMatrix2(v, off=c4d.Vector(0), base="z"):
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
def getMulP(m, v):
    """ Multiply a matrix with a vector representing a point. """
    return v * m


def getMulV(m, v):
    """ Multiply a matrix with a vector representing a direction. """
    return v ^ m


def det(m):
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


def polyToList(p):
    if not isinstance(p, c4d.CPolygon):
        raise TypeError("E: expected c4d.CPolygon, but got %r" % type(p))
    if p.c == p.d: return [p.a,p.b,p.c]
    return [p.a,p.b,p.c,p.d]


def polyToListList(p, obj):
    """ Convert a ``c4d.CPolygon`` to a list of lists. """
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


def listToPoly(l):
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


def listListToPoly(l):
    """ Convert a list of lists to ``c4d.CPolygon``. """
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


def listListToMatrix(l):
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


def matrixToListList(m, includeOffset=False):
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


def unitNormal(a, b, c):
    """ Calculate unit normal of a planar surface. """
    x = det([[1, a.y, a.z],
             [1, b.y, b.z],
             [1, c.y, c.z]])
    y = det([[a.x, 1, a.z],
             [b.x, 1, b.z],
             [c.x, 1, c.z]])
    z = det([[a.x, a.y, 1],
             [b.x, b.y, 1],
             [c.x, c.y, 1]])
    magnitude = (x ** 2 + y ** 2 + z ** 2) ** .5
    return c4d.Vector(x / magnitude, y / magnitude, z / magnitude).GetNormalized()


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
