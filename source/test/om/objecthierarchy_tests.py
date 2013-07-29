# -*- coding: utf-8 -*-
# 
#  objecthierarchy_tests.py
#  py4dlib
#  
#  Created by André Berg on 2012-09-28.
#  Copyright 2013 Berg Media. All rights reserved.
#
#  This file is a copy of the Python tag script
#  found in the C4D file of the same name.
#  It is provided for reference in case CINEMA 4D 
#  is not available or the .c4d file can't be opened.
#  
# pylint: disable-msg=F0401,W0611

import os
import pprint

pp = pprint.PrettyPrinter(width=92)
PP = pp.pprint
PF = pp.pformat

DEBUG = 1 or ('DebugLevel' in os.environ and os.environ['DebugLevel'] > 0)
TESTRUN = 0 or ('TestRunLevel' in os.environ and os.environ['TestRunLevel'] > 0)

try:
    import c4d  #@UnresolvedImport
    from c4d import documents  #@UnresolvedImport
except ImportError:
    if TESTRUN == 1:
        pass

from py4dlib import utils, objects  #@UnusedImport
from py4dlib.objects import ObjectHierarchy


def main():
    utils.clearConsole()
    doc = documents.GetActiveDocument()
    if not doc:
        return None
    targetobj = doc.SearchObject('Target')
    sourceobj = doc.SearchObject('Source')
    if not targetobj or not sourceobj:
        return None
    oh = ObjectHierarchy(targetobj)
    oh.pprint()
    oh.pprint(filtertype=c4d.Onull)
    scene = ObjectHierarchy()
    PP(scene)
    print(scene)
    filtered_objs = oh.get('Target/Source/../*')
    for obj in filtered_objs:
        print(obj.GetName())


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
