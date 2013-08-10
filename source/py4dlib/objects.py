# -*- coding: utf-8 -*-
# 
#  objects.py
#  py4dlib
#  
#  Created by André Berg on 2012-09-26.
#  Copyright 2012 Berg Media. All rights reserved.
#
#  andre.bergmedia@googlemail.com
# 
# pylint: disable-msg=F0401

'''py4dlib.objects -- components for working with CINEMA 4D's objects.'''

import os
import re

__version__ = (0, 5)
__date__ = '2012-09-27'
__updated__ = '2013-08-10'


DEBUG = 0 or ('DebugLevel' in os.environ and os.environ['DebugLevel'] > 0)
TESTRUN = 0 or ('TestRunLevel' in os.environ and os.environ['TestRunLevel'] > 0)

import pprint

pp = pprint.PrettyPrinter()
PP = pp.pprint
PF = pp.pformat

try:
    import c4d  #@UnresolvedImport
    from c4d import documents  #@UnresolvedImport
except ImportError:
    if TESTRUN == 1:
        pass

from py4dlib.utils import UnescapeUnicode, EscapeUnicode, FuzzyCompareStrings, deprecated
from py4dlib.maths import BBox
from py4dlib.mesh import CalcGravityCenter


class ObjectIterator(object):
    """
    Iterator over specific objects in the object manager tree.
        
    Using a depth first traversal scheme, return a tuple in the form
    (op, lvl), where op is a c4d.BaseObject representing the current 
    object and lvl is an integer indicating the current depth level.
        
    :param start_obj:        the object whose hierarchy should be iterated over
    :param stop_obj:         an object or a list of objects at which traversal 
                            should stop (optional)
    :param children_only:   if True, iterate through the sub-hierarchy under
                            start_obj and stop as soon as start_obj's parent or
                            stop_obj (if given) is reached. This excludes start_obj
                            from the iteration.
    :param startlvl:        base indentation level 
    """
    def __init__(self, start_obj, stop_obj=None, children_only=True, startlvl=-1):
        super(ObjectIterator, self).__init__()
        self.curobj = start_obj
        # determine depth level within the hierarchy of start_obj
        op = start_obj
        while op:
            startlvl += 1
            op = op.GetUp()
        self.curlvl = startlvl
        self.children_only = children_only
        if children_only:
            self.stop_objs = [start_obj]
            self.init = False
        else:
            self.stop_objs = []
            self.init = True
        if stop_obj and isinstance(stop_obj, list):
            self.stop_objs.extend(stop_obj)
        elif stop_obj and isinstance(stop_obj, c4d.BaseObject):
            self.stop_objs.append(stop_obj)
    
    def __iter__(self):
        return self
    
    # next() becomes __next__() in later Pythons
    def next(self):
        op = self.curobj
        if self.init is True:
            self.init = False
            return (self.curobj, self.curlvl)
        if op == None:
            raise StopIteration
        if op.GetDown():
            if op.GetNext() in self.stop_objs or \
               op.GetDown() in self.stop_objs:
                raise StopIteration
            self.curlvl += 1
            self.curobj = op.GetDown()
            return (self.curobj, self.curlvl)
        if op in self.stop_objs:
            raise StopIteration
        if self.stop_objs is None:
            while not op.GetNext() and op.GetUp():
                self.curlvl -= 1
                op = op.GetUp()
        else:
            while not op.GetNext() and op.GetUp():
                if (op in self.stop_objs) or \
                   (op.GetUp() in self.stop_objs):
                    raise StopIteration
                self.curlvl -= 1
                op = op.GetUp()
        if op.GetNext():
            if op.GetNext() in self.stop_objs:
                raise StopIteration
            self.curobj = op.GetNext()
            return (self.curobj, self.curlvl)            
        else:
            raise StopIteration
        return (self.curobj, self.curlvl)


class ObjectEntry(object):
    """
    Wraps ``c4d.BaseObject``s and makes them
    hashable, so they can be used as keys in 
    dictionaries.
    """
    def __init__(self, op, lvl=-1, parents=None):
        """
        :param op: the object to wrap.
        :type op: ``c4d.BaseObject``
        :param lvl: the depth level within the hierarchy.
        :type lvl: ``int``
        :param parents: a list of parent objects
        :type parents: ``list<c4d.BaseObject>``
        """
        super(ObjectEntry, self).__init__()
        self.op = op
        self.name = op.GetName()
        curlvl = lvl
        if curlvl < 0:
            while op:
                curlvl += 1
                op = op.GetUp()
        self.curlvl = curlvl
        self.lvl = curlvl
        self.parents = parents
    def __str__(self):
        return ('%s%s' % 
                (' ' * 4 * self.lvl, self.name))
    def __repr__(self):
        return ("%s (%s)" % 
                (self.name, self.op.GetTypeName()))
    def __hash__(self):
        return hash(self.name) ^ self.lvl
    def __cmp__(self, other):
        try:
            return cmp(self.op, other.op)
        except (AttributeError, TypeError):
            return NotImplemented


class ObjectHierarchy(object):
    """
    Represents a hierarchical group structure in the object manager.
    
    Can be used to create a Pythonic snapshot of the current scene 
    so as to provide easy access to specifc sets of objects.
    
    Starting with root object stores a list of ``c4d.BaseObjects`` 
    for each depth level in a dictionary. Each list is indexed by a 
    concatenation of its parent names. The concat character is a
    forward slash, which forms a Unix like filepath as seen with 
    the object manager's address bar widget.
    
    Additionally, a small subset of X-Path like functionality is 
    provided with the ``get()`` function, namely the subset that
    coincides with syntax for wildcard and regular epxression 
    expansion. This makes it easy to select a subset of objects,
    based on parent-name relationships.
    
    :param filter_type: only recognize objects of this c4d type
    :param bool children_only: see :py:class:`ObjectIterator`
    """
    def __init__(self, root_obj=None, filter_type=None, children_only=False):
        super(ObjectHierarchy, self).__init__()
        if root_obj is None:
            doc = c4d.documents.GetActiveDocument()
            root_obj = doc.GetFirstObject()
            children_only = False
        self.children_only = children_only
        self.root = root_obj
        self.maxlvl = -1
        sep = '/'
        hierarchy = {}
        for op, lvl in ObjectIterator(root_obj, children_only=children_only):
            if ((filter_type is None) or 
                (filter_type and op.GetType() == filter_type)):
                plist = []
                opp = op
                i = lvl  # IGNORE:W0612
                while opp:
                    opp = opp.GetUp()
                    if opp:
                        oppname = opp.GetName()
                        i -= 1
                        pentry = oppname
                        plist.append(pentry)
                if len(plist) == 0:
                    plist.append(op.GetName())
                plist.reverse()
                parent_path = sep.join(plist)
                if parent_path not in hierarchy:
                    hierarchy[parent_path] = []
                hierarchy[parent_path].append(op)
            if lvl > self.maxlvl:
                self.maxlvl = lvl
        self.sep = sep
        self.entries = hierarchy
        
    def _strxform(self):
        result = "{"
        for k, v in self.entries.items():
            result += "%r: [" % k
            for op in v:
                result += "%r, " % op.GetName()
            result = result[:-2] # chop off remainder ","
            result += "], "
        result = result[:-2] # chop off remainder ","
        result += "}"
        return result
            
    def __str__(self):
        return self._strxform()
    
    def __repr__(self):
        return repr(self.entries)
    
    def PPrint(self, stop_obj=None, filter_type=None, tabsize=4):
        """Print an indented, tree-like representation of an object manager hierarchy."""
        lvl = 0
        total = handled = 0
        if stop_obj is None and self.children_only:
            stop_obj = self.root
        for op, lvl in ObjectIterator(self.root, stop_obj, children_only=self.children_only):
            total += 1
            indent = lvl * tabsize * ' '
            if not filter_type or (filter_type and op.GetType() == filter_type):
                handled += 1
                print("%s%s" % (indent, op.GetName()))
        filtered = (total - handled)
        if total == 1:
            s = ""
        else:
            s = "s"
        if filtered > 0:
            fstr = " (%d filtered)" % filtered
        else:
            fstr = ""
        print("processed %d object%s%s" % (handled, s, fstr))
        
    def Get(self, path, strict=True):
        """
        Get a list of ``c4d.BaseObject``s for the key path given by 'path'.
        
        Key path can contain wildcards (``*`` or ``?``) or regular expression
        syntax. Prepend a '!' to 'path' if you want to forego wildcard expansion
        and thus ensure it is used as a verbatim regular expression pattern instead.
        
        Note that if 'strict' is True, 'path' must match the whole key it is 
        tested against. Otherwise it is sufficient if the path is contained by
        the key.
        
        Returns a list of all objects for which 'path', expanded, matched a 
        concatenated parent path. Returns an empty list if no objects could be
        located for 'path'.
        """
        results = []
        try:
            path = UnescapeUnicode(path.strip())
        except UnicodeEncodeError:
            path = path.strip()
        if path[-1] == self.sep:
            path = path[:-1] 
        if '..' in path:
            comps = path.split(self.sep)
            resolved_comps = []
            skip = False
            for comp in reversed(comps):
                if comp == '..':
                    skip = True
                    continue
                if skip:
                    skip = False
                    continue
                resolved_comps.append(comp)
            resolved_comps.reverse()
            path = self.sep.join(resolved_comps)
        if path[0] == '!': 
            # hint to take path as a verbatim re pattern
            pat = path[1:]
        else:
            # wildcard version
            pat = re.escape(path)
            # go back one escape level
            pat = path.replace(r'\\', '\\')
            pat = pat.replace('?', '.').replace('*', '.*?')
        if strict is True:
            pat = '^%s$' % pat
            func = re.match
        else:
            pat = '%s' % pat
            func = re.search
        keys = [key for key in list(self.entries.keys()) if 
                func(pat, UnescapeUnicode(key), flags=re.UNICODE)]
        if DEBUG: 
            print("path = %r" % (path))
            print("pat = %r" % (pat))     
            print("keys = %r" % (keys)) 
        try:
            for key in keys:
                result = self.entries.get(key)
                results.extend(result)
        except KeyError:
            pass
        return results
     
          
def Select(obj):
    if not obj.GetBit(c4d.BIT_ACTIVE):
        obj.ToggleBit(c4d.BIT_ACTIVE)
    return obj.GetBit(c4d.BIT_ACTIVE)


def SelectAdd(obj):
    """ Same as select(obj) but uses a slightly different mechanism.
        See also BaseDocument.SetSelection(sel, mode).
    """
    doc = obj.GetDocument()
    doc.SetActiveObject(obj, c4d.SELECTION_ADD)
    

def SelectGroupMembers(grp):
    doc = documents.GetActiveDocument()
    for obj in grp:
        # add each group member to the selection 
        # so we can group them in the object manager
        #doc.AddUndo(UNDO_BITS, obj)
        doc.SetActiveObject(obj, c4d.SELECTION_ADD)


def SelectObjects(objs):
    for obj in objs:
        Select(obj)
    

def DeselectAll(inObjMngr=False):
    """ Not the same as ``BaseSelect.DeselectAll()``.

       :param bool inObjMngr: if True, run the deselect command for the 
          Object Manager, else the general one for the editor viewport.
    """
    if inObjMngr is True:
        c4d.CallCommand(100004767) # deselect all (Object Manager)
    else:
        c4d.CallCommand(12113) # deselect all


def GroupObjects(objs, name="Group"):
    """ CallCommand based grouping of objects from a list. 
        
    Generally unreliable, because selection state matters.
    Use insertUnderNull for better effect.
    """
    DeselectAll(True)
    result = None
    if objs is None: 
        return result
    if not isinstance(objs, list):
        objs = [objs]
    else:
        return result
    for o in objs:
        Select(o)
    if DEBUG: print("creating group %s" % name)
    c4d.CallCommand(100004772) # group objects
    doc = documents.GetActiveDocument()
    grp = doc.GetActiveObject()
    grp.SetName(name)
    result = grp
    return result


def GroupSelected(name="Group"):
    """ CallCommand based grouping of selected objects. 
        
    Generally unreliable, because selection state matters.
    Use insertUnderNull for better effect.
    """
    if DEBUG: print("creating group %s" % name)
    c4d.CallCommand(100004772)  # group objects
    doc = documents.GetActiveDocument()
    grp = doc.GetActiveObject()
    grp.SetName(name)
    result = grp
    return result


def RecurseBranch(obj):
    child = obj.GetDown()
    while child:
        child = child.GetNext()
        return RecurseBranch(child)
    

def GetNextObject(obj, stop_objs=None):
    """ Return the next object in the hierarchy using a depth-first traversal scheme.
    
    If stop_objs is a c4d.BaseObject or a list of c4d.BaseObjects and the next
    operation would encounter this object (or the first object in the list) None
    will be returned. This is so that this function can be used in a while loop.
    """
    if stop_objs and not isinstance(stop_objs, list):
        stop_objs = [stop_objs]
    elif stop_objs is None:
        stop_objs = []
    if obj == None: return None
    if obj.GetDown(): 
        if (obj.GetNext() in stop_objs or
            obj.GetDown() in stop_objs):
            return None
        return obj.GetDown()
    if obj in stop_objs:
        return None
    if len(stop_objs) == 0:
        while not obj.GetNext() and obj.GetUp():
            obj = obj.GetUp()
    else:
        while (not obj.GetNext() and 
                   obj.GetUp() and 
                   obj.GetUp() not in stop_objs):
            if (obj in stop_objs or
                obj.GetUp() in stop_objs):
                return None
            obj = obj.GetUp()
    if obj.GetNext() and obj.GetNext() in stop_objs:
        return None
    else:
        return obj.GetNext()


def GetActiveObjects(doc):
    """ Same as BaseDocument.GetSelection(), where 
        GetSelection also selects tags and materials. 
    """
    lst = list()
    obj = doc.GetFirstObject()
    while obj:
        if obj.GetBit(c4d.BIT_ACTIVE) == True: 
            lst.append(obj)
        obj = GetNextObject(obj)
    return lst


def FindObject(name, start=None, matchfunc=None, *args, **kwargs):
    """ Find object with name 'name'.
    
    :param start: a c4d.BaseObject or a str representing the name
        of a c4d.BaseObject from where the search should begin.
    :type start: ``c4d.BaseObject``
    :param matchfunc: can be used to customize the matching logic 
        by providing the name of a custom function. This function 
        will be passed a potential candidate object plus any 
        remaining args. It should return True or False.
    :type matchfunc: ``function``
    """
    if name is None: return None
    if not isinstance(name, (str, unicode)):
        raise TypeError("E: expected string or unicode, got %s" % type(name))
    doc = documents.GetActiveDocument()
    if not doc: return None
    result = None
    if start is None:
        startop = doc.GetFirstObject()
    else:
        if isinstance(start, str):
            # warning: doesn't distinguish between objects with same name
            startop = doc.SearchObject(start)
        elif isinstance(start, c4d.BaseObject):
            startop = start
        else:
            raise TypeError("E: parameter 'start' must be one of " +
                            "[str, c4d.BaseObject], but is %s" % type(start))
    if not startop: return None
    if start:
        print("Finding %s under %r" % (name, startop.GetName()))
    curname = startop.GetName()
    if startop:
        if matchfunc and matchfunc(startop, *args, **kwargs):
            return startop
        elif curname == name: 
            return startop
    obj = GetNextObject(startop, startop)
    while obj:
        curname = obj.GetName()
        if matchfunc and matchfunc(obj, *args, **kwargs):
            return obj
        elif curname == name: 
            return obj
        obj = GetNextObject(obj, startop)
    return result


def FindObjects(name=None, uip=None):
    """ Find all objects in the scene, either with the name ``name`` 
        and/or the unique IP ``uip``.
    """
    if name is None and uip is None: 
        return None
    if not isinstance(name, (str, unicode)):
        raise TypeError("E: expected string or unicode, got %s" % type(name))
    doc = documents.GetActiveDocument()
    if not doc: 
        return None
    result = []
    obj = doc.GetFirstObject()
    if not obj: 
        return result
    while obj:
        curname = obj.GetName()
        curip = obj.GetUniqueIP()
        if name and uip:
            if curname == name and uip == curip:
                result.append(obj)
        elif uip and name is None:
            if uip == curip:
                result.append(obj)
        elif name and uip is None:
            if name == curname:
                result.append(obj)
        obj = GetNextObject(obj)
    return result


def CreateObject(typ, name, undo=True):
    """ Create a object of type 'typ', with name 'name'.
        This calls c4d.StopAllThreads() internally.
    """
    obj = None
    try:
        doc = documents.GetActiveDocument()
        if doc is None: return None
        obj = c4d.BaseObject(typ)
        obj.SetName(name)
        c4d.StopAllThreads()
        doc.InsertObject(obj)
        if undo is True:
            doc.AddUndo(c4d.UNDOTYPE_NEW, obj)
        c4d.EventAdd()
    except Exception as e:  # IGNORE:W0703
        print("*** Caught Exception: %r ***" % e)
    return obj


def CreateReplaceObject(typ, name):
    """ Create object with name 'name' removing and 
        replacing any object with the same name. 
    """
    doc = c4d.documents.GetActiveDocument()
    if doc is None:
        return False
    obj = doc.SearchObject(name)
    if obj is not None:
        obj.Remove()
    obj = CreateObject(typ, name)
    return obj


def InsertUnderNull(objs, grp=None, name="Group", copy=False):
    """
    Inserts objects under a group (null) object, optionally creating the group.
    
    Note: currently does not reset obj's coordinate frame 
    to that of the new parent.
    
    objs  BaseObject      can be a single object or a list of objects
    grp   BaseObject      the group to place the objects under 
                          (if None a new null object will be created)
    name  str             name for the new group
    copy  bool            copy the objects if True
        
    Returns the modyfied/created group on success, None on failure.
    """
    if grp is None:
        grp = CreateObject(c4d.Onull, name)
    if copy == True: 
        objs = [i.GetClone() for i in objs]
    if DEBUG: print("inserting objs into group '%s'" % grp.GetName())
    if isinstance(objs, list):
        for obj in objs:
            obj.Remove()
            obj.InsertUnder(grp)
    else:
        objs.Remove()
        objs.InsertUnder(grp)
    c4d.EventAdd()
    return grp


@deprecated(since="0.5")
def RecursiveInsertGroups(entry, parent, root, tree, pmatch='90%'):
    if isinstance(entry, dict):
        for node in entry:
            nodeobj = None
            for op, lvl in ObjectIterator(root.op, root.op): # IGNORE:W0612 #@UnusedVariable
                if op.GetName() == node.name:
                    nodeobj = op
            if not nodeobj:
                nodeobj = CreateObject(c4d.Onull, node.name)
                nodeobj.InsertUnder(parent.op)
            return RecursiveInsertGroups(node, node, root, entry, pmatch)
    elif isinstance(entry, list):
        for child in entry: # type(child) == <type: TreeEntry> or another dict
            if isinstance(child, dict):
                return RecursiveInsertGroups(child, parent, root, tree, pmatch)
            else:
                childobj = FindObject(child.name, start=root.op, matchfunc=FuzzyCompareStrings, limit=pmatch)
                if not childobj:
                    childobj = CreateObject(c4d.Onull, child.name)
                childobj.InsertUnder(parent.op)
    else:
        children = tree[entry]
        return RecursiveInsertGroups(children, entry, root, tree, pmatch)


def UniqueSequentialName(name_base, template=u'%(name)s.%(num)s'):
    """ Return a new sequential name based on a naming template and a 
        base name such that the name uniquely identifies an object in 
        the scene.
        
        By default, mimicks the names generated by CINEMA 4D when 
        multiple objects of the same type are created in quick succession.
        
        For example if the scene had the following objects::
        
            Cube
            Cube.1
            Cube.12
            
        the function would return ``Cube.13`` as a new name.
    """
    doc = c4d.documents.GetActiveDocument()
    if doc is None:
        return False
    oh = ObjectHierarchy()
    objs = oh.Get(r"!" + name_base + r".*?\d*")
    nums = []
    for obj in objs:
        name = obj.GetName()
        mat = re.search(ur'(\d+)$', UnescapeUnicode(name), flags=re.UNICODE)
        if mat and mat.group(1):
            try:
                nums.append(int(mat.group(1), 10))
            except ValueError:
                pass
    new_num = 1
    if len(nums) == 0:
        if doc.SearchObject(name_base) is None:
            return name_base
    else:
        new_num = max(nums) + 1
    new_name = template % ({'name': name_base, 'num': new_num})
    return EscapeUnicode(new_name)
    

def GetGlobalPosition(obj):
    return obj.GetMg().off


def GetGlobalRotation(obj):
    return c4d.utils.MatrixToHPB(obj.GetMg())


def GetGlobalScale(obj):
    m = obj.GetMg()
    return c4d.Vector(m.v1.GetLength(),
                      m.v2.GetLength(),
                      m.v3.GetLength())


def SetGlobalPosition(obj, pos):
    m = obj.GetMg()
    m.off = pos
    obj.SetMg(m)


def SetGlobalRotation(obj, rot):
    """
    Please remember, like most 3D engines 
    CINEMA 4D handles rotation in radians.

    Example for H=10, P=20, B=30:

        import c4d
        from c4d import utils
        #...
        hpb = c4d.Vector(utils.Rad(10), utils.Rad(20), utils.Rad(30))
        SetGlobalRotation(obj, hpb) #object's rotation is 10, 20, 30
    """
    m = obj.GetMg()
    pos = m.off
    scale = c4d.Vector(m.v1.GetLength(),
                       m.v2.GetLength(),
                       m.v3.GetLength())

    m = c4d.utils.HPBToMatrix(rot)

    m.off = pos
    m.v1 = m.v1.GetNormalized() * scale.x
    m.v2 = m.v2.GetNormalized() * scale.y
    m.v3 = m.v3.GetNormalized() * scale.z

    obj.SetMg(m)


def SetGlobalScale(obj, scale):
    m = obj.GetMg()
    
    m.v1 = m.v1.GetNormalized() * scale.x
    m.v2 = m.v2.GetNormalized() * scale.y
    m.v3 = m.v3.GetNormalized() * scale.z
    
    obj.SetMg(m)


def SetAxisRotation(obj, rot, local=False):
    """
    Set the rotation of the object axis (i.e. keeping points in place).
    
    obj   object
    rot   vector
    
    Courtesy of Scott Ayers, source:
    http://www.plugincafe.com/forum/forum_posts.asp?TID=5663&PID=23480#23480
    """
    if obj is None: return False
    if not isinstance(rot, c4d.Vector):
        raise TypeError("E: expected c4d.Vector, got %s" % type(rot))
    currot = obj.GetRelRot()
    if c4d.utils.VectorEqual(currot, rot): return
    obj.SetRelRot(rot)
    if local is True:
        mat = obj.GetMl()
    else:
        mat = obj.GetMg()
    inv = ~mat  
    points = obj.GetAllPoints()
    for i in range(len(points)):
        points[i] = points[i] * inv
    obj.SetAllPoints(points)
    obj.Message(c4d.MSG_UPDATE)
    c4d.EventAdd()


def CenterObjectAxis(obj, center="midpoint"):
    """ Center the object's axis. 
    
        This is equivalent to moving the object to the new center 
        and then moving all the points back to the old spot.
        
        :param str center: can be ``midpoint`` to use the center 
            of the object's bounding box, or ``gravity`` to use the 
            object's center of gravity. The difference is that in the
            latter case single points at extreme distances from the
            object's core aren't given as much weight. 
    """ 
    if not isinstance(obj, c4d.PointObject):
        return False
    maxpoints = obj.GetPointCount()
    if maxpoints == 0:
        return False
    
    ml = obj.GetMl()
    rpos = obj.GetRelPos()
    
    if center == "midpoint":
        # calculate the midpoint of object's bounding box
        bb = BBox.FromObject(obj)
        cg = bb.midpoint
    elif center == "gravity":
        # calculate center of gravity of object vertices 
        # in parent's coordinates
        cg = CalcGravityCenter(obj)
    else:
        raise ValueError("E: param 'center': expected one of ['midpoint', 'gravity'], got %r" % (center))
    c = cg * ml
    # invert the local object matrix and get the translation 
    # vector to new position
    inv = ~ml
    trans = (c - rpos) ^ inv
    # move object to new position and compensate vertex 
    # positions
    obj.SetRelPos(c)
    
    for p in xrange(0, maxpoints):
        obj.SetPoint(p, obj.GetPoint(p) - trans)
    # compensate positions of child objects
    child = obj.GetDown()
    while child:
        child.SetRelPos(child.GetRelPos() - trans)
        child = child.GetNext()
    
    obj.Message(c4d.MSG_UPDATE)
    
    return True


def ObjectAxisFromVector(v):
    if not isinstance(v, c4d.Vector):
        raise TypeError("E: expected c4d.Vector, got %r" % (type(v)))
    return c4d.utils.HPBToMatrix(c4d.utils.VectorToHPB(v))


def MakeEditable(e, clone=False):
    """ Run the Make Editible command on an object or a list of objects. 
    
        :param bool clone: if True, return editable clones of the 
            input.
        
        :return: editable object or list of editable objects
            Returns False if the document of the input objects
            can't be found.
    """
    if isinstance(e, c4d.BaseObject):
        objs = [e]
    elif isinstance(e, list):
        if not isinstance(e[0], c4d.BaseObject):
            raise TypeError("E: expected list element to be c4d.BaseObject, got %r" % (type(e[0])))
        objs = e
    else:
        raise TypeError("E: expected c4d.BaseObject or list of c4d.BaseObjects, got %r" % (type(e)))
    
    doc = objs[0].GetDocument()
    if doc is None:
        return False
    
    settings = c4d.BaseContainer()
    
    if clone is True:
        clones = []
        for obj in objs:
            clones.append(obj.GetClone())
        objs = clones
            
    result = c4d.utils.SendModelingCommand(command=c4d.MCOMMAND_MAKEEDITABLE,
                                           list=objs,
                                           mode=c4d.MODELINGCOMMANDMODE_ALL, 
                                           bc=settings, doc=doc, 
                                           flags=c4d.MODELINGCOMMANDFLAGS_CREATEUNDO)
    
    if isinstance(result, list) and len(result) == 1:
        return result[0]
    return result



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
