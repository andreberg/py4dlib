# -*- coding: utf-8 -*-
# 
#  CreatePlanesFromPolygons.py
#  py4dlib.examples
#  
#  Created by André Berg on 2013-08-08.
#  Copyright 2013 Berg Media. All rights reserved.
#
#  andre.bergmedia@googlemail.com
# 
#  CreatePlanesFromPolygons
#  
#  Create a workplane or plane from a selected polygon.
#  
#  Summary: 
#  
#  Example script that shows how to create a planar primitive such as a workplane 
#  or a plane object and adjust its orientation to match the modelling axis set to 
#  normal mode.
#
# pylint: disable-msg=F0401

"""
Name-US:Create Planes From Polygons
Description-US:Create plane or workingplane objects for each selected polygon on a group of selected objects.
"""

import os

__version__ = (0, 2)
__date__ = '2013-08-08'
__updated__ = '2013-08-08'


DEBUG = 0 or ('DebugLevel' in os.environ and os.environ['DebugLevel'] > 0)
TESTRUN = 0 or ('TestRunLevel' in os.environ and os.environ['TestRunLevel'] > 0)

try:
    import c4d  #@UnresolvedImport
    from c4d import documents
except ImportError:
    if TESTRUN == 1:
        pass


# R14 and above no longer have a workingplane object 
# and I don't know yet how to manipulate the document
# workingplane mode.
if c4d.GetC4DVersion() > 13999:
    TYPE = c4d.Oplane
else:
    TYPE = c4d.Oplane


from py4dlib.utils import ClearConsole
from py4dlib.maths import BuildMatrix3, IsZeroVector
from py4dlib.objects import CreateObject
from py4dlib.mesh import CalcPolyCentroid, CalcPolyNormal


def CreatePlanesFromPolygons(op, typ):
    if not isinstance(op, c4d.PolygonObject):
        raise TypeError("E: expected c4d.PolygonObject, got %r" % (type(op)))

    allpolys = op.GetAllPolygons()
    polysel = op.GetPolygonS()

    selpolys = []
    for i, p in enumerate(allpolys):
        if polysel.IsSelected(i) == True:
            selpolys.append((i, p))
   
    if len(selpolys) == 0:
        print("need at least 1 polygon selected for CreatePlaneFromPolygon")
        return False
    
    mg = op.GetMg()
    op_name = op.GetName()

    planes = []

    for i, p in selpolys:
    
        pids = [p.a, p.b, p.c]
        
        p1 = p.a
        p2 = p.b
        p3 = p.c
        p4 = p.d
        
        plen = 3
        if p.c != p.d: 
            pids.append(p4)
            plen = 4
    
        allp = op.GetAllPoints()
            
        pnts = []
        for id_ in pids:
            pnts.append(allp[id_])
    
        a = allp[p1]
        b = allp[p2]
        c = allp[p3]
        d = allp[p4]
    
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
    
        if DEBUG:
            print("%d: a = %r, b = %r, c = %r, d = %r" % (i, a,b,c,d))
            print("cv1 = %r" % cv1)
            print("cv2 = %r" % cv2)
            print("cv3 = %r" % cv3)
            print("cv4 = %r" % cv4)
            print("cva = %r" % cva)
            print("cvb = %r" % cvb)
    
        pn = CalcPolyNormal(p, op)
        pc = CalcPolyCentroid(pids, op)
        
        AXIS_ZY = 1
    
        base = "x"
        axis = AXIS_ZY

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
        
        cv ^=  mg
    
        if DEBUG:
            #print("vmax = %r" % vmax)
            print("pn = %r" % pn)
            print("cv = %r" % cv)
            print("base = %r" % base)
        
        new_mg = BuildMatrix3(pn ^ mg, cv, off=(pc * mg), base=base)
        #new_mg.v2 = -new_mg.v2
    
        name = "%s Plane %d" % (op_name, i)
        plane = CreateObject(typ, name)
        if plane is None:
            return False
    
        plane.SetMg(new_mg)
        
        if typ == c4d.Oconplane:
            plane[c4d.CONSTRUCTIONPLANE_TYPE] = axis
            plane[c4d.CONSTRUCTIONPLANE_SPACING] = 10
        elif typ == c4d.Oplane:
            plane[c4d.PRIM_AXIS] = axis
            plane[c4d.PRIM_PLANE_WIDTH] = 75
            plane[c4d.PRIM_PLANE_HEIGHT] = plane[c4d.PRIM_PLANE_WIDTH]
        else:
            if DEBUG: 
                print("Unknown plane type: %r" % typ)
            return False
        
        plane.Message(c4d.MSG_UPDATE)
        planes.append(plane)
    
    return planes


def main():
    doc = documents.GetActiveDocument()
    if doc is None:
        return False
    
    doc.StartUndo()
    
    sel = doc.GetSelection()
    if sel is None: 
        return False
            
    # loop through all objects
    for op in sel:
        if not isinstance(op, c4d.PolygonObject):
            if DEBUG:
                print("%s: not a polygon object. Skipping..." % str(op.GetName()))
            continue
        
        print("creating plane(s) for object: %s" % op.GetName())
        
        CreatePlanesFromPolygons(op, TYPE)

    # tell C4D to update internal state  
    c4d.EventAdd() 
    doc.EndUndo()


if __name__ == '__main__':
    ClearConsole()
    main()


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
