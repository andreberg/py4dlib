# -*- coding: utf-8  -*-
# 
#  PlaneProjector.pyp
#  py4dlib.examples
#  
#  Created by André Berg on 2011-03-30.
#  Copyright 2013 Berg Media. All rights reserved.
#  
#  Version 1.2
#  Updated: 2013-08-04
#
#  andre.bergmedia@googlemail.com
#  
#  PlaneProjector
#  
#  Project selected points along a direction vector onto a planar target.
#
#  Summary:
#  
#  Can snap any number of points onto planar targets along local or global X, Y, Z, a manual
#  direction or the averaged vertex normals (basically the direction of the modelling tool's
#  Normal setting for a group of selected points).
#  
#  Currently needs a working plane object as a target object. You can create a new working
#  plane yourself and pick it up to be the target by pressing the pick target button (<) or
#  you can select any number of polygons on any number of polygon objects and hit one of the 
#  Create buttons to create a new plane or workplane aligned to the polygons.
#  
#  As a future improvement it shouldn't be hard at all to use polygons of other objects as
#  planar targets. 
#
# pylint: disable-msg=F0401,E1101,W0232

"""
Name-US:Plane Projector
Description-US:Project selected points along a direction vector onto a planar target.
"""

import os
import sys
import time
import math
import random

__version__ = (1, 2)
__date__ = '2011-03-30'
__updated__ = '2013-08-10'

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
    from py4dlib.maths import Plane, IsZeroVector, VAbsMax, BuildMatrix3
    from py4dlib.objects import FindObjects, CreateObject, UniqueSequentialName
    from py4dlib.mesh import CalcAverageVertexNormal, CalcPolyNormal, CalcPolyCentroid
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
C4D_VERSION = c4d.GetC4DVersion()

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

Set the Target Up Axis to the basis component that is
pointing away from the planar surface. E.g. for a new
workplane object with type XZ this would be the Y-axis.

You can also select any number of polygons on any 
number of polygon objects and hit one of the Create 
buttons to create a new plane or workplane aligned to 
the polygons.

In R14 the workplane button aligns the workplane mode
to the selection instead of creating a workplane object.  

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
IDD_DIALOG_SETTINGS = 10001
IDC_GROUP_WRAPPER   = 10002
IDC_GROUP_SETTINGS  = 10003
IDC_STATIC_TARGET   = 10004
IDC_EDIT_TARGET     = 10005
IDC_BUTTON_GETOBJ   = 10006
IDC_STATIC_UPAXIS   = 10007
IDC_COMBO_UPAXIS    = 10008
IDC_BUTTON_PLANE    = 10009
IDC_BUTTON_WPLANE   = 10010
IDC_GROUP_SETTINGS2 = 10011
IDC_STATIC_MODE     = 10012
IDC_COMBO_MODE      = 10013
IDC_GROUP_SETTINGS3 = 10014
IDC_STATIC_MANUAL   = 10015
IDC_GROUP_MANUAL    = 10016
IDC_EDIT_X          = 10017
IDC_EDIT_Y          = 10018
IDC_EDIT_Z          = 10019
IDC_GROUP_BUTTONS   = 10020
IDC_BUTTON_CANCEL   = 10021
IDC_BUTTON_DOIT     = 10022
IDC_DUMMY           = 10023
IDC_MENU_ABOUT      = 30001

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
    target_ip = 0
    plane = None
    
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
                target_ip = self.target_ip
                objs = FindObjects(target_name, target_ip)
                if len(objs) == 0:
                    # our target object is no longer available in the document? 
                    self.RemoveTarget()
                    return True
        return True
    
    def SetTarget(self, op):
        op_name = op.GetName()
        op_ip = op.GetUniqueIP()
        if op_name == self.target_name and op_ip == self.target_ip:
            if DEBUG:
                print("Reusing same target with IP %d" % self.target_ip)
            return
        elif self.target is not None and self.target_ip != 0:
            # replace old target
            self.RemoveTarget()
        c4d.EventAdd()
        new_ip = self.target_ip
        while new_ip == self.target_ip:
            new_ip = random.randint(1, 999)
        self.target_ip = new_ip
        op.SetUniqueIP(self.target_ip)
        self.target = op
        self.target_name = op_name
        if DEBUG:
            print("Setting target %s (%r) with IP %d" % (self.target_name, self.target, self.target_ip))
        self.SetString(IDC_EDIT_TARGET, self.target_name)
    
    def RemoveTarget(self):
        if DEBUG:
            print("Removing target %s (%r) with IP %d" % (self.target_name, self.target, self.target_ip))
        self.target_ip = 0
        self.target.SetUniqueIP(0)
        self.target_name = None
        self.target = None
        self.SetString(IDC_EDIT_TARGET, "")
    
    def CreateOPlanesFromPolygons(self, op, typ):
        
        if not isinstance(op, c4d.PolygonObject):
            raise TypeError("E: expected c4d.PolygonObject, got %r" % (type(op)))
            
        polysel = op.GetPolygonS()
        allpnts = op.GetAllPoints()
        allpolys = op.GetAllPolygons()
    
        selpolys = []
        for i, p in enumerate(allpolys):
            if polysel.IsSelected(i) == True:
                selpolys.append((i, p))
       
        if len(selpolys) == 0:
            c4d.gui.MessageDialog("please select at least 1 polygon on the target object")
            return False
        
        mg = op.GetMg()
        op_name = op.GetName()
    
        planes = []
    
        for i, p in selpolys:
        
            pids = [p.a, p.b, p.c]
            
            p1 = p.a
            p2 = p.b
            p3 = p.c
            p4 = p.d
            
            plen = 3
            if p.c != p.d: 
                pids.append(p4)
                plen = 4
        
            allp = op.GetAllPoints()
                
            pnts = []
            for id_ in pids:
                pnts.append(allp[id_])
        
            a = allp[p1]
            b = allp[p2]
            c = allp[p3]
            d = allp[p4]
        
            cv1 = a - b
            cv2 = b - c
            cv3 = c - d
            cv4 = d - a
            if plen == 4:
                cva = (cv3 - cv1)
                cvb = (cv4 - cv2)
            else:
                cva = cv3 - cv1
                cvb = cv3 - cv2
        
            if DEBUG:
                print("%d: a = %r, b = %r, c = %r, d = %r" % (i, a,b,c,d))
                print("cv1 = %r" % cv1)
                print("cv2 = %r" % cv2)
                print("cv3 = %r" % cv3)
                print("cv4 = %r" % cv4)
                print("cva = %r" % cva)
                print("cvb = %r" % cvb)
        
            pn = CalcPolyNormal(p, op)
            pc = CalcPolyCentroid(pids, op)
            
            AXIS_ZY = 1
        
            base = "x"
            axis = AXIS_ZY
    
            if plen == 4:
                cv = c4d.Vector(cva.x, cvb.y/2, cva.z)
            else:
                if cvb.y == 0:
                    cv = cvb
                else:
                    cv = cva
    
            if IsZeroVector(cv):
                if cv == cva:
                    cv = cvb
                else:
                    cv = cva
            
            cv ^=  mg
        
            if DEBUG:
                #print("vmax = %r" % vmax)
                print("pn = %r" % pn)
                print("cv = %r" % cv)
                print("base = %r" % base)
            
            plane_mg = BuildMatrix3(pn ^ mg, cv, off=(pc * mg), base=base)
            #plane_mg.v2 = -plane_mg.v2
        
            if typ == "workplane_mode":
                # Python access to the new snapping modes
                # including the internal workplane starts
                # from R14.034. For R14.000 - R14.034 we
                # can only create a normal plane unfortunately.
                try:
                    from c4d.modules import snap
                except ImportError:
                    typ = "plane"
            if typ == "workplane":
                plane = CreateObject(c4d.Oconplane, "%s Workplane %d" % (op_name, i))
                if plane is None:
                    return False
                plane[c4d.CONSTRUCTIONPLANE_TYPE] = axis
                plane[c4d.CONSTRUCTIONPLANE_SPACING] = 10
            elif typ == "workplane_mode":
                doc = op.GetDocument()
                if doc is None:
                    doc = c4d.documents.GetActiveDocument()
                    if doc is None:
                        return 
                c4d.CallCommand(431000009)  # Align Workplane To Selection
                wpobj = snap.GetWorkplaneObject(doc)
                if not snap.IsWorkplaneLock(doc):
                    snap.SetWorkplaneLock(doc.GetActiveBaseDraw(), True)
                plane = wpobj
            elif typ == "plane":
                plane = CreateObject(c4d.Oplane, "%s Plane %d" % (op_name, i))
                if plane is None:
                    return False
                w = h = 100
                plane[c4d.PRIM_AXIS] = axis
                plane[c4d.PRIM_PLANE_WIDTH] = w
                plane[c4d.PRIM_PLANE_HEIGHT] = h
            else:
                if DEBUG: 
                    print("Unknown plane type: %r" % typ)
                return False
            
            if typ != "workplane_mode":
                plane.SetMg(plane_mg)
            
            plane.Message(c4d.MSG_UPDATE)
            planes.append(plane)
            
        return planes

        
    def CreatePlaneForObject(self, op):
        
        if not isinstance(op, c4d.BaseObject):
            raise TypeError("E: expected c4d.BaseObject, got %r" % (type(op)))
        
        n = op.GetRelRot()
        pos = op.GetMg().off
        plane = Plane(pos, n)
        
        return plane
    
    def Command(self, id, msg):
        
        doc = documents.GetActiveDocument()
        if not doc: return False

        op = doc.GetActiveObject()
        sel = doc.GetSelection()
         
        if id == IDC_BUTTON_DOIT:
            
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
            
        elif id == IDC_BUTTON_PLANE:

            if sel is None: 
                return False
            
            for op in sel:
                if DEBUG:
                    print("creating plane for object %s" % op.GetName())
                
                self.CreateOPlanesFromPolygons(op, "plane")
            
        elif id == IDC_BUTTON_WPLANE:
            
            if sel is None: 
                return False
            
            if C4D_VERSION > 14000 and C4D_VERSION < 14034:
                typ = "plane"
            elif C4D_VERSION >= 14034:
                typ = "workplane_mode"
            else:
                typ = "workplane"

            for op in sel:
                if DEBUG:
                    print("creating workplane for object %s" % op.GetName())

                self.CreateOPlanesFromPolygons(op, typ)
            
        elif id == IDC_BUTTON_GETOBJ:
            
            if op is None: 
                return False
            
            typ = op.GetType()
            
            valid_types = [c4d.Opolygon, c4d.Oplane]
            if C4D_VERSION < 14000:
                valid_types.append(c4d.Oconplane)
            
            if typ in valid_types:
                self.SetTarget(op)
        
        elif id == IDC_EDIT_TARGET:
            
            curstr = self.GetString(IDC_EDIT_TARGET)
            
            if len(curstr) == 0:
                if self.target is not None and self.target_ip != 0:
                    self.RemoveTarget()
            
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
        
        plane = self.dialog.CreatePlaneForObject(target)
                
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
