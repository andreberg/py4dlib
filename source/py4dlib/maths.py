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

__version__ = (0, 5)
__date__ = '2013-07-29'
__updated__ = '2013-08-06'


DEBUG = 0 or ('DebugLevel' in os.environ and os.environ['DebugLevel'] > 0)
TESTRUN = 0 or ('TestRunLevel' in os.environ and os.environ['TestRunLevel'] > 0)


try:
    import c4d  #@UnresolvedImport
    from c4d.utils import Rad, Deg
except ImportError:
    if TESTRUN == 1:
        pass


twopi = 2 * math.pi
eps = 0.0000001


def FloatEqual(a, b, places=8):
    """ Same as ``c4d.utils.FloatTolerantCompare`` just a shorter function name. """
    return round(abs(b - a), places) == 0

            
class BBox(object):
    """
    Calculate various bounding box metrics from a list of points, 
    such as min, max, midpoint, radius and size.
    """
    def __init__(self):
        super(BBox, self).__init__()
        FLOATMIN = sys.float_info[3]-1000 # workaround for underflow error
        FLOATMAX = sys.float_info[0]
        self.min = c4d.Vector(FLOATMAX)
        self.max = c4d.Vector(FLOATMIN)
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
            self.AddPoint(p)
        
    @classmethod
    def FromPointList(cls, lst):
        """
        Returns a new BBox object with all 
        points from a list added.
        
        Elements of lst must be of type ``c4d.Vector``.
        
        :raise ValueError: if the list is empty.
        """
        if isinstance(lst, list):
            if not isinstance(lst[0], c4d.Vector):
                # only check the first entry in the 
                # interest of performance since this
                # code may be called in performance
                # critical sections.
                raise TypeError("E: expected c4d.Vector in lst, got %s" % type(lst[0]))
            allpnts = lst
        else:
            raise TypeError("E: expected list of c4d.Vectors, got %s" % type(lst))
        if len(lst) == 0: 
            raise ValueError("E: list of points is empty")
        bb = BBox()
        for i, p in enumerate(allpnts):  # IGNORE:W0612 @UnusedVariable
            bb.AddPoint(p)
            bb.np += 1
        return bb
    
    @classmethod
    def FromObject(cls, obj, sel_only=False):
        """
        Returns a new BBox object with all 
        points from the passed object.
        
        :param sel_only: ``bool`` - use selected
        points only instead of all points.
        
        :raise ValueError: if the object has 
        no points.
        """
        if not isinstance(obj, c4d.PointObject):
            raise TypeError("E: expected c4d.PointObject, got %s" % type(obj))
        allpnts = obj.GetAllPoints()
        if len(allpnts) == 0: 
            raise ValueError("E: object has no points")
        bb = BBox()
        if sel_only is True:
            pntsel = obj.GetPointS()
            if pntsel.HostAlive():
                for i, p in enumerate(allpnts):  # IGNORE:W0612 @UnusedVariable
                    if pntsel.IsSelected(i):
                        bb.AddPoint(obj.GetPoint(i))
                        bb.np += 1
            else:
                return bb
        else:
            for i, p in enumerate(allpnts):  # IGNORE:W0612 @UnusedVariable
                bb.AddPoint(p)
                bb.np += 1
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
    

class Plane(object):
    """
    Represents a plane defined by positional offset and normal direction.
    """
    
    def __init__(self, pos, n):
        super(Plane, self).__init__()
        self.pos = pos
        self.n = n.GetNormalized()
        if DEBUG: 
            print("New plane with pos = %r, normal n = %r" % (pos, n))

    def __str__(self):
        return "%r, pos = %r, n = %r" % (self, self.pos, self.n)
    
    def SetN(self, new_n):
        self.n = new_n.GetNormalized()
    
    def SetPos(self, new_pos):
        self.pos = new_pos
    
    def SideAsString(self, d):
        if d < 0:
            res = "back"
        elif d == 0:
            res = "onplane"
        else:
            res = "front"
        return res
    
    def PointResidence(self, p):
        """
        Define the resident direction of a point with respect
        to the plane.
        
        The point can be either in front of the plane (+1), on the
        plane (0) or at the back of the plane (-1).
        """
        d = self.PointDistance(p)
        if d <= eps:
            d = -1
        elif abs(d) < eps:
            d = 0
        else:
            d = 1
        if DEBUG: 
            print("point residence = %r" % d)
        return d
    
    def PointDistance(self, p, get_signed=True):
        """
        Calculate distance from a point p to the plane.
        
        :param bool get_signed: set to True if you want the signed distance.
        
        A signed distance can be useful to determine if the point is located 
        in the half space from the backside of the plane or in the half space 
        on the front.
        """
        if p is None:
            raise ValueError("Point p can't be None")
        if not isinstance(p, c4d.Vector):
            raise TypeError("Expected Vector, got %s" % type(p))
        if DEBUG: 
            print("pos = %r, n = %r, p = %r" % (self.pos, self.n, p))
        if not get_signed:
            projp = self.LineIntersection(p)
            if projp is None:
                raise ValueError("dist can't be None when projected along plane normal!")
            dist = (p - projp).GetLength()
        else:
            pos = self.pos
            n = self.n
            d = -n * pos
            dist = (n.x * p.x + n.y * p.y + n.z * p.z + d)
            if DEBUG:
                s = ""
                if get_signed is True:
                    s = " (signed)"
                print("dist = %r%s" % (dist, s))
        return dist
    
    def LineIntersection(self, p, d=None):
        """
        Calculate intersection point with a line starting at position p
        and pointing in the direction d. 
                
        :param c4d.Vector d: direction of the line. 
            If None, the normal of the plane will be used instead.
            
        :return: ``c4d.Vector`` representing the intersection point, or
        None if an intersection isn't possible (parallel directions).
        """
        if not isinstance(p, c4d.Vector):
            raise TypeError("E: expected c4d.Vector, got %s" % type(p))
        n = self.n
        if d is None:
            d = n
        elif not isinstance(d, c4d.Vector):
            raise TypeError("E: expected c4d.Vector, got %s" % type(d))
        else:
            d.Normalize()
        pos = self.pos
        ddn = d.Dot(n)
        if abs(ddn) < eps:
            return None
        mu = (pos - p).Dot(n) / ddn
        p_isect = p + mu * d
        return p_isect


def VDeg(v, isHPB=False):
    """ Convert each component of vector v to degrees. """
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


def VAvg(lv):
    """ Calculate the average of a list of vectors. """
    if not isinstance(lv, list): 
        raise TypeError("E: expected list of c4d.Vectors, got %s" % type(lv))
    lstlen = len(lv)
    res = c4d.Vector(0,0,0)
    if lstlen == 0: return res
    for l in lv:
        res.x += l.x
        res.y += l.y
        res.z += l.z
    res.x = res.x / float(lstlen)
    res.y = res.y / float(lstlen)
    res.z = res.z / float(lstlen)
    return res


def VAbsMin(v):
    """ Return min component of a vector using abs(x) < abs(y) comparisons. """
    if not isinstance(v, c4d.Vector): 
        raise TypeError("E: expected c4d.Vector, got %s" % type(v))
    result = v.x
    if abs(v.y) < abs(v.x):
        result = v.y
    elif abs(v.z) < abs(v.x):
        result = v.z
    return result


def VAbsMax(v):
    """ Return max component of a vector using abs(x) > abs(y) comparisons. """
    if not isinstance(v, c4d.Vector): 
        raise TypeError("E: expected c4d.Vector, got %s" % type(v))
    result = v.x
    if abs(v.y) > abs(v.x):
        result = v.y
    elif abs(v.z) > abs(v.x):
        result = v.z
    return result


def VBoundaryLerp(lv, t=0.5):
    """
    Interpolate linearily between a list of vectors, such that 
    the resulting vector points to the weighted midpoint in the
    vector space defined by the boundaries max X to min X and 
    max Y to min Y.
    
    :param float t: the weighting coefficient.
    
    :return: None if len(lst) is 0 or if the angle between 
    the two max/min vectors is greater than 180 degrees.
    """
    if not isinstance(lv, list): 
        raise TypeError("E: expected list, got %s" % type(lv))
    if not isinstance(lv[0], c4d.Vector): 
        raise TypeError("E: expected list of c4d.Vector, got list of %s" % type(lv[0]))
    lstlen = len(lv)
    FLOATMIN = sys.float_info[3]-1000
    FLOATMAX = sys.float_info[0]
    vnull = c4d.Vector(0)
    vmin = c4d.Vector(FLOATMAX)
    vmax = c4d.Vector(FLOATMIN)
    res = None
    if lstlen == 0: 
        return res
    maxV, minV = vmax, vmin
    for v in lv:
        if v.x < minV.x: minV = v
        if v.x > maxV.x: maxV = v
    a = c4d.utils.VectorAngle(minV, maxV)
    if DEBUG:
        print("minV = %r, maxV = %r" % (minV, maxV))
        print("angle between minV and maxV = %r" % (a))
    if a <= eps:
        return None
    if a >= Rad(180):
        a -= Rad(180)
        a = -a
    midV = vnull
    t1 = (math.sin((1.0 - t) * a) / math.sin(a))
    t2 = (math.sin(t * a) / math.sin(a))
    midV.x = t1 * minV.x + t2 * maxV.x
    midV.y = t1 * minV.y + t2 * maxV.y
    return midV


def VLerp(startv, endv, t=0.5):
    """ Linear interpolation between 2 vectors. """
    if t <= 0.0 or t > 1.0:
        raise ValueError("E: t must satisfy 0<t<1, but is %f" % t)
    return (startv + (t * (endv - startv)))


def VNLerp(startv, endv, t=0.5):
    """ Normalized linear interpolation between 2 vectors. """
    if t <= 0.0 or t > 1.0:
        raise ValueError("E: t must satisfy 0<t<1, but is %f" % t)
    return VLerp(startv, endv, t).GetNormalized()


def VSLerp(startv, endv, t=0.5):
    """ Spherical linear interpolation between 2 vectors. """
    if t <= 0.0 or t > 1.0:
        raise ValueError("E: t must satisfy 0<t<1, but is %f" % t)
    dot = endv.Dot(startv)
    #if dot <= -1.0:
    #    dot = -1.0
    #if dot >= 1.0:
    #    dot = 1.0
    theta = SafeAcos(dot) * t
    relv = endv - startv * dot
    relv.Normalize()
    r = (startv * math.cos(theta))
    s = (relv * math.sin(theta))
    result = r + s
    return result


def MAbs(m):
    """ ``abs()`` each component vector of matrix m. """
    return c4d.Matrix(abs(m.off), abs(m.v1), abs(m.v2), abs(m.v3))


def BuildMatrix(v, off=None, order="zyx"):
    """ Builds a new orthonormal basis from a direction 
        and (optionally) an offset vector using John F. 
        Hughes and Thomas Möller's method.
    """
    if v is None or not isinstance(v, c4d.Vector):
        raise ValueError("E: expected c4d.Vector, got %r" % v)
    if off is None:
        off = c4d.Vector(0)
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


def BuildMatrix2(v, off=None, base="z"):
    """ Builds a new orthonormal basis from a direction 
        and (optionally) an offset vector using base 
        aligned cross products. 
        
        :param base:  ``str`` the base component 'v' represents.
    """
    if v is None or not isinstance(v, c4d.Vector):
        raise ValueError("E: expected c4d.Vector, got %r" % v)
    if off is None:
        off = c4d.Vector(0)
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
    """ Multiply a matrix with a vector representing a point. 
        Same as ``c4d.Matrix.Mul(v)``.
    """
    return v * m


def GetMulV(m, v):
    """ Multiply a matrix with a vector representing a direction. 
        Same as ``c4d.Matrix.MulV(v)``
    """
    return v ^ m


def Det(m):
    """ Determinant of an ``n x n`` matrix.
     
        m can be of type ``c4d.Matrix`` when ``n = 3`` 
        or ``list<list>`` when ``n = 3`` or ``n = 4`` .
    """
    def __check_dimensions(m, req):
        for i, row in enumerate(m):
            if len(row) != req:
                ValueError("E: non-square matrix, with row %d != required size %d" % (i, req))
    if isinstance(m, list):
        flen = len(m[0])
        if flen == 3:
            __check_dimensions(m, flen)
            # row major
            return (m[0][0] * m[1][1] * m[2][2] +
                    m[0][1] * m[1][2] * m[2][0] + 
                    m[0][2] * m[1][0] * m[2][1] - 
                    m[0][2] * m[1][1] * m[2][0] - 
                    m[0][1] * m[1][0] * m[2][2] - 
                    m[0][0] * m[1][2] * m[2][1])
            # column major
            #return (-m[0][2] * m[1][1] * m[2][0] + 
            #         m[0][1] * m[1][2] * m[2][0] + 
            #         m[0][2] * m[1][0] * m[2][1] -
            #         m[0][0] * m[1][2] * m[2][1] - 
            #         m[0][1] * m[1][0] * m[2][2] +
            #         m[0][0] * m[1][1] * m[2][2])
        elif flen == 4:
            __check_dimensions(m, flen)
            return (m[0][3] * m[1][2] * m[2][1] * m[3][0] - 
                    m[0][2] * m[1][3] * m[2][1] * m[3][0] -
                    m[0][3] * m[1][1] * m[2][2] * m[3][0] +
                    m[0][1] * m[1][3] * m[2][2] * m[3][0] +
                    m[0][2] * m[1][1] * m[2][3] * m[3][0] -
                    m[0][1] * m[1][2] * m[2][3] * m[3][0] -
                    m[0][3] * m[1][2] * m[2][0] * m[3][1] +
                    m[0][2] * m[1][3] * m[2][0] * m[3][1] +
                    m[0][3] * m[1][0] * m[2][2] * m[3][1] -
                    m[0][0] * m[1][3] * m[2][2] * m[3][1] -
                    m[0][2] * m[1][0] * m[2][3] * m[3][1] +
                    m[0][0] * m[1][2] * m[2][3] * m[3][1] +
                    m[0][3] * m[1][1] * m[2][0] * m[3][2] -
                    m[0][1] * m[1][3] * m[2][0] * m[3][2] -
                    m[0][3] * m[1][0] * m[2][1] * m[3][2] +
                    m[0][0] * m[1][3] * m[2][1] * m[3][2] +
                    m[0][1] * m[1][0] * m[2][3] * m[3][2] -
                    m[0][0] * m[1][1] * m[2][3] * m[3][2] -
                    m[0][2] * m[1][1] * m[2][0] * m[3][3] +
                    m[0][1] * m[1][2] * m[2][0] * m[3][3] +
                    m[0][2] * m[1][0] * m[2][1] * m[3][3] -
                    m[0][0] * m[1][2] * m[2][1] * m[3][3] -
                    m[0][1] * m[1][0] * m[2][2] * m[3][3] +
                    m[0][0] * m[1][1] * m[2][2] * m[3][3])
    return (m.v1.x * m.v2.y * m.v3.z + 
            m.v1.y * m.v2.z * m.v3.x + 
            m.v1.z * m.v2.x * m.v3.y - 
            m.v1.z * m.v2.y * m.v3.x - 
            m.v1.y * m.v2.x * m.v3.z - 
            m.v1.x * m.v2.z * m.v3.y)


def Transpose(e):
    """ Transpose matrix e in row-major format to column-major.
        ``e`` can be of type ``list<list>`` structure or ``c4d.Matrix``.
    """
    if isinstance(e, list):
        ll = e
    elif isinstance(e, c4d.Matrix):
        ll = MatrixToListList(e)
    else:
        raise TypeError("E: expected list<list> or c4d.Matrix, got %r" % (type(e)))
    temp = zip(*ll)  # IGNORE:W0142
    result = []
    for i in temp:
        result.append(list(i))
    return result


def PolyToList(p):
    """ Convert a ``c4d.CPolygon`` to a ``list`` of ``c4d.Vectors``, 
        representing the points of the polygon. 
    """ 
    if not isinstance(p, c4d.CPolygon):
        raise TypeError("E: expected c4d.CPolygon, got %r" % type(p))
    if p.c == p.d: 
        return [p.a,p.b,p.c]
    return [p.a,p.b,p.c,p.d]


def PolyToListList(p, obj):
    """ Convert a ``c4d.CPolygon`` to a ``list<list>`` structure. 
    
    ``list<list>`` represents a list of points comprised of a 
    list of coordinate values.
    """
    if not isinstance(p, c4d.CPolygon):
        raise TypeError("E: expected c4d.CPolygon, got %r" % type(p))
    if not isinstance(obj, c4d.PolygonObject):
        raise TypeError("E: expected c4d.PolygonObject, got %r" % type(obj))
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

    
def ListToPoly(li):
    """ Convert a ``list`` of ``int`` representing indices 
        into an object's point list to a ``c4d.CPolygon``. 
    """
    if not isinstance(li, list): 
        raise TypeError("E: expected list, got %r" % type(li))
    for i, e in enumerate(li):
        if not isinstance(e, int):
            raise TypeError("E: element %d of l should be of type int, but is %r" % (i, type(e)))
    ln = len(li)
    if ln < 3:
        raise IndexError("list must have at least 3 indices")
    elif ln == 3:
        return c4d.CPolygon(li[0],li[1],li[2])
    else:
        return c4d.CPolygon(li[0],li[1],li[2],li[3])


def ListListToPoly(lli):
    """ Convert a ``list<list>`` structure to ``c4d.CPolygon``. 
    
    ``list<list>`` represents a list of indices that indentify
    points of an object.
    """
    if not isinstance(lli, list): 
        raise TypeError("E: expected list, got %r" % type(lli))
    for i, e in enumerate(lli):
        if not isinstance(e, int):
            raise TypeError("E: element %d of l should be of type int, but is %r" % (i, type(e)))
    ln = len(lli)
    if ln < 3:
        raise IndexError("E: list must have at least 3 indices")
    elif ln == 3:
        return c4d.CPolygon(lli[0][0], lli[0][1], lli[0][2],
                            lli[1][0], lli[1][1], lli[1][2],
                            lli[2][0], lli[2][1], lli[2][2])
    else:
        return c4d.CPolygon(lli[0][0], lli[0][1], lli[0][2],
                            lli[1][0], lli[1][1], lli[1][2],
                            lli[2][0], lli[2][1], lli[2][2],
                            lli[3][0], lli[3][1], lli[3][2])


def ListListToMatrix(lli):
    """ Convert a ``list<list>`` structure, representing a list of list 
        of coordinate values to a ``c4d.Matrix``. 
        
        See :py:func:`MatrixToListList` to find out which list corresponds
        to which matrix component.
    """
    if not isinstance(lli, list):
        raise TypeError("E: expected list of list, got %r" % type(lli))
    m = len(lli)
    n = len(lli[0])
    if not isinstance(lli[0], (float, int)):
        raise TypeError("E: expected list elements of type float or int, got %r" % (type(lli[0])))
    # check dimensions.
    # 
    # This part could be handled by a local private function but 
    # risks creating a closure that prolongs the time required for
    # local variable lookup outside the function. 
    for i in xrange(m):
        n = len(lli[i])
        if n != 3 and n != 4:
            raise ValueError("E: wrong dimensions. n must equal 3 or 4, but is %d" % (m))
    if m == 4 and n == 4:
        return c4d.Matrix(c4d.Vector(lli[0][0], lli[0][1], lli[0][2], lli[0][3]), 
                          c4d.Vector(lli[1][0], lli[1][1], lli[1][2], lli[1][3]),
                          c4d.Vector(lli[2][0], lli[2][1], lli[2][2], lli[2][3]),
                          c4d.Vector(lli[3][0], lli[3][1], lli[3][2], lli[3][3]))
    elif m == 4 and n == 3:
        return c4d.Matrix(c4d.Vector(lli[0][0], lli[0][1], lli[0][2]), 
                          c4d.Vector(lli[1][0], lli[1][1], lli[1][2]),
                          c4d.Vector(lli[2][0], lli[2][1], lli[2][2]),
                          c4d.Vector(lli[3][0], lli[3][1], lli[3][2]))
    else:
        raise ValueError("E: invalid dimensions. Accepted dimensions include 4x4 and 4x3, but currently are %dx%d" % (m, n))
    

def ListToMatrix(lv):
    """ Convert a list of 3 or 4 ``c4d.Vector`` to ``c4d.Matrix``. """ 
    if not isinstance(lv, list):
        raise TypeError("E: expected list of vectors, got %r" % type(lv))
    m = len(lv)
    if not isinstance(lv[0], c4d.Vector):
        raise TypeError("E: expected list elements of type c4d.Vector, got %r" % (type(lv[0])))
    if m == 4:
        return c4d.Matrix(lv[0], lv[1], lv[2], lv[3])
    elif m == 3:
        return c4d.Matrix(c4d.Vector(0), lv[1], lv[2], lv[3])
    else:
        raise ValueError("E: need list of length 3 or 4, got %d" % (m))


def MatrixToListList(m, incl_off=False):
    """ Convert a ``c4d.Matrix`` to a ``list<list>`` structure. 
        The structure layout is generally in row-major format, 
        and the ordering the same as the order required for 
        constructing a ``c4d.Matrix`` by hand:
        
        .. code::
            
            [[off.x, off.y, off.z],
             [v1.x,   v1.y,  v1.z], 
             [v2.x,   v2.y,  v2.z],
             [v3.x,   v3.y,  v3.z]]
    """
    if not isinstance(m, c4d.Matrix):
        raise TypeError("E: expected c4d.Matrix, got %r" % type(m))
    if incl_off is True:
        return [[m.off.x, m.off.y, m.off.z],
                [m.v1.x,  m.v1.y,  m.v1.z],
                [m.v2.x,  m.v2.y,  m.v2.z],
                [m.v3.x,  m.v3.y,  m.v3.z]]
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
    mag = (x ** 2 + y ** 2 + z ** 2) ** .5
    if mag > 0.0:
        a_type = type(a)  # make testable
        result = a_type(x / mag, y / mag, z / mag).GetNormalized()
        return result
    else:
        raise ValueError("E: magnitude must be > 0.0")


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


def IsColinear(lv):
    """ Given a list of vectors check if they all share the same coordinates 
        in at least 2 dimensions. 
        
        :return: True if all the vectors in the list are co-linear. 
    """
    x = lv[0].x
    y = lv[0].y
    z = lv[0].z
    is_cl_x = 1
    is_cl_y = 1
    is_cl_z = 1
    for v in lv:
        if not FloatEqual(v.x, x):
            is_cl_x = 0
            break
    for v in lv:
        if not FloatEqual(v.y, y):
            is_cl_y = 0
            break
    if is_cl_x + is_cl_y >= 2:
        return True
    for v in lv:
        if not FloatEqual(v.z, z):
            is_cl_z = 0
            break
    return (is_cl_x + is_cl_y + is_cl_z) >= 2

        
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
