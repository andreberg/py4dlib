# -*- coding: utf-8 -*-
# 
#  ShowPolygonNumber.py
#  py4dlib.examples
#  
#  Created by André Berg on 2013-07-29.
#  Copyright 2013 Berg Media. All rights reserved.
#
#  andre.bergmedia@googlemail.com
#
#  ShowPolygonNumber
#
#  Create and attach text splines to polygons.
#  
#  Summary: 
#  
#  Example script that shows how to get point and polygon selections 
#  and how to create objects and attach them to polygons in local and 
#  global coordinate systems.
#
# pylint: disable-msg=F0401

"""
Name-US:Show Polygon Number
Description-US:Create and attach text splines indicating the polygon number to each selected polygon.
"""

import os

__version__ = (0, 2)
__date__ = '2013-07-29'
__updated__ = '2013-08-08'


DEBUG = 0 or ('DebugLevel' in os.environ and os.environ['DebugLevel'] > 0)
TESTRUN = 0 or ('TestRunLevel' in os.environ and os.environ['TestRunLevel'] > 0)

try:
    import c4d  #@UnresolvedImport
    from c4d import documents
except ImportError:
    if TESTRUN == 1:
        pass


if DEBUG:
    import py4dlib
    reload(py4dlib.mesh)
    reload(py4dlib.maths)


from py4dlib.maths import BuildMatrix3, IsZeroVector, BBox
from py4dlib.mesh import CalcPolyNormal, CalcPolyCentroid, CalcPolyArea, PolyToListList
from py4dlib.mesh import GetSelectedPoints, GetSelectedPolys
from py4dlib.objects import CreateObject, InsertUnderNull
from py4dlib.utils import ClearConsole, PPLLString


# group text spline objects under op else insert at root
GROUP_UNDER = True
TEXT_SIZE = 1

def main(doc):  # IGNORE:W0621
    doc.StartUndo()
    
    sel = doc.GetSelection()
    if sel is None: return False
        
    c4d.StopAllThreads()
    
    # loop through all objects
    for op in sel:
        if not isinstance(op, c4d.PolygonObject):
            if DEBUG:
                print("%s: not a polygon object. Skipping..." % str(op.GetName()))
            continue
        print("object name: %s" % op.GetName())
        
        pointsel = op.GetPointS()
        pointselcnt = pointsel.GetCount()
        pointcnt = op.GetPointCount()
        allpoints = op.GetAllPoints()

        print("number of selected points = %s (%s total)" % (pointselcnt, pointcnt))

        polysel = op.GetPolygonS()
        polyselcnt = polysel.GetCount()
        polycnt = op.GetPolygonCount()
        allpolys = op.GetAllPolygons()

        
        print("number of selected polygons = %s (%s total)" % (polyselcnt, polycnt))

        pnts = GetSelectedPoints(op)
        plys = GetSelectedPolys(op)

        if len(plys) == 0:
            # nothing selected? use all polys
            plys = list(xrange(0, polycnt))

        print("selected points = %s" % pnts)
        print("selected polys  = %s" % plys)

        for pnt in pnts:
            print("%d: %s" % (pnt, allpoints[pnt]))

        pmarks = []

        op_mg = op.GetMg()
        op_name = op.GetName()

        pgrp_name = "%s - Polygon #s" % op_name
        pgrp = doc.SearchObject(pgrp_name)
        if pgrp:
            pgrp.Remove()

        for ply in plys:
            poly = allpolys[ply]
            
            a = allpoints[poly.a]
            b = allpoints[poly.b]
            c = allpoints[poly.c]
            d = allpoints[poly.d]

            pids = [a, b, c]

            plen = 3
            if c != d: 
                pids.append(d)
                plen = 4
    
            cv1 = a - b
            cv2 = b - c
            cv3 = c - d
            cv4 = d - a
            if plen == 4:
                cva = (cv3 - cv1)
                cvb = (cv4 - cv2)
            else:
                cva = cv3 - cv1
                cvb = cv3 - cv2

            if plen == 4:
                cv = c4d.Vector(cva.x, cvb.y/2, cva.z)
            else:
                if cvb.y == 0:
                    cv = cvb
                else:
                    cv = cva
    
            if IsZeroVector(cv):
                if cv == cva:
                    cv = cvb
                else:
                    cv = cva

            AXIS_ZY = 1

            base = "x"
            axis = AXIS_ZY 

            if DEBUG: 
                print("pids = %r" % pids)
                print("%d: %s, points as list<list>:" % (ply, poly))
                print("%s" % (PPLLString(PolyToListList(poly, op))))
            
            # calculate polygon normals
            pnormal = CalcPolyNormal(poly, op)
            if DEBUG: print("normal: %s" % (pnormal))

            # calculate polygon area and bounding box 
            parea = CalcPolyArea(poly, op)
            pbb = BBox.FromPolygon(poly, op)
            pbb_slen = pbb.size.GetLength()
            parea = (parea / pbb_slen / 2.0) * TEXT_SIZE
            
            if DEBUG:
                print("pbb_slen: %s" % pbb_slen)
                print("area: %s" % (parea))
            
            # create text spline objects
            pname = "%d" % ply

            pmark = CreateObject(c4d.Osplinetext, pname)
            pmark[c4d.PRIM_TEXT_TEXT] = pname    # Text
            pmark[c4d.PRIM_TEXT_HEIGHT] = parea  # Font Height
            pmark[c4d.PRIM_PLANE] = axis         # Orientation
            
            if GROUP_UNDER:
                ppos = CalcPolyCentroid(poly, op)
            else:
                # put in scene globally and don't group under op
                ppos = CalcPolyCentroid(poly, op) * op_mg
            
            # match position and orientation
            pmg = BuildMatrix3(pnormal, cv, off=ppos, base=base)
            pmg.v2 = -pmg.v2

            # create translation matrix to center the text letters
            tm = c4d.utils.MatrixMove(c4d.Vector(0, -parea/3, 0))
            pmg *= tm

            pmark.SetMg(pmg)
            pmarks.append(pmark)
        
        # group spline text objects under null for each op
        pgrp = InsertUnderNull(pmarks, name=pgrp_name)

        if GROUP_UNDER:
            pgrp.InsertUnder(op)

    # tell C4D to update internal state  
    c4d.EventAdd() 
    doc.EndUndo()

        
if __name__ == '__main__':
    ClearConsole()
    doc = documents.GetActiveDocument()
    main(doc)



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
