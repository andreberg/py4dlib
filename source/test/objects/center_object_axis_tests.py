# -*- coding: utf-8 -*-
# 
#  center_object_axis_tests.py
#  py4dlib
#  
#  Created by André Berg on 2013-08-02.
#  Copyright 2013 Berg Media. All rights reserved.
#
#  This file is a copy of a Python script
#  to be run on the C4D file of the same name.
#  
# pylint: disable-msg=F0401,W0611,E1103

import os

DEBUG = 1 or ('DebugLevel' in os.environ and os.environ['DebugLevel'] > 0)
TESTRUN = 0 or ('TestRunLevel' in os.environ and os.environ['TestRunLevel'] > 0)

try:
    import c4d  #@UnresolvedImport
    from c4d import documents  #@UnresolvedImport
except ImportError:
    if TESTRUN == 1:
        pass


import py4dlib
from py4dlib.utils import ClearConsole
from py4dlib.maths import BBox
from py4dlib.objects import CreateReplaceObject, CenterObjectAxis, MakeEditable
from py4dlib.mesh import CalcGravityCenter


if DEBUG:
    reload(py4dlib)
    reload(py4dlib.maths)
    reload(py4dlib.mesh)
    reload(py4dlib.utils)
    reload(py4dlib.objects)


def main():
    doc = documents.GetActiveDocument()
    if doc is None:
        return False
    
    doc.StartUndo()

    op = CreateReplaceObject(c4d.Osphere, "TestSphere")
    if op is None:
        return False

    op = MakeEditable(op)
    
    which_p = 1
    trans = c4d.Vector(0, 100, 0)

    doc.AddUndo(c4d.UNDOTYPE_CHANGE, op)
    op.SetPoint(which_p, op.GetPoint(which_p) + trans)

    CenterObjectAxis(op, center="midpoint")
    
    op_mg = op.GetMg()
    op_name = op.GetName()

    bb = BBox.FromObject(op)
    mp = bb.midpoint
    cg = CalcGravityCenter(op)
    
    # no need to multiply with op_mg since we'll insert under TestSphere later
    mp_off = mp # * op_mg
    cg_off = cg # * op_mg

    mp_mg = c4d.Matrix(mp_off, op_mg.v1, op_mg.v2, op_mg.v3)
    cg_mg = c4d.Matrix(cg_off, op_mg.v1, op_mg.v2, op_mg.v3)
    
    print("midpoint in local coords  = %r" % mp_off)
    print("midpoint in global coords = %r" % (mp_off * op_mg))

    print("grav center in local coords  = %r" % cg_off)
    print("grav center in global coords = %r" % (cg_off * op_mg))
    
    mp_null = CreateReplaceObject(c4d.Onull, "%s Midpoint" % op_name)
    cg_null = CreateReplaceObject(c4d.Onull, "%s Gravity Center" % op_name)
    
    cg_null[c4d.NULLOBJECT_DISPLAY] = 7  # Hexagon
    cg_null[c4d.NULLOBJECT_RADIUS] = 125

    mp_null[c4d.NULLOBJECT_DISPLAY] = 2  # Circle
    mp_null[c4d.NULLOBJECT_RADIUS] = 100
    
    mp_null.SetMg(mp_mg)
    cg_null.SetMg(cg_mg)

    mp_null.InsertUnder(op)
    cg_null.InsertUnder(op)

    print("assert(mp_null.GetMg().off == c4d.Vector(0, 50, 0))")
    assert(mp_null.GetMg().off == c4d.Vector(0, 50, 0))
    
    print("True")

    doc.EndUndo()
    doc.Message(c4d.MSG_UPDATE)

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
