# -*- coding: utf-8 -*-
# 
#  PrintObjectHierarchy.py
#  py4dlib.examples
#  
#  Created by André Berg on 2013-07-29.
#  Copyright 2013 Berg Media. All rights reserved.
#
#  andre.bergmedia@googlemail.com
# 
# pylint: disable-msg=F0401

'''PrintObjectHierarchy -- shows how to use the ObjectHierarchy class.'''

import os

__all__ = []
__version__ = (0, 1)
__date__ = '2013-07-29'
__updated__ = '2013-08-02'


DEBUG = 1 or ('DebugLevel' in os.environ and os.environ['DebugLevel'] > 0)
TESTRUN = 0 or ('TestRunLevel' in os.environ and os.environ['TestRunLevel'] > 0)

import pprint

pp = pprint.PrettyPrinter(width=92)
PP = pp.pprint
PF = pp.pformat

try:
    import c4d  #@UnresolvedImport
    from c4d import documents
except ImportError:
    if TESTRUN == 1:
        pass

from py4dlib.objects import ObjectHierarchy
from py4dlib.utils import ClearConsole


def main(doc):  # IGNORE:W0621
    if not doc: return None
    doc.StartUndo()
    
    sel = doc.GetSelection()
    if sel is None: return False
        
    c4d.StopAllThreads()
    
    root = doc.GetFirstObject()
    if not root: return False
    
    print("printing hierarchy starting from %r" % root.GetName())

    oh = ObjectHierarchy(root)
    oh.PPrint()
    
    print("printing Null objects starting from %r" % root.GetName())
    
    oh.PPrint(filtertype=c4d.Onull)
        
    PP(oh)
    print(oh)
    
    filteredObjs = oh.Get('*/*')
    for obj in filteredObjs:
        print obj.GetName()

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
