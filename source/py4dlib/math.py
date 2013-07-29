# -*- coding: utf-8 -*-
# 
#  math.py
#  py4dlib
#  
#  Created by André Berg on 2013-07-29.
#  Copyright 2013 Berg Media. All rights reserved.
#
#  andre.bergmedia@googlemail.com
# 
# pylint: disable-msg=F0401

'''py4dlib.math -- linalg etc. functions'''

import os

__version__ = (0, 1)
__date__ = '2013-07-29'
__updated__ = '2013-07-29'


DEBUG = 0 or ('DebugLevel' in os.environ and os.environ['DebugLevel'] > 0)
TESTRUN = 0 or ('TestRunLevel' in os.environ and os.environ['TestRunLevel'] > 0)


try:
    import c4d  #@UnresolvedImport
    from c4d.utils import Rad, Deg
except ImportError:
    if TESTRUN == 1:
        pass


def vDeg(v, isHPB=False):
    """ Convert each component of vector v to degrees. """
    if v is None:
        raise ValueError("v can't be None")
    if not isinstance(v, c4d.Vector): 
        raise TypeError("Expected vector, got %s" % type(v))
    if isHPB:
        res = c4d.Vector(0,0,0)
        res.x = Deg(v.x)
        res.y = Deg(v.y)
        res.z = Deg(v.z)
        if res.x >= 180:
            res.x -= 360
        if res.y >= 180:
            res.y -= 360
        if res.z >= 180:
            res.z -= 360
        return res
    else:
        return c4d.Vector(Deg(v.x), Deg(v.y), Deg(v.z))


def vRad(v, isHPB=False):
    """ Convert each component of vector v to radians. """
    if v is None:
        raise ValueError("v can't be None")
    if not isinstance(v, c4d.Vector): 
        raise TypeError("Expected vector, got %s" % type(v))
    if isHPB:
        if v.x >= 180:
            v.x -= 360
        if v.y >= 180:
            v.y -= 360
        if v.z >= 180:
            v.z -= 360
    return c4d.Vector(Rad(v.x), Rad(v.y), Rad(v.z))


def vAvg(lst):
    """ Calculate the average of a list of vectors. """
    if lst is None:
        raise ValueError("List lst can't be None")
    if not isinstance(lst, list): 
        raise TypeError("Expected list of vectors, got %s" % type(lst))
    lstlen = len(lst)
    res = c4d.Vector(0,0,0)
    if lstlen == 0: return res
    for l in lst:
        res.x += l.x
        res.y += l.y
        res.z += l.z
    res.x = res.x / float(lstlen)
    res.y = res.y / float(lstlen)
    res.z = res.z / float(lstlen)
    return res


def vAbsMin(v):
    """ Return min component of a vector using abs(x) < abs(y) comparisons. """
    if v is None:
        raise ValueError("v can't be None")
    if not isinstance(v, c4d.Vector): 
        raise TypeError("Expected vector, got %s" % type(v))
    result = v.x
    if abs(v.y) < abs(v.x):
        result = v.y
    elif abs(v.z) < abs(v.x):
        result = v.z
    return result
    

def buildMatrix(v, off=c4d.Vector(0), order="zyx"):
    """ Builds a new orthonormal basis from a direction 
        and (optionally) an offset vector using John F. 
        Hughes and Thomas Möller's method.
    """
    if v is None or not isinstance(v, c4d.Vector):
        raise ValueError("Expected c4d.Vector, but got %r" % v)
    r = v.GetNormalized()
    mincomp = c4d.utils.VectorMin(v)
    if r.x == mincomp:
        s = c4d.Vector(0, -r.z, r.y)
    elif r.y == mincomp:
        s = c4d.Vector(-r.z, 0, r.x)
    else:
        s = c4d.Vector(-r.y, r.x, 0)
    s = s.GetNormalized()
    t = r.Cross(s)
    t = t.GetNormalized()
    if order == "xyz":
        return c4d.Matrix(off, r, s, t)
    elif order == "xzy":
        return c4d.Matrix(off, r, t, s)
    elif order == "yxz":
        return c4d.Matrix(off, s, r, t)        
    elif order == "yzx":
        return c4d.Matrix(off, s, t, r)        
    elif order == "zxy":
        return c4d.Matrix(off, t, r, s)        
    elif order == "zyx":
        return c4d.Matrix(off, t, s, r)
    else:
        return c4d.Matrix(off, r, s, t)


def buildMatrix2(v, base="z", off=c4d.Vector(0)):
    """ Builds a new orthonormal basis from a direction 
        and (optionally) an offset vector. 
    """
    if v is None or not isinstance(v, c4d.Vector):
        raise ValueError("Expected c4d.Vector, but got %r" % v)
    if base == "z":
        z = v.GetNormalized()
        x = z.Cross(c4d.Vector(1, 0, 0)).GetNormalized()
        y = x.Cross(z).GetNormalized()
    elif base == "y":
        y = v.GetNormalized()
        z = y.Cross(c4d.Vector(0, 0, 1)).GetNormalized()
        x = z.Cross(y).GetNormalized()
    else:  # "x"
        x = v.GetNormalized()
        y = x.Cross(c4d.Vector(0, 1, 0)).GetNormalized()
        z = y.Cross(x).GetNormalized()
    return c4d.Matrix(off, x, y, z)


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
