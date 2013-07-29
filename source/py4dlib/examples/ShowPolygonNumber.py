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
# pylint: disable-msg=F0401

''' 
ShowPolygonNumber -- create and attach text splines to polygons.

Summary: 

Example script that shows how to get point and polygon selections 
and how to create objects and attach them to polygons in local and 
global coordinate systems.
'''

import os

__all__ = []
__version__ = (0, 1)
__date__ = '2013-07-29'
__updated__ = '2013-07-29'


DEBUG = 1 or ('DebugLevel' in os.environ and os.environ['DebugLevel'] > 0)
TESTRUN = 0 or ('TestRunLevel' in os.environ and os.environ['TestRunLevel'] > 0)

try:
    import c4d  #@UnresolvedImport
    from c4d import documents
except ImportError:
    if TESTRUN == 1:
        pass
    
from py4dlib.mesh import getSelectedPoints, getSelectedPolys, calcPolyNormal, calcPolyCentroid
from py4dlib.math import buildMatrix2
from py4dlib.objects import createObject, insertUnderNull
from py4dlib.utils import clearConsole


# group text spline objects under op else insert at root
GROUP_UNDER = True


def main(doc):  # IGNORE:W0621
    doc.StartUndo()
    
    sel = doc.GetSelection()
    if sel is None: return False
        
    c4d.StopAllThreads()
    
    # loop through all objects
    for op in sel:
        if not isinstance(op, c4d.PointObject):
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

        pnts = getSelectedPoints(op)
        plys = getSelectedPolys(op)

        if len(plys) == 0:
            # nothing selected? use all polys
            plys = list(xrange(0, polycnt))

        print("selected points = %s" % pnts)
        print("selected polys  = %s" % plys)

        for pnt in pnts:
            print("%d: %s" % (pnt, allpoints[pnt]))

        pmarks = []

        for ply in plys:
            poly = allpolys[ply]
            if DEBUG: print("%d: %s" % (ply, poly))

            # calculate polygon normals
            pnormal = calcPolyNormal(poly, op)
            if DEBUG: print("normal: %s" % (pnormal))
            
            # create text spline objects
            pname = "%d" % ply
            pmark = doc.SearchObject(pname)
            if pmark:
                pmark.Remove()
            pmark = createObject(c4d.Osplinetext, pname)
            pmark[c4d.PRIM_TEXT_TEXT] = pname     # Text
            pmark[c4d.PRIM_TEXT_HEIGHT] = 5       # Font Height 0.1
            pmark[c4d.PRIM_PLANE] = 1             # Plane ZY
            
            op_mg = op.GetMg()
            op_rr = c4d.utils.HPBToMatrix(op.GetRelRot())
            
            if GROUP_UNDER:
                ppos = calcPolyCentroid(poly, op)
                prot = pnormal 
            else:
                # put in scene globally and don't group under op
                ppos = calcPolyCentroid(poly, op) * op_mg
                prot = (op_rr * pnormal)

            # match position and orientation
            pmg = buildMatrix2(prot, off=ppos, base="-x")
            pmark.SetMg(pmg)
            
            pmarks.append(pmark)
        
        # group spline text objects under null for each op
        pgrp_name = "%s - Polygon #s" % op.GetName()
        pgrp = doc.SearchObject(pgrp_name)
        if pgrp:
            pgrp.Remove()
        pgrp = insertUnderNull(pmarks, name=pgrp_name)

        if GROUP_UNDER:
            pgrp.InsertUnder(op)

    # tell C4D to update internal state  
    c4d.EventAdd() 
    doc.EndUndo()

        
if __name__ == '__main__':
    clearConsole()
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
