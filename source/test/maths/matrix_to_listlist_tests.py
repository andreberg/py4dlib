# -*- coding: utf-8 -*-
# 
#  matrix_to_listlist_tests.py
#  py4dlib
#  
#  Created by André Berg on 2013-08-02.
#  Copyright 2013 Berg Media. All rights reserved.
#
#  This file is a copy of a Python script
#  to be run on the C4D file of the same name.
#  
# pylint: disable-msg=F0401,W0611

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
from py4dlib.utils import PPLLString, ClearConsole
from py4dlib.maths import MatrixToListList, ListListToMatrix
from py4dlib.objects import CreateObject, Select

if DEBUG:
    reload(py4dlib)
    reload(py4dlib.maths)
    reload(py4dlib.utils)


def main():
    ClearConsole()
    doc = documents.GetActiveDocument()
    op = doc.SearchObject("Cube")
    if op is not None:
        print("Removing old Cube...")
        op.Remove()
    print("Creating new Cube...")
    op = CreateObject(c4d.Ocube, "Cube")
    Select(op)

    print("")

    mg = op.GetMg()
    n_off = c4d.Vector(100, 0, 0)
    n_mg = c4d.Matrix(n_off, mg.v1, mg.v2, mg.v3)
    
    print("Setting new mg from manually constructed Matrix:")
    print("  %r" % n_mg)
    op.SetMg(n_mg)
    
    print("")

    print("Converting matrix n_mg to list<list>:")
    n_mgll = MatrixToListList(n_mg, incl_off=True)
    print("")
    
    print("Displaying new mg as list<list>:") 
    print(PPLLString(n_mgll))
    print("")
    
    print("Setting new global matrix from list<list>:") 
    n_ll = [[200.0, 10.0, 0.0],
            [  2.0,  0.0, 0.0], 
            [  0.0,  2.0, 0.0], 
            [  0.0,  0.0, 2.0]]
    print(PPLLString(n_ll))
    print("")
    
    print("Converting list<list> structure to Matrix n_llmg")
    n_llmg = ListListToMatrix(n_ll)
    print("  %r" % n_llmg)
    print("")
    
    print("Setting n_llmg")
    print("")
    op.SetMg(n_llmg)
    
    print("assert op.GetMg().off.x == 200")
    
    assert(op.GetMg().off.x == 200)
    print("True")
    
    c4d.EventAdd()

if __name__=='__main__':
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
