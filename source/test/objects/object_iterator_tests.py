# -*- coding: utf-8 -*-
# 
#  object_iterator_tests.py
#  py4dlib
#  
#  Created by André Berg on 2012-09-26.
#  Copyright 2013 Berg Media. All rights reserved.
#
#  This file is a copy of the Python tag script
#  found in the C4D file of the same name.
#  It is provided for reference if C4D is not
#  available or the .c4d file can't be opened.
#  
#  andre.bergmedia@googlemail.com
#
# pylint: disable-msg=F0401,W0611

import os

DEBUG = 1 or ('DebugLevel' in os.environ and os.environ['DebugLevel'] > 0)
TESTRUN = 0 or ('TestRunLevel' in os.environ and os.environ['TestRunLevel'] > 0)

try:
    from c4d import documents  #@UnresolvedImport
except ImportError:
    if TESTRUN == 1:
        pass

from py4dlib import utils
from py4dlib.objects import ObjectIterator


def main():
    utils.ClearConsole()

    doc = documents.GetActiveDocument()
    if not doc: 
        return False

    # get some objects from the om tree...
    # ...at top level hierarchy
    group1obj = doc.SearchObject('Group1')
    # ... and somewhere further down
    cube2obj = doc.SearchObject('Cube2') 
    if not group1obj or not cube2obj: 
        return False

    indent = 4
    
    print("this should iterate through Group1's children and")
    print("it should stop before Group2\n")
    
    cur = []
    for op, lvl in ObjectIterator(group1obj):
        print("%s%s" % (' ' * lvl * indent, op.GetName()))
        cur.append(op.GetName())
    
    assert(cur == ['Group1A', 'Cube', 'Würfel', 'Group1AA', 'Cube2', 
            'Wuerfel2', 'Group1B', 'Sweep-NURBS', 'Kreis', 'Heart'])
    
    print("\n")
    print("this should iterate starting from and including Group1")
    print("and it should not stop unless at the end of the object")
    print("manager top level\n")

    cur = []
    for op, lvl in ObjectIterator(group1obj, children_only=False):
        print("%s%s" % (' ' * lvl * indent, op.GetName()))
        cur.append(op.GetName())

    assert(cur == ["Group1", "Group1A", "Cube", "Würfel", "Group1AA", 
        "Cube2", "Wuerfel2", "Group1B", "Sweep-NURBS", "Kreis", "Heart", 
        "Group2", "Röhre", "Zylinder", "Zylinder2", "Group3", "Group3A", 
        "Group3AA", "Group3AB", "Kugel", "Platonischer Körper", "Group4", 
        "Group4A", "Group4AA", "Group4AB", "Kugel2", "Platonischer Körper2"])
    
    print("\n")
    print("this should iterate through Group1's children only and it ")
    print("should stop before Cube2:\n")
    
    cur = []
    for op, lvl in ObjectIterator(group1obj, stopobj=cube2obj):
        print("%s%s" % (' ' * lvl * indent, op.GetName()))
        cur.append(op.GetName())

    assert(cur == ["Group1A", "Cube", "Würfel", "Group1AA"])

    # now test iterating within a sub hierarchy

    # get some more objects from the om tree...
    # ...at sub level hierarchy
    group3obj = doc.SearchObject('Group3')
    # ... and somewhere further down
    group3abobj = doc.SearchObject('Group3AB') 
    if not group3obj or not group3abobj: 
        return False

    print("\n")
    print("this should iterate through Group3's children and it should stop")
    print("before going up again through Zylinder2\n")

    cur = []
    for op, lvl in ObjectIterator(group3obj, startlvl=4):
        print("%s%s" % (' ' * lvl * indent, op.GetName()))
        cur.append(op.GetName())

    assert(cur == ["Group3A", "Group3AA", "Group3AB", "Kugel", "Platonischer Körper"])

    print("\n")
    print("this should iterate starting from and including Group3 and it ")
    print("should not stop unless at the end of the object manager top level\n")

    cur = []
    for op, lvl in ObjectIterator(group3obj, children_only=False, startlvl=4):
        print("%s%s" % (' ' * lvl * indent, op.GetName()))
        cur.append(op.GetName())

    assert(cur == ["Group3", "Group3A", "Group3AA", "Group3AB", "Kugel", 
        "Platonischer Körper",  "Group4", "Group4A", "Group4AA", "Group4AB", 
        "Kugel2", "Platonischer Körper2"])

    print("\n")
    print("this should iterate through Group3's children only and it should ")
    print("stop after Group3AB\n")

    cur = []
    for op, lvl in ObjectIterator(group3obj, stopobj=group3abobj, startlvl=4):
        print("%s%s" % (' ' * lvl * indent, op.GetName()))
        cur.append(op.GetName())

    assert(cur == ["Group3A", "Group3AA"])


if __name__ == '__main__':
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
