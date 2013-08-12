# -*- coding: utf-8 -*-
# 
#  test.utils_tests
#  project
#  
#  Created by André Berg on 2013-08-12.
#  Copyright 2013 Berg Media. All rights reserved.
#
#  andre.bergmedia@googlemail.com
# 
# pylint: disable-msg=F0401

import os
import unittest

__version__ = (0, 1)
__date__ = '2013-08-12'
__updated__ = '2013-08-12'


DEBUG = 0 or ('DebugLevel' in os.environ and os.environ['DebugLevel'] > 0)
TESTRUN = 1 or ('TestRunLevel' in os.environ and os.environ['TestRunLevel'] > 0)


from py4dlib import utils
from py4dlib.utils import EscapeUnicode, UnescapeUnicode


class Test(unittest.TestCase):

    def testEscapeUnescapeUnicode(self):
        
        a1 = "W\xfcrfel"        # R12 latin-1 bytes
        u1 = u"W\xfcrfel"       # R12 latin-1 unicode
        a2 = r"W\u00FCrfel"    # R12 bytes escaped unicode
        a3 = "W\xc3\xbcrfel"    # R13/14 utf-8 bytes
        u2 = u"Würfel"          # R13/14 utf-8 unicode
        
        src = [a1, u1, a2, a3, u2]
        
        dst12 = []
        for s in src:
            dst12.append(EscapeUnicode(s))
        
        utils.C4D_VERSION = 13000
        
        dst13 = []
        for s in src:
            dst13.append(EscapeUnicode(s))
        
        for d in dst12:
            self.assertEquals(r"W\u00FCrfel", d)
            
        dst13_expected = src
        
        for i in xrange(len(dst13)):
            self.assertEquals(dst13[i], dst13_expected[i])
        
        utils.C4D_VERSION = 12000
        
        for j in dst12:
            res = UnescapeUnicode(j)
            self.assertEquals(res, u"W\xfcrfel")


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()


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
    