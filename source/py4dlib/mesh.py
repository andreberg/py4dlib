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

__version__ = (0, 6)
__date__ = '2013-07-29'
__updated__ = '2013-08-08'


DEBUG = 0 or ('DebugLevel' in os.environ and os.environ['DebugLevel'] > 0)
TESTRUN = 0 or ('TestRunLevel' in os.environ and os.environ['TestRunLevel'] > 0)


try:
    import c4d  #@UnresolvedImport
except ImportError:
    if TESTRUN == 1:
        pass

from py4dlib.maths import VAvg, UnitNormal, BBox


def TogglePolySelection(obj):
    result = False
    if not isinstance(obj, c4d.PolygonObject):
        return result
    totalpolys = obj.GetPolygonCount()
    psel = obj.GetPolygonS()
    while psel.HostAlive() == 1:
        for poly in xrange(totalpolys):
            psel.Toggle(poly)
            result = True
        break
    return result


def SelectAllPolys(obj):
    result = False
    if not isinstance(obj, c4d.PolygonObject):
        return result
    totalpolys = obj.GetPolygonCount()
    psel = obj.GetPolygonS()
    while psel.HostAlive() == 1:
        for poly in xrange(totalpolys):
            psel.Select(poly)
        result = True
        break
    return result


def SelectPolys(li, obj, clearOldSel=True):
    """ Switch the selection state to 'selected' for a list of polygons. 
        Expects a list of polygon indices.
        
        If ``clearOldSel`` is True, clears the old polygon selection.
        Otherwise appends to the current selection. Default is True.
        
        :return: True if the selection state was changed, or False if 
            obj is not a ``c4d.PolygonObject``.
    """
    result = False
    if not isinstance(obj, c4d.PolygonObject):
        return result
    if not isinstance(li, list):
        raise TypeError("E: expected list, got %r" % (type(li)))
    psel = obj.GetPolygonS()
    if clearOldSel is True:
        psel.DeselectAll()
    while psel.HostAlive() == 1:
        for i in li:
            psel.Select(i)
        result = True
        break
    return result


def SelectPoints(li, obj, clearOldSel=True):
    """ Switch the selection state to 'selected' for a list of points. 
        Expects a list of point indices.
        
        If ``clearOldSel`` is True, clears the old polygon selection.
        Otherwise appends to the current selection. Default is True.
        
        :return: True if the selection state was changed, or False if 
            obj is not a ``c4d.PointObject``.
    """
    result = False
    if not isinstance(obj, c4d.PointObject):
        return result
    if not isinstance(li, list):
        raise TypeError("E: expected list, got %r" % (type(li)))
    psel = obj.GetPointS()
    if clearOldSel is True:
        psel.DeselectAll()
    while psel.HostAlive() == 1:
        for i in li:
            psel.Select(i)
        result = True
        break
    return result


def GetSelectedPoints(obj):
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


def GetSelectedPolys(obj):
    """ Returns list of selected polygons indices. 

        To get the actual polygon(s) do something like 
    
        allpolys = obj.GetAllPolygons()
        poly = allpolys[index]
    """
    if not isinstance(obj, c4d.PolygonObject):
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


def GetPointsForIndices(li, obj):
    """ Return a list with the actual points from a list of point indices.
        
        If ``li`` already is of type ``list<c4d.Vector>`` return the list untouched.
    """
    if not isinstance(obj, c4d.PointObject):
        raise TypeError("E: expected c4d.PointObject, got %s" % type(obj))
    if not isinstance(li, list):
        raise TypeError("E: expected list, got %r" % (type(li)))
    if isinstance(li[0], int):
        allp = obj.GetAllPoints()
        lv = []
        for i in li:
            lv.append(allp[i])
    elif isinstance(li[0], c4d.Vector):
        lv = li
    else:
        raise TypeError("E: expected list<int>, got %r" % (type(li[0])))
    return lv


def GetPolysForIndices(li, obj):
    """ Return a list with the actual polygons from a list of polygon indices.
        
        If ``li`` already is of type ``list<c4d.CPolygon>`` return the list untouched.
    """
    if not isinstance(obj, c4d.PointObject):
        raise TypeError("E: expected c4d.PointObject, got %s" % type(obj))
    if not isinstance(li, list):
        raise TypeError("E: expected list, got %r" % (type(li)))
    if isinstance(li[0], int):
        allp = obj.GetAllPolygons()
        lpl = []
        for i in li:
            lpl.append(allp[i])
    elif isinstance(li[0], c4d.CPolygon):
        lpl = li
    else:
        raise TypeError("E: expected list<int>, got %r" % (type(li[0])))
    return lpl


def GetIndicesForPoints(lp, obj):
    """ Return a list of point indices for all points that are 
        equal to the vectors from lp.
        
        Warning: can be time consuming for large models, since this 
        has to check against all points each time for every element 
        in lp. 
        
        You are better off acquiring the list of indices another way. 
        Especially if it is just about converting a list of selected 
        points to their indices. 
        
        Use :py:func:`GetSelectedPoints` in that case.
        
        If ``lp`` already is of type ``list<int>`` return the list untouched.
    """
    if not isinstance(obj, c4d.PointObject):
        raise TypeError("E: expected c4d.PointObject, got %s" % type(obj))
    if not isinstance(lp, list):
        raise TypeError("E: expected list, got %r" % (type(lp)))
    if isinstance(lp[0], int):
        return lp
    elif isinstance(lp[0], c4d.Vector):
        li = []
        allp = obj.GetAllPoints()
        for p in lp:
            for i, pn in enumerate(allp):
                if c4d.utils.VectorEqual(p, pn):
                    li.append(i)
        return li
    else:
        raise TypeError("E: expected list<c4d.Vector>, got %r" % (type(lp[0])))


def GetPolysForPoints(li, obj, strict=True):
    """ Returns a list of polygon indices for all polygons that have 
        points with point indices given by ``li`` as their members. 
        
        This is the same as converting between selections by holding
        Cmd/Ctrl when pressing the modelling mode buttons in CINEMA 4D.
    
        :param bool strict: if True, return only those polygons
            that fully are fully enclosed by all the points that make 
            up that polygon.
    
        If ``li`` already is of type ``list<c4d.CPolygon>`` return the 
        list untouched.
    """
    if not isinstance(obj, c4d.PointObject):
        raise TypeError("E: expected c4d.PointObject, got %s" % type(obj))
    if not isinstance(li, list):
        raise TypeError("E: expected list, got %r" % (type(li)))
    if len(li) == 0:
        return []
    if isinstance(li[0], c4d.CPolygon):
        return li
    lpli = []  # list of poly indices
    allpl = obj.GetAllPolygons()
    if strict is False:
        for pli, poly in enumerate(allpl):
            plli = PolyToList(poly)
            for i in li:
                if i in plli:
                    lpli.append(pli)
            lpli = list(set(lpli))
    else:
        nbr = c4d.utils.Neighbor()
        nbr.Init(obj)
        pdict = {}
        for i in li:
            nbr_polys = nbr.GetPointPolys(i)
            for j in nbr_polys:
                if j in pdict:
                    pdict[j] += 1
                else:
                    pdict[j] = 1
        for k, v in pdict.iteritems():
            if v >= 4:
                lpli.append(k)
    return lpli
            

def CalcPolyCentroid(e, obj):
    """ Calculate the centroid of a polygon by averaging its vertices.
        
        :param e: can be ``c4d.CPolygon``, ``list<int>`` representing 
            point indices, or ``list<c4d.Vector>`` representing a list
            of points.
    """
    if not isinstance(obj, c4d.PolygonObject):
        raise TypeError("E: expected c4d.PolygonObject, got %s" % type(obj))
    if isinstance(e, c4d.CPolygon):
        lst = PolyToList(e)
    elif isinstance(e, list):
        lst = e
    else:
        raise TypeError("E: expected c4d.CPolygon or list of ints representing point indices, got %s" % type(e))
    if isinstance(lst[0], int):
        allp = obj.GetAllPoints()
        vlst = []
        for i in lst:
            vlst.append(allp[i])
    elif isinstance(lst[0], c4d.Vector):
        vlst = lst
    else:
        raise TypeError("E: expected list<int> or list<c4d.Vector>, got %r" % (type(lst[0])))   
    return VAvg(vlst)


def CalcPolyNormal(e, obj):
    """ Calculate the orientation of face normal by using Newell's method.
    
        See :py:func:`CalcVertexNormal` for an example of usage within the calling context.
        
        :param e: can be ``c4d.CPolygon``, ``list<int>`` representing 
            point indices, or ``list<c4d.Vector>`` representing a list
            of points.
    """
    if not isinstance(obj, c4d.PolygonObject):
        raise TypeError("E: expected c4d.PolygonObject, got %s" % type(obj))
    if isinstance(e, c4d.CPolygon):
        lst = PolyToList(e)
    elif isinstance(e, list):
        lst = e
    else:
        raise TypeError("E: expected c4d.CPolygon or list, got %s" % type(e))
    lv = GetPointsForIndices(lst, obj)
    N = c4d.Vector(0,0,0)
    llen = len(lv)
    for i in range(llen):
        x = i
        n = ((i+1) % llen)
        vtx = lv[x]
        vtn = lv[n]
        N.x += (vtx.y - vtn.y) * (vtx.z + vtn.z)
        N.y += (vtx.z - vtn.z) * (vtx.x + vtn.x)
        N.z += (vtx.x - vtn.x) * (vtx.y + vtn.y)
    return N.GetNormalized()
    

def CalcVertexNormal(v, idx, obj):
    """ Calculate the vertex normal by averaging surrounding face normals.
        Usually called from a construct like the following:
    
        .. code::
        
            # calculate the average normal of a selected points
            vtx_normals = []
            
            for i, point in enumerate(obj.GetAllPoints()):
                if pointsel.IsSelected(i):
                    vn = CalcVertexNormal(point, i, obj)
                    vtx_normals.append(vn)
            
            N = VAvg(vtx_normals)
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
        normal = CalcPolyNormal(poly, obj)
        normals.append(normal)
    ln = len(normals)
    if ln == 0: return N # beware of div by zero
    for n in normals:
        N += n
    N = c4d.Vector(N.x/ln, N.y/ln, N.z/ln)
    return N.GetNormalized()


def CalcAverageVertexNormal(obj):
    """ Calculate the average normal of a selection of points. 
    
        This gives the same normal as setting the modelling tool 
        to "Normal" mode for an arbitrary point selection.
        
        :return: normal or zero vector if no points selected.
    """
    if not isinstance(obj, (c4d.PointObject, c4d.PolygonObject)):
        raise TypeError("E: expected c4d.PointObject or c4d.PolygonObject, got %r" % (type(obj)))
    
    points = obj.GetAllPoints()
    pointsel = obj.GetPointS()
    
    if pointsel.GetCount() == 0:
        return c4d.Vector(0)
    
    vtx_normals = []
    for i, p in enumerate(points):
        # calc average vertex normal
        if pointsel.IsSelected(i):
            vn = CalcVertexNormal(p, i, obj)
            vtx_normals.append(vn)
        
    N = VAvg(vtx_normals)
    return N


def CalcThreePointNormal(v1, v2, v3):
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


def CalcTriangleArea(p, obj):
    if not isinstance(obj, c4d.PointObject):
        return None
    if not isinstance(p, c4d.CPolygon):
        raise TypeError("E: expected c4d.CPolygon, got %s" % type(p))
    lst = PolyToList(p)
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


def CalcPolyArea(p, obj, normalized=False):
    total = c4d.Vector(0, 0, 0)
    ply = PolyToList(p)
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
    normal = UnitNormal(allp[ply[0]], allp[ply[1]], allp[ply[2]])
    result = total.Dot(normal)
    return abs(result / 2)


def CalcBBox(e, selOnly=False, obj=None):
    """ Construct a :py:class:`BBox` for a ``c4d.PointObject``, a ``c4d.CPolygon``,
        or a list of polygon indices. If you have a list of point indices you can
        construct a BBox directly using the :py:func:`FromPointList` class method.
        
        You must supply the object the polygon list belongs to in the latter case.
    
        Note that if you are interested in the midpoint or radius only, you can
        use the built-in ``c4d.BaseObject.GetMp()`` and ``GetRad()`` methods 
        respectively.
    
        :param bool selOnly:  if True, use selected points 
            only if e is a ``c4d.PointObject``. Otherwise use 
            all points of the object.  
    """
    if isinstance(e, c4d.PointObject):
        bb = BBox.FromObject(e, selOnly=selOnly)
        return bb
    elif isinstance(e, c4d.CPolygon):
        if e.c == e.d:
            bb = BBox.FromPointList([e.a, e.b, e.c])
        else:
            bb = BBox.FromPointList([e.a, e.b, e.c, e.d])
        return bb
    elif isinstance(e, list):
        if not isinstance(obj, c4d.PolygonObject):
            raise TypeError("E: expected c4d.PolygonObject, got %r" % (type(obj)))
        pnts = []
        allpolys = obj.GetAllPolygons()
        allpnts = obj.GetAllPoints()
        for i in e:
            p = allpolys[i]
            if p.c == p.d:
                pnts.extend([allpnts[p.a], allpnts[p.b], allpnts[p.c]])
            else:
                pnts.extend([allpnts[p.a], allpnts[p.b], allpnts[p.c], allpnts[p.d]])
        bb = BBox.FromPointList(pnts)
        return bb
    else:
        raise TypeError("E: expected c4d.PointObject or c4d.CPolygon, but got %r" % (type(e)))


def CalcGravityCenter(obj):
    """ Calculate the center of gravity for obj. """
    if not isinstance(obj, c4d.PointObject):
        raise TypeError("E: expected c4d.PointObject, got %r" % (type(obj)))
    maxpoints = obj.GetPointCount()
    if maxpoints == 0:
        return c4d.Vector(0)
    cg = c4d.Vector(0)
    scale = 1.0 / maxpoints
    for c in xrange(0, maxpoints):
        cg += (obj.GetPoint(c) * scale)
    return cg


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
