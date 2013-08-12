# -*- coding: UTF-8  -*-
#
#  Regex Renamer.pyp
#  py4dlib.examples
#  
#  Created by Andre Berg on 2011-04-02.
#  Copyright 2013 Berg Media. All rights reserved.
#
#  Version 1.1
#  Updated: 2013-08-12
#
#  andre.bergmedia@googlemail.com
#  
#  RegexRenamer
#  
#  Search for and select/rename objects using Python's powerful re module.
#
#  Summary:
#  
#  Regex Renamer is a command plugin, that allows for utilizing Python's 
#  powerful "re" module to perform regular expression based searching and 
#  replacing within object names.
#
# pylint: disable-msg=F0401,E1101,W0232

"""
Name-US:Regex Renamer
Description-US:Find & Replace object names using Python's powerful re module.
"""

import os
import re
import time

__version__ = (1, 1)
__date__ = '2011-04-02'
__updated__ = '2013-08-13'

DEBUG = 0 or ('DebugLevel' in os.environ and os.environ['DebugLevel'] > 0)
TESTRUN = 0 or ('TestRunLevel' in os.environ and os.environ['TestRunLevel'] > 0)

if DEBUG:
    import pprint
    pp = pprint.PrettyPrinter(width=200)
    PP = pp.pprint
    PF = pp.pformat

try:
    import c4d  #@UnresolvedImport
    from c4d import plugins, bitmaps, gui, documents
    from c4d.utils import *
except ImportError:
    if TESTRUN == 1:
        pass

PY4DLIB_FOUND = False

try:
    from py4dlib.objects import Select, DeselectAll, GetNextObject
    from py4dlib.plugins import UserDefaults
    from py4dlib.utils import EscapeUnicode, UnescapeUnicode
    PY4DLIB_FOUND = True
except ImportError:
    pass

CR_YEAR = time.strftime("%Y")

# -------------------------------------------
#                GLOBALS
# -------------------------------------------

PLUGIN_NAME    = "Regex Renamer"
PLUGIN_VERSION = '.'.join(str(x) for x in __version__)
PLUGIN_HELP    = "Find & Replace object names using Python's powerful re module"
PLUGIN_ABOUT   = """(C) %s Andre Berg (Berg Media)
All rights reserved.

Version %s 

Regex Renamer is a command plugin, that
allows for utilizing Python's powerful "re"
module to perform regular expression based
searching and replacing within object names.

Use at your own risk!

It is recommended to try out the plugin
on a spare copy of your data first.
""" % (CR_YEAR, PLUGIN_VERSION)

IDS_HINT_NONASCII = """There is a special treatment for non-ASCII characters 
like for example German umlauts. CINEMA 4D internally 
they are stored as a \\uXXXX escape sequence and thus 
need to be converted to and from this form. Before this
was done automatically by the plugin you had to 
prepend a single backslash to the higher order ASCII 
character.
"""

IDS_TIPS1 = """If you leave the "Replace with:" field empty, 
matching objects will be selected but no 
name replacement will be performed.
"""

IDS_SETTINGS_PARSE_ERROR_SEARCHREGEX_UNKNOWN = "Parsing 'Search for' failed. The error message was: %s"
IDS_SETTINGS_PARSE_ERROR_REPLACEREGEX_UNKNOWN = "Parsing 'Replace with' failed. The error message was: %s"
IDS_SETTINGS_COMPILE_ERROR_SEARCHREGEX = "Compiling regex in 'Search for' failed. The error message was: %s"
IDS_SETTINGS_PARSE_ERROR_WRONG_SYNTAX = """Please use pure regex syntax only. Term will be wrapped in ur'<term>'."""
IDS_SETTINGS_PARSE_ERROR_BLACKLISTED = "Error: please refrain from using the following words: 'import os', 'removedirs', 'remove', 'rmdir'"


# Defaults

DEFAULT_SETTINGS = {
    'search': r"(.*?)\.(\d)",
    'replace': r"\2-\1",
    'ignorecase': False,
    'multiline': False,
    'dotall': False,
    'verbose': False,
    'selectiononly': False
}

SETTINGS_FILEPATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "res", "settings.ini")

# Try to read existing settings from disk but if none are found,
# apply the defaults dict defined above and create a new setttings 
# file from it. This is run exactly once during CINEMA 4D's launch time.
USER_DEFAULTS = UserDefaults(SETTINGS_FILEPATH, defaults=DEFAULT_SETTINGS)

if DEBUG:
    print("USER_DEFAULTS: %s" % USER_DEFAULTS)


# -------------------------------------------
#               PLUGING IDS
# -------------------------------------------

# unique ID
ID_REGEXRENAMER = 1026925


# Element IDs
IDD_DIALOG_SETTINGS     = 10001
IDC_GROUP_WRAPPER       = 10002
IDC_GROUP_SETTINGS      = 10003
IDC_STATIC_SEARCH       = 10004
IDC_EDIT_SEARCH         = 10005
IDC_STATIC_REPLACE      = 10006
IDC_EDIT_REPLACE        = 10007
IDC_CHECK_IGNORECASE    = 10008
IDC_CHECK_MULTILINE     = 10009
IDC_CHECK_DOTALL        = 10010
IDC_CHECK_VERBOSE       = 10011
IDC_GROUP_SETTINGS2     = 10012
IDC_CHECK_SELECTIONONLY = 10013
IDC_GROUP_BUTTONS       = 10014
IDC_BUTTON_CANCEL       = 10015
IDC_BUTTON_DOIT         = 10016
IDC_DUMMY               = 10017
IDC_MENU_ABOUT          = 30001
IDC_MENU_TUTORIAL       = 30002
IDC_MENU_HINT_NONASCII  = 30003
IDC_MENU_TIPS           = 30004

# String IDs
IDS_DIALOG_TITLE         = PLUGIN_NAME
IDS_MENU_INFO            = "Info"
IDS_MENU_ABOUT           = "About..."
IDS_MENU_TUTORIAL        = "Online tutorial..."
IDS_MENU_HINT_NONASCII   = "Unicode chars..."
IDS_MENU_TIPS            = "Tips..."


# ------------------------------------------------------
#                   User Interface
# ------------------------------------------------------

class RegexRenamerDialog(gui.GeDialog):
    
    def CreateLayout(self):
        self.SetTitle(IDS_DIALOG_TITLE)
        
        plugins.GeResource().Init(os.path.dirname(os.path.abspath(__file__)))
        self.LoadDialogResource(IDD_DIALOG_SETTINGS, flags=c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT)
        
        # Menu
        self.MenuFlushAll()
        self.MenuSubBegin(IDS_MENU_INFO)
        self.MenuAddString(IDC_MENU_ABOUT, IDS_MENU_ABOUT)
        self.MenuAddString(IDC_MENU_TUTORIAL, IDS_MENU_TUTORIAL)
        self.MenuAddString(IDC_MENU_HINT_NONASCII, IDS_MENU_HINT_NONASCII)
        self.MenuAddString(IDC_MENU_TIPS, IDS_MENU_TIPS)
        self.MenuSubEnd()
        
        self.MenuFinished()
        
        return True
    
    def InitValues(self):
        
        global USER_DEFAULTS
        
        if USER_DEFAULTS is None:
            # the config file should always be there because we created it at the top of the script
            # during CINEMA 4D's launch time but just to be safe create it again if the config file 
            # isn't there
            USER_DEFAULTS = UserDefaults(SETTINGS_FILEPATH, defaults=DEFAULT_SETTINGS)

        # read settings            
        searchregex = USER_DEFAULTS.Get("search")
        replaceterm = USER_DEFAULTS.Get("replace")
        ignorecase = USER_DEFAULTS.GetBool("ignorecase")
        multiline = USER_DEFAULTS.GetBool("multiline")
        verbose = USER_DEFAULTS.GetBool("verbose")
        selectiononly = USER_DEFAULTS.GetBool("selectiononly")
        dotall = USER_DEFAULTS.GetBool("dotall")
        
        if DEBUG:
            print("stored search regex = %s" % searchregex)
            print("stored replace term = %s" % replaceterm)
            print("stored ignorecase = %s" % ignorecase)
            print("stored multiline = %s" % multiline)
            print("stored verbose = %s" % verbose)
            print("stored dot all = %s" % dotall)
            print("stored selection only = %s" % selectiononly)
            
        self.SetString(IDC_EDIT_SEARCH, searchregex)
        self.SetString(IDC_EDIT_REPLACE, replaceterm)
        self.SetBool(IDC_CHECK_IGNORECASE, ignorecase)
        self.SetBool(IDC_CHECK_MULTILINE, multiline)
        self.SetBool(IDC_CHECK_VERBOSE, verbose)
        self.SetBool(IDC_CHECK_DOTALL, dotall)
        self.SetBool(IDC_CHECK_SELECTIONONLY, selectiononly)
        if len(replaceterm) > 0:
            self.SetString(IDC_BUTTON_DOIT, "Replace")
        else:
            self.SetString(IDC_BUTTON_DOIT, "Select")
        return True
    
    def Command(self, id, msg):
        
        global USER_DEFAULTS
        
        cursearchregex = self.GetString(IDC_EDIT_SEARCH)
        curreplaceterm = self.GetString(IDC_EDIT_REPLACE)
        multiline = self.GetBool(IDC_CHECK_MULTILINE)
        ignorecase = self.GetBool(IDC_CHECK_IGNORECASE)
        dotall = self.GetBool(IDC_CHECK_DOTALL)
        verbose = self.GetBool(IDC_CHECK_VERBOSE)
        selectiononly = self.GetBool(IDC_CHECK_SELECTIONONLY)
        
        if id == IDC_BUTTON_DOIT:
            
            try:
                # Unescape Unicode in R12 because in R12 expects repr("Würfel") == "W\\\u00FC" 
                # which is a non standard escape sequence, while repr(u"Würfel") == u"W\xfcrfel" (latin-1).
                # In R13 and R14 repr("Würfel") == 'W\xc3\xbcrfel' (utf-8) and 
                # repr(u"Würfel") == 'W\xc3\xbcrfel' (utf-8).
                evalsearchregex = ur"""%s""" % UnescapeUnicode(cursearchregex)
            except Exception, e:
                c4d.gui.MessageDialog(IDS_SETTINGS_PARSE_ERROR_SEARCHREGEX_UNKNOWN % e)
                return False
            try:
                evalreplaceterm = ur"""%s""" % UnescapeUnicode(curreplaceterm)
            except Exception, e:
                c4d.gui.MessageDialog(IDS_SETTINGS_PARSE_ERROR_REPLACEREGEX_UNKNOWN % e)
                return False
            
            scriptvars = {
                'search': evalsearchregex,
                'replace': evalreplaceterm,
                'multiline': multiline,
                'ignorecase': ignorecase,
                'dotall': dotall,
                'verbose': verbose,
                'selectiononly': selectiononly
            }
            script = RegexRenamerScript(scriptvars)
            if DEBUG:
                print("do it: %r" % msg)
                print("script = %r" % script)
                print("scriptvars = %r" % scriptvars)
                
            return script.run()
        
        elif id == IDC_BUTTON_CANCEL:
            
            searchregex = self.GetString(IDC_EDIT_SEARCH)
            replaceterm = self.GetString(IDC_EDIT_REPLACE)
            multiline = self.GetBool(IDC_CHECK_MULTILINE)
            ignorecase = self.GetBool(IDC_CHECK_IGNORECASE)
            dotall = self.GetBool(IDC_CHECK_DOTALL)
            verbose = self.GetBool(IDC_CHECK_VERBOSE)
            selectiononly = self.GetBool(IDC_CHECK_SELECTIONONLY)
            
            if DEBUG:
                print("cancel: %r" % msg)
                print("search: %r" % searchregex)
                print("replace: %r" % replaceterm)
                print("ignorecase: %s" % ignorecase)
                print("multiline: %s" % multiline)
                print("verbose: %s" % verbose)
                print("dot all: %s" % dotall)
                print("selection only: %s" % selectiononly)
                        
            if USER_DEFAULTS is not None:
                USER_DEFAULTS.Set("search", searchregex)
                USER_DEFAULTS.Set("replace", replaceterm)
                USER_DEFAULTS.Set("ignorecase", ignorecase)
                USER_DEFAULTS.Set("multiline", multiline)
                USER_DEFAULTS.Set("verbose", verbose)
                USER_DEFAULTS.Set("dotall", dotall)
                USER_DEFAULTS.Set("selectiononly", selectiononly)
                USER_DEFAULTS.Save()
                
            self.Close()
        
        elif id == IDC_EDIT_REPLACE:
            
            replaceterm = self.GetString(IDC_EDIT_REPLACE)
            if len(replaceterm) > 0:
                self.SetString(IDC_BUTTON_DOIT, "Replace")
            else:
                self.SetString(IDC_BUTTON_DOIT, "Select")
                    
        elif id == IDC_MENU_ABOUT:
            
            c4d.gui.MessageDialog(PLUGIN_ABOUT)
        
        elif id == IDC_MENU_TUTORIAL:
            
            thispath = os.path.dirname(os.path.abspath(__file__))
            tutorialfile = os.path.join(thispath, "res", "tutorial.html")
            c4d.storage.GeExecuteFile(tutorialfile)
        
        elif id == IDC_MENU_HINT_NONASCII:
            
            c4d.gui.MessageDialog(IDS_HINT_NONASCII)
        
        elif id == IDC_MENU_TIPS:
            
            c4d.gui.MessageDialog(IDS_TIPS1)
            
        else:
            if DEBUG:
                print("id = %s" % id)
        
        return True
    


# ------------------------------------------------------
#                   Command Script
# ------------------------------------------------------

class RegexRenamerScript(object):
    """Run when the user clicks the OK button."""
    def __init__(self, scriptvars=None):
        super(RegexRenamerScript, self).__init__()
        self.data = scriptvars
    
    def run(self):
        if not PY4DLIB_FOUND:
            c4d.gui.MessageDialog(PY4DLIB_NOT_FOUND_MSG)
            return False
        
        doc = documents.GetActiveDocument()
        if doc is None: return False
        
        doc.StartUndo()
                        
        searchregex = self.data['search']
        replaceterm = self.data['replace']
        ignorecase = self.data['ignorecase']
        multiline = self.data['multiline']
        verbose = self.data['verbose']
        dotall = self.data['dotall']
        selectiononly = self.data['selectiononly']
        
        flags = re.UNICODE
        if ignorecase is True:
            flags = flags | re.IGNORECASE
        if multiline is True:
            flags = flags | re.MULTILINE
        if verbose is True:
            flags = flags | re.VERBOSE
        if dotall is True:
            flags = flags | re.DOTALL
        
        try:
            pat = re.compile(searchregex, flags)
        except Exception, e:
            c4d.gui.MessageDialog(IDS_SETTINGS_COMPILE_ERROR_SEARCHREGEX % e)
            return False
                
        c4d.StopAllThreads()
                
        c4d.StatusSetSpin()
        timestart = c4d.GeGetMilliSeconds()
        
        if selectiononly:
            sel = doc.GetSelection()
            if sel is None or len(sel) == 0: return False
            DeselectAll(True)
            for op in sel:
                curname = UnescapeUnicode(op.GetName())
                if DEBUG: 
                    print("processing %r (%r)" % (curname, op))
                    print("searchregex = %r, curname = %r" % (searchregex, curname))
                if re.search(pat, curname):
                    doc.AddUndo(c4d.UNDOTYPE_CHANGE, op)
                    Select(op)
                    if len(replaceterm) > 0:
                        newname = re.sub(pat, replaceterm, curname)
                        op.SetName(EscapeUnicode(newname))
                        op.Message(c4d.MSG_UPDATE)
                        c4d.EventAdd()
        else:
            DeselectAll(True)
            op = doc.GetFirstObject()
            while op:
                curname = UnescapeUnicode(op.GetName())
                if DEBUG: 
                    print("processing %r (%r)" % (curname, op))
                    print("searchregex = %r, curname = %r" % (searchregex, curname))
                if re.search(pat, curname):
                    doc.AddUndo(c4d.UNDOTYPE_CHANGE, op)
                    Select(op)
                    if len(replaceterm) > 0:
                        newname = re.sub(pat, replaceterm, curname)
                        op.SetName(EscapeUnicode(newname))
                        op.Message(c4d.MSG_UPDATE)
                        c4d.EventAdd()
                op = GetNextObject(op)
        
        c4d.StatusClear()
        
        # tell C4D to update internal state
        c4d.EventAdd()
        doc.EndUndo()
        
        timeend = int(c4d.GeGetMilliSeconds() - timestart)
        timemsg = "RegexRenamer: finished in " + str(timeend) + " milliseconds"
        print(timemsg)
        
        return True
    

# ----------------------------------------------------
#                      Main
# ----------------------------------------------------

class RegexRenamerMain(plugins.CommandData):
    dialog = None
    def Execute(self, doc):
        # create the dialog
        if self.dialog is None:
            self.dialog = RegexRenamerDialog()
        return self.dialog.Open(c4d.DLG_TYPE_ASYNC, pluginid=ID_REGEXRENAMER, defaultw=355, defaulth=200)
    
    def RestoreLayout(self, secref):
        # manage nonmodal dialog
        if self.dialog is None:
            self.dialog = RegexRenamerDialog()
        return self.dialog.Restore(pluginid=ID_REGEXRENAMER, secret=secref)
    


if __name__ == "__main__":
    thispath = os.path.dirname(os.path.abspath(__file__))
    icon = bitmaps.BaseBitmap()
    icon.InitWith(os.path.join(thispath, "res", "icon.png"))
    plugins.RegisterCommandPlugin(
        ID_REGEXRENAMER,
        PLUGIN_NAME,
        0,
        icon,
        PLUGIN_HELP,
        RegexRenamerMain()
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
