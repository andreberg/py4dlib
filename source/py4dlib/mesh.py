# -*- coding: utf-8 -*-
# 
#  mesh.py
#  py4dlib
#  
#  Created by André Berg on 2013-07-29.
#  Copyright 2013 Berg Media. All rights reserved.
#
#  andre.bergmedia@googlemail.com
# 
# pylint: disable-msg=F0401

'''py4dlib.mesh -- point and polygon operations.'''

import os

__version__ = (0, 2)
__date__ = '2013-07-29'
__updated__ = '2013-07-31'


DEBUG = 0 or ('DebugLevel' in os.environ and os.environ['DebugLevel'] > 0)
TESTRUN = 0 or ('TestRunLevel' in os.environ and os.environ['TestRunLevel'] > 0)


try:
    import c4d  #@UnresolvedImport
except ImportError:
    if TESTRUN == 1:
        pass

from py4dlib.math import vAvg, polyToList, unitNormal, BBox


def togglePolySelection(obj):
    result = False
    if not isinstance(obj, c4d.PointObject):
        return result
    totalpolys = obj.GetPolygonCount()
    psel = obj.GetPolygonS()
    while psel.HostAlive() == 1:
        for poly in xrange(totalpolys):
            psel.Toggle(poly)
            result = True
        break
    return result


def selectAllPolys(obj):
    result = False
    if not isinstance(obj, c4d.PointObject):
        return result
    totalpolys = obj.GetPolygonCount()
    psel = obj.GetPolygonS()
    while psel.HostAlive() == 1:
        for poly in xrange(totalpolys):
            psel.Select(poly)
        result = True
        break
    return result


def getSelectedPoints(obj):
    """ Returns list of selected point indices. 

    To get the actual point(s) do something like 

    allpoints = op.GetAllPoints()
    point = allpoints[index]
    """
    if not isinstance(obj, c4d.PointObject):
        return None
    else:
        result = []
        pnts = obj.GetPointCount()
        psel = obj.GetPointS()
        for idx, sel in enumerate(psel.GetAll(pnts)):
            if not sel: 
                continue
            else:
                result.append(idx)
        return result


def getSelectedPolys(obj):
    """ Returns list of selected polygons indices. 

    To get the actual polygon(s) do something like 

    allpolys = obj.GetAllPolygons()
    poly = allpolys[index]
    """
    if not isinstance(obj, c4d.PointObject):
        return None
    else:
        result = []
        plys = obj.GetPolygonCount()
        psel = obj.GetPolygonS()
        for idx, sel in enumerate(psel.GetAll(plys)):
            if not sel: 
                continue
            else:
                result.append(idx)
        return result


def calcPolyCentroid(p, obj):
    """ Calculate the centroid of a polygon by averaging its vertices. """
    if not isinstance(obj, c4d.PointObject):
        return None
    if not isinstance(p, c4d.CPolygon):
        raise TypeError("E: expected c4d.CPolygon, got %s" % type(p))
    lst = polyToList(p)
    allp = obj.GetAllPoints()
    vlst = []
    for i in lst:
        vlst.append(allp[i])
    return vAvg(vlst)


def calcPolyNormal(p, obj):
    """ Calculate the orientation of face normal by using Newell's method.
        See calcVertexNormal for an example of usage within the calling context.
    """
    if not isinstance(p, c4d.CPolygon):
        raise TypeError("E: expected c4d.CPolygon, got %s" % type(p))
    N = c4d.Vector(0,0,0)
    lst = polyToList(p)
    llen = len(lst)
    allp = obj.GetAllPoints()
    for i in range(llen):
        x = i
        n = ((i+1) % llen)
        vtx = allp[lst[x]]
        vtn = allp[lst[n]]
        N.x += (vtx.y - vtn.y) * (vtx.z + vtn.z)
        N.y += (vtx.z - vtn.z) * (vtx.x + vtn.x)
        N.z += (vtx.x - vtn.x) * (vtx.y + vtn.y)
    return N.GetNormalized()
    

def calcVertexNormal(v, idx, obj):
    """ Calculate the vertex normal by averaging surrounding face normals.
        Usually called from a construct like the following:
    
        for i, point in enumerate(obj.GetAllPoints()):
            vn = calcVertexNormal(point, i, obj)
    """
    if not isinstance(v, c4d.Vector):
        raise TypeError("E: expected c4d.Vector, got %s" % type(v))
    N = c4d.Vector(0,0,0)
    nb = c4d.utils.Neighbor()
    nb.Init(obj)
    pntpolys = nb.GetPointPolys(idx)
    polys = []
    normals = []
    allp = obj.GetAllPolygons()
    for poly in pntpolys:
        poly = allp[poly]
        polys.append(poly)
        normal = calcPolyNormal(poly, obj)
        normals.append(normal)
    ln = len(normals)
    if ln == 0: return N # beware of div by zero
    for n in normals:
        N += n
    N = c4d.Vector(N.x/ln, N.y/ln, N.z/ln)
    return N.GetNormalized()


def calcThreePointNormal(v1, v2, v3):
    """ Calculate the surface normal of a three point plane.
        Doesn't take orientation of neighboring polygons into account.
    """
    try:
        d1 = - v1 + v3
        d2 = - v2 + v3
        result = d1.Cross(d2).GetNormalized()
    except Exception, e:
        raise ValueError("E: surface normal calculation failed. The error message was: %r" % e)
    return result


def calcTriangleArea(p, obj):
    if not isinstance(obj, c4d.PointObject):
        return None
    if not isinstance(p, c4d.CPolygon):
        raise TypeError("E: expected c4d.CPolygon, got %s" % type(p))
    lst = polyToList(p)
    llen = len(lst)
    if llen != 3:
        raise ValueError("E: expected triangle, but got n-gon with n = %d" % llen)
    allp = obj.GetAllPoints()
    result = 0
    for i in range(0, 3, 3):
        a = i
        b = i+1
        c = i+2
        v1 = allp[lst[a]]
        v2 = allp[lst[b]]
        v3 = allp[lst[c]]
        d1 = v3 - v1
        d2 = v3 - v2
        result += (d1.Cross(d2).GetLength()) / 2.0
    return result


def calcPolyArea(p, obj, normalized=False):
    total = c4d.Vector(0, 0, 0)
    ply = polyToList(p)
    lply = len(ply)
    if lply < 3:
        return 0
    allp = obj.GetAllPoints()
    for i in range(0, lply):
        v1 = allp[ply[i]]
        if i is lply-1:
            v2 = allp[ply[0]]
        else:
            v2 = allp[ply[i+1]]
        prod = v1.Cross(v2)
        if normalized:
            prod.Normalize()
        total.x += prod.x
        total.y += prod.y
        total.z += prod.z
    normal = unitNormal(allp[ply[0]], allp[ply[1]], allp[ply[2]])
    result = total.Dot(normal)
    return abs(result / 2)


def calcBBox(e):
    """ Construct a :py:class:`BBox` for a ``c4d.PointObject`` - 
        using selected points only or all points if no selection -  
        or for a ``c4d.CPolygon``. 
    """
    if isinstance(e, c4d.PointObject):
        bb = BBox.fromPoints(e)
        return bb
    elif isinstance(e, c4d.CPolygon):
        if e.c == e.d:
            bb = BBox.fromPoints([e.a, e.b, e.c])
        else:
            bb = BBox.fromPoints([e.a, e.b, e.c, e.d])
        return bb
    else:
        raise TypeError("E: expected c4d.PointObject or c4d.CPolygon, but got %r" % (type(e)))


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
