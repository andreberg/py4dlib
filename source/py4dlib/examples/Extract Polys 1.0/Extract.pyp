# -*- coding: utf-8 -*-
# 
#  Extract.pyp
#  py4dlib.examples
#  
#  Created by André Berg on 2013-08-02.
#  Copyright 2013 Berg Media. All rights reserved.
#
#  andre.bergmedia@googlemail.com
# 
# pylint: disable-msg=F0401,E1101,W0232

'''
Extract -- extracts selected polygons into a new polygon object. 

Summary:
 
Same as selecting polygons on some objects, 
running Split, then deleting the inverse 
selection to keep only the selected polys.
'''

import os
import time

__all__ = []
__version__ = (1, 0)
__date__ = '2013-08-02'
__updated__ = '2013-08-02'


DEBUG = 0 or ('DebugLevel' in os.environ and os.environ['DebugLevel'] > 0)
TESTRUN = 0 or ('TestRunLevel' in os.environ and os.environ['TestRunLevel'] > 0)

PY4DLIB_FOUND = False

if DEBUG:
    import pprint
    pp = pprint.PrettyPrinter(width=200)
    PP = pp.pprint
    PF = pp.pformat

try:
    import c4d  #@UnresolvedImport
    from c4d import plugins, bitmaps, gui, documents
except ImportError:
    if TESTRUN == 1:
        pass

try:
    from py4dlib.objects import DeselectAll, Select, GetGlobalRotation
    from py4dlib.objects import SetGlobalRotation, SetAxisRotation
    from py4dlib.objects import SelectObjects, InsertUnderNull
    from py4dlib.mesh import TogglePolySelection, GetSelectedPolys
    PY4DLIB_FOUND = True
except ImportError:
    pass


# ----------------------------------------------
#                   GLOBALS 
# ----------------------------------------------

CR_YEAR = time.strftime("%Y")

PLUGIN_VERSION = '.'.join(str(x) for x in __version__)
PLUGIN_NAME = "Extract"
PLUGIN_HELP = "Extracts polygon selections from a model, where contiguous surfaces are scattered over multiple polygon objects."
PLUGIN_ABOUT   = """(C) %s Andre Berg (Berg Media)
All rights reserved.

Version %s

Same as selecting polygons on some objects,
running Split, then deleting the inverse
selection to keep only the selected polys.
Plus a few extras. Works with multiple object
selections.

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
ID_EXTRACT = 1026898

# Element IDs
IDD_DIALOG_SETTINGS      = 10001
IDC_BUTTON_CANCEL        = 10002
IDC_BUTTON_DOIT          = 10003
IDC_GROUP_WRAPPER        = 10004
IDC_GROUP_SETTINGS       = 10005
IDC_GROUP_BUTTONS        = 10006
IDC_DUMMY                = 10007
IDC_CHK_OPTIMIZE         = 10008
IDC_CHK_CENTER           = 10009
IDC_CHK_KEEPNORMALTAG    = 10010
IDC_CHK_HIDE             = 10011
IDC_CHK_DELETEORIG       = 10012
IDC_CHK_RENORMALIZE      = 10013
IDC_MENU_ABOUT           = 30001

# String IDs
IDS_DIALOG_TITLE   = PLUGIN_NAME
IDS_MENU_INFO      = "Info"
IDS_MENU_ABOUT     = "About..."


# ------------------------------------------------------
#                   User Interface 
# ------------------------------------------------------

class ExtractDialog(gui.GeDialog):
    
    def CreateLayout(self):        
        plugins.GeResource().Init(os.path.dirname(os.path.abspath(__file__)))
        self.LoadDialogResource(IDD_DIALOG_SETTINGS, flags=c4d.BFH_SCALEFIT)
                
        # Menu
        self.MenuFlushAll()
        self.MenuSubBegin(IDS_MENU_INFO)
        self.MenuAddString(IDC_MENU_ABOUT, IDS_MENU_ABOUT)
        self.MenuSubEnd()
        
        self.MenuFinished()
        
        self.SetTitle(IDS_DIALOG_TITLE)
        
        return True
    
    def InitValues(self):
        deleteorig = False
        keepnormal = False
        self.SetBool(IDC_CHK_OPTIMIZE, True)
        self.SetBool(IDC_CHK_CENTER, True)
        self.SetBool(IDC_CHK_DELETEORIG, deleteorig)
        self.SetBool(IDC_CHK_HIDE, False)
        self.SetBool(IDC_CHK_KEEPNORMALTAG, keepnormal)
        self.SetBool(IDC_CHK_RENORMALIZE, False)
        
        self.Enable(IDC_CHK_RENORMALIZE, keepnormal)
        self.Enable(IDC_CHK_HIDE, deleteorig)
        return True
    
    def Disable(self, ID):
        return self.Enable(ID, False)
    
    def Command(self, ID, msg):
        if ID == IDC_BUTTON_DOIT:
            scriptvars = {
                'optimize': self.GetBool(IDC_CHK_OPTIMIZE), 
                'nodelete': self.GetBool(IDC_CHK_HIDE), 
                'centeraxis': self.GetBool(IDC_CHK_CENTER),
                'keepnormaltags': self.GetBool(IDC_CHK_KEEPNORMALTAG),
                'renormalize': self.GetBool(IDC_CHK_RENORMALIZE),
                'deleteorig': self.GetBool(IDC_CHK_DELETEORIG)
            }
            script = ExtractScript(scriptvars)
            if DEBUG:
                print("do it: %r" % msg)
                print("script = %r" % script)
                print("scriptvars = %r" % scriptvars)
            try:
                return script.run()
            except Exception as e:
                if DEBUG or TESTRUN:
                    print(e)
            finally:
                c4d.StatusClear()
        elif ID == IDC_BUTTON_CANCEL:
            if DEBUG:
                print("cancel: %r" % msg)
            self.Close()
        elif ID == IDC_MENU_ABOUT:
            c4d.gui.MessageDialog(PLUGIN_ABOUT)
        elif ID == IDC_CHK_DELETEORIG:
            self.Enable(IDC_CHK_HIDE, (self.GetBool(IDC_CHK_DELETEORIG)))
        elif ID == IDC_CHK_KEEPNORMALTAG:
            self.Enable(IDC_CHK_RENORMALIZE, self.GetBool(IDC_CHK_KEEPNORMALTAG))
        else:
            if DEBUG:
                print("ID = %s" % ID)
        
        return True
    


# ------------------------------------------------------
#                   Command Script 
# ------------------------------------------------------

class ExtractScript(object):
    
    def __init__(self, scriptvars=None):
        super(ExtractScript, self).__init__()
        self.data = scriptvars
    
    def hideDelete(self, objs, doc):
        # Hide/Delete
        if objs is None:
            raise ValueError("objs can't be None")
        if not isinstance(objs, list):
            objs = [objs]
        settings = c4d.BaseContainer()
        if self.data['nodelete'] == True:
            kmd = c4d.MCOMMAND_HIDESELECTED
            verb = "hide selected"      
        else:
            for obj in objs:
                doc.AddUndo(c4d.UNDOTYPE_CHANGE, obj)
            kmd = c4d.MCOMMAND_DELETE
            verb = "delete"
        retval = c4d.utils.SendModelingCommand(
            command=kmd, list=objs, 
            mode=c4d.MODIFY_POLYGONSELECTION, 
            bc=settings, doc=doc
        )
        if DEBUG:
            if retval is False: 
                print("%s failed." % verb)
            elif retval is True: 
                print("%s successful." % verb)  
        return retval
    
    def run(self):
        if not PY4DLIB_FOUND:
            c4d.gui.MessageDialog(PY4DLIB_NOT_FOUND_MSG)
            return False
        
        doc = documents.GetActiveDocument()
        doc.StartUndo()
        
        sel = doc.GetSelection()
        if sel is None or len(sel) == 0: 
            return False
        
        for op in sel:
            if not isinstance(op, c4d.PolygonObject):
                c4d.gui.MessageDialog("Please make sure your selection includes polygon objects only.")
                return False 
        
        c4d.StatusSetSpin()
        timestart = c4d.GeGetMilliSeconds()
        
        grps = []
        cpys = []
        i = 0   # IGNORE:W0612
        
        c4d.StopAllThreads()
        DeselectAll(True)
        
        # loop through all objects
        for op in sel:
            polysel = GetSelectedPolys(op)
            if len(polysel) == 0:
                print("skipping %s because no polygon selection" % op.GetName())
                continue
            
            cpy = op.GetClone()
            doc.AddUndo(c4d.UNDOTYPE_NEW, cpy)
            doc.InsertObject(cpy)
            cpys.append(cpy)
            
            if self.data['deleteorig']:
                self.hideDelete(op, doc)
                
            Select(cpy)
            
            # unfortunately we need to kill the normal tags
            # since the points get shuffled
            if self.data['keepnormaltags'] == False:
                cpy.KillTag(c4d.Tnormal)
            
            # now deselect selected poly and select unselected
            TogglePolySelection(cpy)
            modobjs = []
            
            retval = self.hideDelete([cpy], doc)
            if isinstance(retval, list):    
                modobjs.extend(retval)
            elif isinstance(retval, c4d.BaseObject):
                modobjs.append(retval)
            elif retval is False:
                return False
            
            # Optimize Unused Points
            settings = c4d.BaseContainer()
            if self.data['optimize'] == True:
                settings[c4d.MDATA_OPTIMIZE_TOLERANCE] = 0.1
                settings[c4d.MDATA_OPTIMIZE_POINTS] = False
                settings[c4d.MDATA_OPTIMIZE_POLYGONS] = False
                settings[c4d.MDATA_OPTIMIZE_UNUSEDPOINTS] = True
                retval = c4d.utils.SendModelingCommand(
                    command=c4d.MCOMMAND_OPTIMIZE, list=[op, cpy],
                    mode=c4d.MODIFY_POLYGONSELECTION, 
                    bc=settings, doc=doc
                )
                if retval is False:
                    if DEBUG: print("optimize failed")
                    return False
                elif retval is True:
                    if DEBUG: print("optimize successful")
            
            if DEBUG:
                print("modobjs = %r" % modobjs)
            
            # Center cpy axis
            if self.data['centeraxis'] == True:
                c4d.CallCommand(1011982) # center axis to...
                c4d.EventAdd()
            
            i += 1
            DeselectAll(True)
            # end for
        
        if i == 0:
            print("Nothing to do...")
            return False
            
        # Create collecting group
        op = sel[0]
        try:
            parent = op.GetUp()
            parentname = parent.GetName()
            prot = GetGlobalRotation(parent)
        except Exception:  # IGNORE:W0703
            parent = None
            parentname = "Objects"
            prot = c4d.Vector(0,0,0)
        grpname = "Detached %s" % parentname
        
        # get parent pos and rot (if applicable)
        pmg = op.GetUpMg()
        
        # Add cpy to group
        SelectObjects(cpys)
        grp = InsertUnderNull(cpys, grp=None, name=grpname)
        gmg = grp.GetMg()
        
        if DEBUG:
            print("pmg = %r" % pmg)
            print("gmg = %r" % gmg)
        
        # calc current offset to world 0
        # (since our new copies are created 
        # relative to world zero), then add 
        # the difference to pmg and use the 
        # result as new pos for grp
        wdiff = gmg.off - c4d.Vector(0,0,0)
        newoff = pmg.off + wdiff
        gmg.off = newoff
        
        if DEBUG:
            print("wdiff = %r" % wdiff)
            print("newoff = %r" % newoff)
            print("gmg = %r" % gmg)
        
        grp.SetMg(gmg)
        if parent is not None: # if it has a parent
            SetGlobalRotation(grp, prot)
        
        if (self.data['keepnormaltags'] == True and 
            self.data['renormalize'] == True):
            # since CINEMA 4D performs object axis 
            # transform ("Y Up") when importing OBJ files
            # we need to recreate this manually for the 
            # normal data to make sense again, e.g.
            # rotate the object axis by B=90 
            for op in grp.GetChildren():
                if op.GetTag(c4d.Tnormal) is not None:
                    theta = c4d.utils.Rad(90)
                    trot = c4d.Vector(0, 0, theta)
                    SetAxisRotation(op, trot - prot)
        
        if DEBUG:
            print("grp = %r" % grp)
            print("grps = %r" % grps)
            print("cpys = %r" % cpys)
        
        doc.SetMode(c4d.Mmodel)
        
        c4d.StatusClear()
        
        # tell C4D to update internal state  
        c4d.EventAdd()
        doc.EndUndo()
        
        timeend = int(c4d.GeGetMilliSeconds() - timestart)
        timemsg = "Extract: finished in " + str(timeend) + " milliseconds"
        print(timemsg)
        
        return True
    

# ----------------------------------------------------
#                      Main 
# ----------------------------------------------------
class ExtractMain(plugins.CommandData):
    
    dialog = None
    
    def Execute(self, doc):  # IGNORE:W0613
        # create the dialog
        if self.dialog is None:
            self.dialog = ExtractDialog()
        return self.dialog.Open(c4d.DLG_TYPE_ASYNC, pluginid=ID_EXTRACT, defaultw=230)
    
    def RestoreLayout(self, secref):
        # manage nonmodal dialog
        if self.dialog is None:
            self.dialog = ExtractDialog()
        return self.dialog.Restore(pluginid=ID_EXTRACT, secret=secref)
    


if __name__ == "__main__":
    thispath = os.path.dirname(os.path.abspath(__file__))
    icon = bitmaps.BaseBitmap()
    icon.InitWith(os.path.join(thispath, "res/", "icon.tif"))
    plugins.RegisterCommandPlugin(
        ID_EXTRACT, 
        PLUGIN_NAME, 
        0, 
        icon, 
        PLUGIN_HELP, 
        ExtractMain()
    )
    print("%s v%s loaded. (C) %s Andre Berg" % (PLUGIN_NAME, PLUGIN_VERSION, CR_YEAR))


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
