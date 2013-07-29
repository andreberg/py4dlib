# -*- coding: utf-8 -*-
# 
#  plugins_tests.py
#  py4dlib
#  
#  Created by André Berg on 2012-09-26.
#  Copyright 2012 Berg Media. All rights reserved.
# 
#  andre.bergmedia@googlemail.com
#
# pylint: disable-msg=F0401

import os
import unittest

__version__ = (0, 1)
__date__ = '2012-09-26'
__updated__ = '2013-07-29'

from py4dlib.plugins import UserDefaults

DEFAULTS = {
     'triangulate': True,
     'mode': 'quads',
     'mindistance': 0.005
}

FILEPATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "res", "settings.ini")

class PluginsTest(unittest.TestCase):
    
    def setUp(self):
        for apath in [FILEPATH]:
            if os.path.exists(apath) and not os.path.isdir(apath):
                print("removing %r" % apath)
                os.remove(apath)
        
    def tearDown(self):
        pass

    def testUserDefaultsCreationWithDefaults(self):
        settings = UserDefaults(filepath=FILEPATH, defaults=DEFAULTS)
        self.assertTrue(os.path.exists(settings.filepath))
        statedefaults = settings.state.defaults()
        self.assertDictEqual(statedefaults, DEFAULTS, 'state defaults should be %r, but is %r' % (DEFAULTS, statedefaults))
        expected_contents = """[DEFAULT]
triangulate = True
mindistance = 0.005
mode = quads

[Settings]

"""     
        with open(FILEPATH, 'rb') as savedconfig:
            actual_contents = savedconfig.read()
        self.assertEqual(expected_contents, actual_contents, 'expected contents should be %r, but is %r' % (expected_contents, actual_contents))
        
    def testUserDefaultsCreationNoDefaults(self):
        settings = UserDefaults(filepath=FILEPATH)
        self.assertTrue(os.path.exists(settings.filepath))
        statedefaults = settings.state.defaults()
        self.assertDictEqual(statedefaults, {}, 'state defaults should be %r, but is %r' % ({}, statedefaults))

    def testUserDefaultsModificationAndSaving(self):
        settings = UserDefaults(filepath=FILEPATH)
        self.assertTrue(os.path.exists(settings.filepath))
        settings.set('string', 'some string')
        settings.set('int', 1)
        settings.set('float', 2.0)
        settings.save()
        expected_contents = """[Settings]
string = some string
int = 1
float = 2.0

"""     
        with open(FILEPATH, 'rb') as savedconfig:
            actual_contents = savedconfig.read()
        self.assertEqual(expected_contents, actual_contents, 'expected contents should be %r, but is %r' % (expected_contents, actual_contents))

    def testUserDefaultsReadingAndRetrieving(self):
        settings = UserDefaults(filepath=FILEPATH)
        settings.set('string', 'some string')
        settings.set('int', 1)
        settings.set('float', 2.0)
        settings.save()
        settings2 = UserDefaults(filepath=FILEPATH)
        self.assertTrue(os.path.exists(settings2.filepath))
        strval = settings2.get('string')
        intval = settings2.get('int')
        floatval = settings2.get('float')
        expected_strval = 'some string'
        expected_intval = '1'
        expected_floatval = '2.0'
        self.assertEqual(strval, expected_strval, 'expected string value should be %r, but is %r' % (expected_strval, strval))
        self.assertEqual(intval, expected_intval, 'expected int value should be %r, but is %r' % (expected_intval, intval))
        self.assertEqual(floatval, expected_floatval, 'expected float value should be %r, but is %r' % (expected_floatval, floatval))
        self.assertNotEqual(floatval, 2.0, 'expected float value should not be %r, but is %r' % (2.0, floatval))


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
