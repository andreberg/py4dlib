# -*- coding: utf-8 -*-
# 
#  objects_tests.py
#  py4dlib
#  
#  Created by André Berg on 2012-09-28.
#  Copyright 2012 Berg Media. All rights reserved.
# 
#  andre.bergmedia@googlemail.com
#
# pylint: disable-msg=F0401,W1401

import os
import unittest
import pprint

__version__ = (0, 1)
__date__ = '2012-09-28'
__updated__ = '2013-07-29'


try:
    from py4dlib.objects import ObjectHierarchy
except ImportError:
    pass

pp = pprint.PrettyPrinter()
PP = pp.pprint
PF = pp.pformat

DEBUG = 1 or (os.environ.has_key('DebugLevel') and os.environ['DebugLevel'] > 0)
TESTRUN = 0 or (os.environ.has_key('TestRunLevel') and os.environ['TestRunLevel'] > 0)


DATA = {
    'Source/Group1ABB': [
        'Kegel1', 
        'Kegel2', 
        'Polygons1'
    ], 'Target/Group1/Group1A/Group1AB': [
            'Cube3', 
            'W\ürfel3', 
            'Group1ABA', 
            'Group1ABB'
    ], 'Target': [
            'Target', 
            'Group1'
    ], 'Target/Group1/Group1A/Group1AA': [
            'Cube2', 
            'W\ürfel2'
    ], 'Source/Group1ABA/Sweep-NURBS': [
            'Kreis', 
            'Heart'
    ], 'Target/Group1/Group1A': [
            'Cube1', 
            'W\ürfel1', 
            'Group1AA', 
            'Group1AB', 
            'Group1AC'
    ], 'Source/Group1AC': [
            'Cube3', 
            'W\ürfel3'
    ], 'Source/Group1AA': [
            'Cube2', 'W\ürfel2'
    ], 'Source/Group1AB': [
            'Cube3', 
            'W\ürfel3'
    ], 'Target/Group1/Group1A/Group1AC': [
            'Cube3', 
            'W\ürfel3', 
            'Group1ACA'
    ], 'Source': [
            'Source', 
            'Group1', 
            'Group1A', 
            'Group1AA', 
            'Group1AB', 
            'Group1ABA', 
            'Group1ABB', 
            'Group1AC', 
            'Group1ACA'
    ], 'Source/Group1ABA': [
            'Sweep-NURBS'
    ], 'Source/Group1A': [
            'Cube1', 
            'W\ürfel1'
    ], 'Target/Group1': [
            'Group1A'
    ], 'Target/Group1/Group1A/Group1AB/Group1ABA/Sweep-NURBS': [
            'Kreis', 
            'Heart'
    ], 'Target/Group1/Group1A/Group1AB/Group1ABB': [
            'Kegel1', 
            'Kegel2', 
            'Polygons1'
    ], 'Target/Group1/Group1A/Group1AB/Group1ABA': [
            'Sweep-NURBS'
    ]
}

class OHMock(ObjectHierarchy):
    '''ObjectHierarchy mock object'''
    def __init__(self): # IGNORE:W0231
        # yes, we don't call/init super here to avoid 'c4d' is not defined
        self.sep = '/'
        self.entries = DATA


class ObjectsTest(unittest.TestCase):

    def setUp(self):
        self.mockobj = OHMock()
        
    def testGetFullyQualifiedKeyPath(self):
        expected = ['Sweep-NURBS']
        path = 'Target/Group1/Group1A/Group1AB/Group1ABA'
        actual = self.mockobj.get(path)
        self.assertEqual(actual, expected, 'actual should equal %r, but is %r' % (expected, actual))
        
    def testGetWildcardExpandedKeyPath1(self):
        expected = ['Kreis', 'Heart', 'Sweep-NURBS', 'Kegel1', 'Kegel2', 'Polygons1']
        path = 'Target/Group1/Group1A/Group1AB/*'
        actual = self.mockobj.get(path)
        self.assertEqual(actual, expected, 'actual should equal %r, but is %r' % (expected, actual))
        
    def testGetWildcardExpandedKeyPath2(self):
        expected = ['Kreis', 'Heart', 'Sweep-NURBS', 'Kegel1', 'Kegel2', 'Polygons1']
        path = 'Target/*/*/*/*'
        actual = self.mockobj.get(path)
        self.assertEqual(actual, expected, 'actual should equal %r, but is %r' % (expected, actual))
        
    def testGetWildcardExpandedKeyPath3(self):
        # this also matches 'Target/Group1/Group1A/Group1AB' directly now 
        # since the wildcard character is not after the sepaerator and thus 
        # can evaluate to nothing
        expected = ['Kreis', 'Heart', 'Cube3', 'W\ürfel3', 'Group1ABA', 'Group1ABB', 'Sweep-NURBS', 'Kegel1', 'Kegel2', 'Polygons1']
        path = 'Target/Group1/Group1A/Group1AB*' 
        actual = self.mockobj.get(path)
        self.assertEqual(actual, expected, 'actual should equal %r, but is %r' % (expected, actual))

    def testGetPatternExpandedKeyPath(self):
        expected = ['Target', 'Group1', 'Kegel1', 'Kegel2', 'Polygons1']
        path = '(Source/Group1ABB|Target)' 
        actual = self.mockobj.get(path)
        self.assertEqual(actual, expected, 'actual should equal %r, but is %r' % (expected, actual))
        
    def testGetRePatternExpandedKeyPath(self):
        expected = ['Kegel1', 'Kegel2', 'Polygons1']
        path = '!(?!\T)(Source/Group1ABB|Target)' 
        actual = self.mockobj.get(path)
        self.assertEqual(actual, expected, 'actual should equal %r, but is %r' % (expected, actual))

    def testGetRelativeExpandedKeyPath(self):
        expected = ['Cube3', 'W\ürfel3', 'Group1ABA', 'Group1ABB']
        path = 'Target/Group1/Group1A/Group1AB/Group1ABA/..'
        actual = self.mockobj.get(path)
        self.assertEqual(actual, expected, 'actual should equal %r, but is %r' % (expected, actual))


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