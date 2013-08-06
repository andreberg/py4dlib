# -*- coding: utf-8  -*-
# 
#  PlaneProjector.pyp
#  py4dlib.examples
#  
#  Created by André Berg on 2011-03-30.
#  Copyright 2013 Berg Media. All rights reserved.
#  
#  Version 1.0
#  Updated: 2013-08-04
#
#  andre.bergmedia@googlemail.com
# 
# pylint: disable-msg=F0401,E1101,W0232
from py4dlib.maths import BuildMatrix2

'''
PlaneProjector -- project selected points along a direction vector onto a planar target.

Summary:

Can snap any number of points onto planar targets along local or global X, Y, Z, a manual
direction or the averaged vertex normals (basically the direction of the modelling tool's
Normal setting for a group of selected points).

Currently needs a working plane object as a target object. You can create a new working
plane yourself and pick it up to be the target by pressing the pick target button (<) or
you can select any three points on any polygon or point object and it will create the
working plane for you when you press the (<) button.

As a future improvement it shouldn't be hard at all to use polygons of other objects as
planar targets. 
'''

import os
import sys
import time
import math

__version__ = (1, 0)
__date__ = '2011-03-30'
__updated__ = '2013-08-06'

DEBUG = 0 or ('DebugLevel' in os.environ and os.environ['DebugLevel'] > 0)
TESTRUN = 0 or ('TestRunLevel' in os.environ and os.environ['TestRunLevel'] > 0)

try:
    import c4d  #@UnresolvedImport
    from c4d import plugins, bitmaps, gui, documents
    from c4d.utils import *
except ImportError:
    if TESTRUN == 1:
        pass

PY4DLIB_FOUND = False

try:
    from py4dlib.maths import Plane, IsZeroVector, VAvg, VAbsMax, BBox
    from py4dlib.objects import FindObject, CreateObject, UniqueSequentialName, SetGlobalRotation, ObjectAxisFromVector
    from py4dlib.mesh import CalcAverageVertexNormal, CalcThreePointNormal, CalcPolyCentroid, CalcPolyNormal
    PY4DLIB_FOUND = True
except ImportError:
    pass

if DEBUG:
    import pprint
    pp = pprint.PrettyPrinter(width=200)
    PP = pp.pprint
    PF = pp.pformat

VNULL = c4d.Vector(0)
VX = c4d.Vector(1,0,0)
VY = c4d.Vector(0,1,0)
VZ = c4d.Vector(0,0,1)

CR_YEAR = time.strftime("%Y")


# -------------------------------------------
#                GLOBALS 
# -------------------------------------------

PLUGIN_NAME    = "Plane Projector"
PLUGIN_VERSION = '.'.join(str(x) for x in __version__)
PLUGIN_HELP    = "Project selected points along a direction vector onto planar target"
PLUGIN_ABOUT   = """(C) %s Andre Berg (Berg Media)
All rights reserved.

Version %s

Plane Projector allows you to have a selection of 
points projected along a direction onto a planar 
target.

Select a construction plane or a plane object and
press the "Get Object" button (<). Then switch back
to your polygon object, select some points and press
"Project". The direction in which the projection will
occur, can be set using the direction combo box.

Set the Target Up Axis to the base component that is
pointing away from the planar surface. E.g. for a new
workplane object with type XZ this would be the Y-axis.

Tip: you can also select exactly 3 points on any point
or polygon object and hit the (<) button to create a
new working plane aligned to those three points.

Use at your own risk! 

It is recommended to try out the plugin 
on a spare copy of your data first.
""" % (CR_YEAR, PLUGIN_VERSION)

PY4DLIB_NOT_FOUND_MSG = """This plugin needs py4dlib which is missing.

Please download and install it free of charge
from http://github.com/andreberg/py4dlib.
"""

# -------------------------------------------
#               PLUGING IDS 
# -------------------------------------------

# unique ID
ID_PLANEPROJECTOR = 1026917


# Element IDs
IDD_DIALOG_SETTINGS  = 10001
IDC_GROUP_WRAPPER    = 10002
IDC_GROUP_SETTINGS   = 10003
IDC_STATIC_TARGET    = 10004
IDC_EDIT_TARGET      = 10005
IDC_BUTTON_GETOBJ    = 10006
IDC_STATIC_UPAXIS    = 10007
IDC_COMBO_UPAXIS     = 10008
IDC_GROUP_SETTINGS2  = 10009
IDC_STATIC_MODE      = 10010
IDC_COMBO_MODE       = 10011
IDC_GROUP_SETTINGS3  = 10012
IDC_STATIC_MANUAL    = 10013
IDC_GROUP_MANUAL     = 10014
IDC_EDIT_X           = 10015
IDC_EDIT_Y           = 10016
IDC_EDIT_Z           = 10017
IDC_GROUP_BUTTONS    = 10018
IDC_BUTTON_CANCEL    = 10019
IDC_BUTTON_DOIT      = 10020
IDC_DUMMY            = 10021
IDC_MENU_ABOUT       = 30001

# String IDs
IDS_DIALOG_TITLE   = PLUGIN_NAME
IDS_MENU_INFO      = "Info"
IDS_MENU_ABOUT     = "About..."

# "Enum"

ID_MODE_NORMAL   = 1
ID_MODE_MANUAL   = 2
ID_MODE_X        = 3
ID_MODE_Y        = 4
ID_MODE_Z        = 5
ID_MODE_LOCAL_X  = 6
ID_MODE_LOCAL_Y  = 7
ID_MODE_LOCAL_Z  = 8

ID_UPAXIS_X = 1
ID_UPAXIS_Y = 2
ID_UPAXIS_Z = 3


# ------------------------------------------------------
#                   User Interface 
# ------------------------------------------------------

class PlaneProjectorDialog(gui.GeDialog):
    mode = None
    target = None
    target_name = None
    opip = 0
    def CreateLayout(self):
        self.SetTitle(IDS_DIALOG_TITLE)
        
        plugins.GeResource().Init(os.path.dirname(os.path.realpath(__file__)))
        self.LoadDialogResource(IDD_DIALOG_SETTINGS, flags=c4d.BFH_SCALEFIT)
        
        # Menu
        self.MenuFlushAll()
        self.MenuSubBegin(IDS_MENU_INFO)
        self.MenuAddString(IDC_MENU_ABOUT, IDS_MENU_ABOUT)
        self.MenuSubEnd()
        
        self.MenuFinished()
        
        return True
        
    def EnableManual(self, flag):
        self.Enable(IDC_EDIT_X, flag)
        self.Enable(IDC_EDIT_Y, flag)
        self.Enable(IDC_EDIT_Z, flag)
    
    def InitValues(self):
        self.SetLong(IDC_COMBO_MODE, 1)
        self.SetDegree(IDC_EDIT_X, 0.0)
        self.SetDegree(IDC_EDIT_Y, 0.0)
        self.SetDegree(IDC_EDIT_Z, 0.0)
        self.SetLong(IDC_COMBO_UPAXIS, 2)
        self.EnableManual(False)
        return True
    
    def CoreMessage(self, id, msg):
        if id == c4d.DOCUMENT_CHANGED:
            if self.target is not None and self.target_name is not None:
                target_name = self.target_name
                op = FindObject(target_name)
                if op is None or op.GetUniqueIP() != self.opip: 
                    self.RemoveTarget()
                    return True
        return True
    
    def SetTarget(self, op):
        if op.GetName() == self.target_name and op.GetUniqueIP() == self.opip:
            if DEBUG:
                print("Reusing same target with IP %d" % self.opip)
            return
        new_name = UniqueSequentialName("Plane Projector Target", template=u'%(name)s')
        op.SetName(new_name)
        c4d.EventAdd()
        self.opip += 1
        op.SetUniqueIP(self.opip)
        self.target = op
        self.target_name = new_name
        if DEBUG:
            print("Setting target %s (%r) with IP %d" % (self.target_name, self.target, self.opip))
        self.SetString(IDC_EDIT_TARGET, self.target_name)
    
    def RemoveTarget(self):
        if DEBUG:
            print("Removing target %s (%r) with IP %d" % (self.target_name, self.target, self.opip))
        self.target = None
        self.target_name = None
        self.opip -= 1
        self.SetString(IDC_EDIT_TARGET, "")
    

    def CreatePlane(self, op, typ, pidx):
        # if we have more than three points it's 
        # ambigious which ones we should utilize
        # so only make it happen if exactly three
        if DEBUG: 
            print("Creating snap target plane...")
    
        if len(points) != 3:
            raise ValueError("E: need exactly 3 points, got %d" % len(points))
        
        allp = op.GetAllPoints()
    
        p1 = pidx[0]
        p2 = pidx[1]
        p3 = pidx[2]
    
        a = allp[p1]
        b = allp[p2]
        c = allp[p3]
    
        mg = op.GetMg()
        rot = c4d.utils.MatrixToHPB(mg)
    
        plane_type = typ
        
        c4d.StopAllThreads()
        
        # TODO: if ALT is held down maybe look for another
        # object with name "Plane Projector Target" and remove it
        
        n = CalcThreePointNormal(a, b, c)
        pn = CalcPolyNormal([p1, p2, p3], op)
        pc = CalcPolyCentroid(e, obj)
    
        AXIS_XY = 0
        AXIS_ZY = 1
        AXIS_XZ = 2
        
        vmax = VAbsMax(n)
    
        if n.x == vmax:
            base = "x"
            axis = AXIS_ZY
        elif n.y == vmax:
            base = "y"
            axis = AXIS_XZ
        else:
            base = "z"
            axis = AXIS_XY
    
        n = abs(n)
        bb = BBox.FromPointList([a, b, c])
        
        new_mg = BuildMatrix2(pn ^ mg, pc * mg, base=base)
        new_mg2 = ObjectAxisFromVector(n ^ mg)
        
        name = UniqueSequentialName("Plane Projector Target", template=u'%(name)s')
        plane = CreateObject(plane_type, name)
        if plane is None:
            return False
        
        if plane_type == c4d.Oconplane:
            plane[c4d.CONSTRUCTIONPLANE_TYPE] = axis
            plane[c4d.CONSTRUCTIONPLANE_SPACING] = 10
        elif plane_type == c4d.Oplane:
            plane[c4d.PRIM_AXIS] = axis
        else:
            if DEBUG: print("Unknown plane type: %r" % plane_type)
            return False
    
        if DEBUG: print("snap target newmg = %r" % new_mg)
        plane.SetMg(new_mg)
    
        SetGlobalRotation(plane, rot)
    
        plane.Message(c4d.MSG_UPDATE)
        return plane
    
    def Command(self, id, msg):
        
        doc = documents.GetActiveDocument()
        if not doc: return False
                
        if id == IDC_BUTTON_DOIT:
            
            op = doc.GetActiveObject()
            if op is None: 
                return False
            
            self.mode = self.GetLong(IDC_COMBO_MODE)
            scriptvars = {
                'mode': self.mode,
                'target': self.target,
            }
            script = PlaneProjectorScript(scriptvars, dialog=self)
            if DEBUG:
                print("do it: %r" % msg)
                print("script = %r" % script)
                print("scriptvars = %r" % scriptvars)
            try:
                c4d.StatusSetSpin()
                result = script.run()
            finally:
                c4d.StatusClear()
            return result
            
        elif id == IDC_BUTTON_CANCEL:
            
            if DEBUG:
                print("cancel: %r" % msg)
            c4d.StatusClear()
            self.Close()
            
        elif id == IDC_BUTTON_GETOBJ:
            
            op = doc.GetActiveObject()
            if op is None: 
                return False
            typ = op.GetType()
            
            if typ == c4d.Oconplane or typ == c4d.Oplane:
                self.SetTarget(op)
            elif typ == c4d.Opolygon:
                # if three points are selected on a polygon object
                # we can create a construction plane oriented to the
                # surface normal of a plane going through all three points.
                # that way the user can select three points on another
                # object and get a plane as target when the get object
                # button is pressed                
                allpoints = op.GetAllPoints()
                pointsel = op.GetPointS()
                
                points = []
                pidx_lst = []
                for i, point in enumerate(allpoints):
                    # calc average vertex normal
                    if pointsel.IsSelected(i):
                        points.append(point)
                        p_idx.append(i)
                
                if len(points) == 3:
                    plane = self.CreatePlane(op, c4d.Oconplane, pidx_lst)                    
                    self.SetTarget(plane)
                
        elif id == IDC_COMBO_MODE:
            
            self.EnableManual(False)
            val = self.GetLong(IDC_COMBO_MODE)
            
            if val == ID_MODE_NORMAL:
                
                # NORMAL
                op = doc.GetActiveObject()
                if op is None: return False
                
                typ = op.GetType()
                if typ == c4d.PolygonObject or typ == c4d.PointObject:
                    
                    N = CalcAverageVertexNormal(op)
                    
                    self.SetReal(IDC_EDIT_X, Deg(N.x))
                    self.SetReal(IDC_EDIT_Y, Deg(N.y))
                    self.SetReal(IDC_EDIT_Z, Deg(N.z))
                    
                    c4d.EventAdd()
                    
            elif val == ID_MODE_MANUAL:
                
                # MANUAL
                self.EnableManual(True)
                
            elif val == ID_MODE_X or val == ID_MODE_LOCAL_X:
                # X
                # self.SetDegree(IDC_EDIT_X, Rad(90.0))
                # self.SetDegree(IDC_EDIT_Y,  0.0)
                # self.SetDegree(IDC_EDIT_Z,  0.0)
                pass
            elif val == ID_MODE_Y or val == ID_MODE_LOCAL_Y:
                # Y
                # self.SetDegree(IDC_EDIT_X,  0.0)
                # self.SetDegree(IDC_EDIT_Y, Rad(90.0))
                # self.SetDegree(IDC_EDIT_Z,  0.0)
                pass
            elif val == ID_MODE_Z or val == ID_MODE_LOCAL_Z:
                # Z
                # self.SetDegree(IDC_EDIT_X,  0.0)
                # self.SetDegree(IDC_EDIT_Y,  0.0)
                # self.SetDegree(IDC_EDIT_Z, Rad(90.0))
                pass
            else:
                # shouldn't happen
                raise ValueError("Combo box value range error")
        elif id == IDC_MENU_ABOUT:
            c4d.gui.MessageDialog(PLUGIN_ABOUT)
        else:
            if DEBUG:
                print("id = %s" % id)
        
        c4d.EventAdd()
        return True
    


# ------------------------------------------------------
#                   Command Script 
# ------------------------------------------------------

class PlaneProjectorScript(object):
    """Run when the user clicks the OK button."""
    def __init__(self, scriptvars=None, dialog=None):
        super(PlaneProjectorScript, self).__init__()
        self.data = scriptvars
        self.dialog = dialog
    
    def run(self):
        if not PY4DLIB_FOUND:
            c4d.gui.MessageDialog(PY4DLIB_NOT_FOUND_MSG)
            return False
        
        try:
            target = self.data['target']
            mode = self.data['mode']
        except:
            return False
             
        if target is None or target == -1:
            return False
        
        # very important!
        c4d.StopAllThreads()
        timestart = c4d.GeGetMilliSeconds()
        
        N = VNULL
        tmg = target.GetMg()
                
        upaxis = self.dialog.GetLong(IDC_COMBO_UPAXIS)
        
        if DEBUG:
            print("target = %r" % target)
            print("mode = %r" % mode)
            print("upaxis = %r" % upaxis)
        
        if upaxis == ID_UPAXIS_X:
            tnorm = tmg.v1
        elif upaxis == ID_UPAXIS_Y:
            tnorm = tmg.v2
        else:  # upaxis == ID_UPAXIS_Z
            tnorm = tmg.v3
        
        local_dir = False
        
        if mode == ID_MODE_MANUAL:
            
            N.x = self.dialog.GetReal(IDC_EDIT_X)
            N.y = self.dialog.GetReal(IDC_EDIT_Y)
            N.z = self.dialog.GetReal(IDC_EDIT_Z)
            
            if DEBUG: 
                print("ID_MODE_MANUAL: N = %r" % N)
                
            #N.Normalize()
            
        elif mode == ID_MODE_X:
            N = VX            
        elif mode == ID_MODE_Y:
            N = VY            
        elif mode == ID_MODE_Z:
            N = VZ
        elif mode == ID_MODE_LOCAL_X:
            N = VX
            local_dir = True
        elif mode == ID_MODE_LOCAL_Y:
            N = VY
            local_dir = True
        elif mode == ID_MODE_LOCAL_Z:
            N = VZ
            local_dir = True

        if DEBUG:
            print("target = %r" % target)
            print("mode = %r" % mode)
            print("upaxis = %r" % upaxis)
            print("local_dir = %r" % local_dir)

        doc = documents.GetActiveDocument()
        if doc is None: return False
        
        doc.StartUndo()
        
        sel = doc.GetSelection()
        if sel is None: return False

        # loop through all objects
        for op in sel:
            if op.GetType() != c4d.Opolygon:
                continue
            
            if mode == ID_MODE_NORMAL:
                # calc vertex normal average of selection
                N = CalcAverageVertexNormal(op)
            
            if IsZeroVector(N):
                if DEBUG: print("N is a zero vector. Skipping...")
                continue
            
            mg = op.GetMg()
            ml = op.GetMl()
            rot = op.GetRelRot()
            rotm = HPBToMatrix(rot)
    
            allpoints = op.GetAllPoints()
            pointsel = op.GetPointS()
            pointselcnt = pointsel.GetCount()
            
            if DEBUG: 
                print("# of selected points = %s" % pointselcnt)
            
            points = []
            for i, point in enumerate(allpoints):
                if pointsel.IsSelected(i):
                    points.append((i, point))
            
            if len(points) == 0:
                continue
            
            # Convert the intersection ray direction to world orientation
            # by multiplying with the inverse of the obj's rotation matrix.
            # The averaged vertex normal already has taken the object's local
            # rotation into account since it was calculated from the orientation
            # of all surrounding polygons.
            if (local_dir is False and (mode != ID_MODE_NORMAL or mode != ID_MODE_MANUAL)):
                N = N ^ ~rotm    
                    
            # Don't forget that v * m converts spatial coordinate points 
            # and v ^ m converts direction/orientation vectors...
            plane = Plane(tmg.off * ~mg, tnorm ^ ~mg)
    
            if DEBUG:
                print("tnorm = %r" % (tnorm))
                print("N = %r" % (N))
                print("plane = %r" % (plane))
    
            for i, point in points:
    
                side = plane.PointResidence(point)
                                        
                if mode != ID_MODE_MANUAL:
                    if side > 0:
                        # if our point is on the "back" side of
                        # the target plane, we need to reverse
                        # the projection direction
                        N = -N
                
                isect = plane.LineIntersection(point, N)
                if isect is None:
                    if DEBUG: print("No intersection. Skipping...")
                    continue
    
                dist = (point - isect).GetLength()
    
                if DEBUG: 
                    print("side = %r" % plane.SideAsString(side))
                    print("isect = %r" % isect)
                    print("dist = %r" % (dist))
                
                doc.AddUndo(c4d.UNDOTYPE_CHANGE, op)
                
                op.SetPoint(i, isect)
                op.Message(c4d.MSG_UPDATE)
        
        c4d.StatusClear()
        
        # tell C4D to update internal state  
        doc.EndUndo()
        c4d.EventAdd() 
        
        timeend = int(c4d.GeGetMilliSeconds() - timestart)
        timemsg = "PlaneProjector: finished in " + str(timeend) + " milliseconds"
        print(timemsg)
        
        return True
    

# ----------------------------------------------------
#                      Main 
# ----------------------------------------------------

class PlaneProjectorMain(plugins.CommandData):
    dialog = None
    def Execute(self, doc):
        # create the dialog
        if self.dialog is None:
            self.dialog = PlaneProjectorDialog()
        return self.dialog.Open(c4d.DLG_TYPE_ASYNC, pluginid=ID_PLANEPROJECTOR)
    
    def RestoreLayout(self, secref):
        # manage nonmodal dialog
        if self.dialog is None:
            self.dialog = PlaneProjectorDialog()
        return self.dialog.Restore(pluginid=ID_PLANEPROJECTOR, secret=secref)
    


if __name__ == "__main__":
    thispath = os.path.dirname(os.path.abspath(__file__))
    icon = bitmaps.BaseBitmap()
    icon.InitWith(os.path.join(thispath, "res", "icon.png"))
    plugins.RegisterCommandPlugin(
        ID_PLANEPROJECTOR, 
        PLUGIN_NAME, 
        0, 
        icon, 
        PLUGIN_HELP, 
        PlaneProjectorMain()
    )
    print("%s v%s loaded. (C) %s Andre Berg" % (PLUGIN_NAME, PLUGIN_VERSION, CR_YEAR))


# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
