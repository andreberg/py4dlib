# -*- coding: utf-8 -*-
# 
#  test.maths_tests
#  project
#  
#  Created by André Berg on 2013-08-02.
#  Copyright 2013 Berg Media. All rights reserved.
#
#  andre.bergmedia@googlemail.com
# 
# pylint: disable-msg=F0401

import os
import math
import unittest

__version__ = (0, 1)
__date__ = '2013-08-02'
__updated__ = '2013-08-05'


DEBUG = 1 or ('DebugLevel' in os.environ and os.environ['DebugLevel'] > 0)
TESTRUN = 0 or ('TestRunLevel' in os.environ and os.environ['TestRunLevel'] > 0)


try:
    import c4d  #@UnresolvedImport
except ImportError:
    if TESTRUN == 1:
        pass

from py4dlib.maths import Det, UnitNormal, Transpose, VLerp, VNLerp, VSLerp

eps = 0.000001

def FloatEqual(a, b, places=len(str(eps))-2):
    return round(abs(b - a), places) == 0
    
class VectorMock(object):
    """ Mock object for c4d.Vectors """
    
    def __init__(self, x, y=None, z=None):
        if y is None:
            y = x
        if z is None:
            z = x
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
    
    def __str__(self):
        return ("%r, x = %s, y = %s, z = %s" % (self, self.x, self.y, self.z))

    def __len__(self):
        return self.GetLength()
    
    def __sub__(self, other):
        return VectorMock(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def __rsub__(self, other):
        return VectorMock(other.x - self.x, other.y - self.y, other.z - self.z)
        
    def __add__(self, other):
        return VectorMock(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __mul__(self, other):
        return VectorMock(self.x * other, self.y * other, self.z * other)
    
    def __rmul__(self, other):
        return self.__mul__(other)

    def __eq__(self, other):
        return (FloatEqual(self.x, other.x) and FloatEqual(self.y, other.y) and FloatEqual(self.z, other.z))
        
    def GetLength(self):
        return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)
    
    def GetNormalized(self):
        ool = 1.0 / len(self)
        return VectorMock(self.x * ool, self.y * ool, self.z * ool)
 
    def Normalize(self):
        ool = 1.0 / len(self)
        self.x *= ool
        self.y *= ool
        self.z *= ool
           
    def Dot(self, other):
        return float(self.x * other.x + self.y * other.y + self.z * other.z)

    def Cross(self, other):
        return VectorMock(self.y * other.z - self.z * other.y, 
                          self.z * other.x - self.x * other.z,
                          self.x * other.y - self.y * other.x)
        
class CPolygonMock(object):
    """ Mock object for c4d.CPolygons """
    def __init__(self, a, b, c, d=None):
        self.a = a
        self.b = b
        self.c = c
        if d is None:
            d = c
        self.d = d


class Test(unittest.TestCase):


    def testDet(self):
        m = [[ 1, 22,  3],
             [ 5,  1,  7],
             [ 9, -1,  2]]
        det = Det(m)
        
        self.assertEquals(1133, det)
        
        m2 = [[ 1, 22,  3,  4], 
              [ 5,  6,  7,  8], 
              [ 9, 22, 22, 12], 
              [13, 14, 15, 16]]
        det2 = Det(m2)
        
        self.assertEquals(5280, det2)
        
    def testUnitNormal(self):
        a = VectorMock(-100,  100,  100)
        b = VectorMock(-100,  100, -100)
        c = VectorMock(-100, -100,  100)
        
        normal = UnitNormal(a, b, c)
        
        self.assertEquals(-1.0, normal.x)
    
    def testTranspose(self):
        m44 = [[1,   2,  3,  4],
               [5,   6,  7,  8],
               [9,  10, 11, 12],
               [13, 14, 15, 16]]
        
        expected = [[1, 5,  9, 13], 
                    [2, 6, 10, 14], 
                    [3, 7, 11, 15], 
                    [4, 8, 12, 16]]
        
        m44_t = Transpose(m44)
        self.assertEquals(m44_t, expected)

    def testVLerp(self):
        vs = VectorMock(2, 2, 2)
        ve = VectorMock(4, 4, 4)
        
        vl = VLerp(vs, ve)
        expected = VectorMock(3.0)
        
        self.assertEquals(vl, expected)
        
    def testVNLerp(self):
        vs = VectorMock(2, 2, 2)
        ve = VectorMock(4, 4, 4)
        
        vnl = VNLerp(vs, ve)
        expected = VectorMock(0.6)
        
        self.assertEquals(vnl, expected)
        print(vnl)
        
        
    def testSLerp(self):
        vs = VectorMock(0, 1, 0)
        ve = VectorMock(1, 0, 0)
        
        vsl = VSLerp(vs, ve)
        expected = VectorMock(0.707106781187, 0.707106781187, 0.0)
        
        self.assertEquals(vsl, expected)
        print(vsl)
        
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
    