Objects
-------

Functions for working with CINEMA 4D's objects.

.. class:: ObjectIterator(startobj, stopobj=None, children_only=True, startlvl=-1)

   Iterator over specific objects in the object manager tree.

   Using a depth first traversal scheme, return a tuple in the form
   ``(op, lvl)``, where op is a ``c4d.BaseObject`` representing the current 
   object and lvl is an integer indicating the current depth level.

   :param c4d.BaseObject startobj:  the object whose hierarchy should be iterated over
   :param c4d.BaseObject stopobj:   an object or a list of objects at which traversal 
                                    should stop (optional)
   :param bool children_only:       if True, iterate through the sub-hierarchy under
                                    startobj and stop as soon as startobj's parent or
                                    stopobj (if given) is reached. This excludes startobj
                                    from the iteration.
   :param int startlvl:             base indentation level 
                           
.. class:: ObjectEntry(op, lvl=-1, parents=None)

   Wraps ``c4d.BaseObject`` and makes them hashable, 
   so they can be used as keys in dictionaries.
   
   :param c4d.BaseObject op: the object to wrap.
   :param int lvl: the depth level within the hierarchy.
   :param list parents: a list of parent objects   

.. class:: ObjectHierarchy(rootobj=None, filtertype=None)
   
   Represents a hierarchical group structure in the object manager.

   Can be used to create a Pythonic snapshot of the current scene 
   so as to provide easy access to specifc sets of objects.
   
   Starting with root object stores a list of ``c4d.BaseObjects`` 
   for each depth level in a dictionary. Each list is indexed by a 
   concatenation of its parent names. The concat character is a
   forward slash, which forms a Unix like filepath as seen with 
   the object manager's address bar widget.
   
   Additionally, a small subset of X-Path like functionality is 
   provided with the ``Get()`` function, namely the subset that
   coincides with syntax for wildcard and regular epxression 
   expansion. This makes it easy to select a subset of objects,
   based on parent-name relationships.
   
   :param c4d.Otype filtertype: only recognize objects of this c4d type
   
   .. function:: PPrint(stopobj=None, filtertype=None, tabsize=4)
   
      Print an indented, tree-like representation of an object manager hierarchy.
      
   .. function:: Get(path)
      
      Get a list of ``c4d.BaseObject`` for the key path given by 'path'.

      Key path can contain wildcards (``*`` or ``?``) or regular expression
      syntax. Prepend a ``!`` to ``path`` if you want to forego wildcard expansion
      and thus ensure it is used as a verbatim regular expression pattern instead.
      
      Note that ``path`` must match the whole key it is tested against.
      
      Returns a list of all objects for which ``path``, expanded, matches a 
      concatenated parent path. 
      
      Returns an empty list if no objects could be located for ``path``.

.. function:: Select(obj)

.. function:: SelectAdd(obj)

   Same as :py:func:`Select` but uses a slightly different mechanism.
   
   See also ``BaseDocument.SetSelection(sel, mode)``.
   
.. function:: SelectGroupMembers(grp)
   
.. function:: SelectObjects(objs)
   
.. function:: DeselectAll(in_objmngr=False)

   Not the same as ``BaseSelect.DeselectAll()``.

   :param bool in_objmngr: if True, run the deselect command for the 
      Object Manager, else the general one for the editor viewport.
   
.. function:: GroupObjects(objs, name="Group")
   
   ``CallCommand`` based grouping of objects from a list. 
   Generally unreliable, because selection state matters.
    
   Use :py:func:`InsertUnderNull` for better effect.

.. function:: GroupSelected(name="Group")
   
   ``CallCommand`` based grouping of selected objects. 
   Generally unreliable, because selection state matters.
   
   Use :py:func:`InsertUnderNull` for better effect.

.. function:: RecurseBranch(obj)
   
.. function:: GetNextObject(obj, stopobjs=None)
   
   Return the next object in the hierarchy using a depth-first traversal scheme.
   
   If stopobjs is a ``c4d.BaseObject`` or a list of ``c4d.BaseObjects`` and the next
   operation would encounter this object (or the first object in the list) None
   will be returned. This is so that this function can be used in a while loop.

.. function:: GetActiveObjects(doc)

   Same as ``BaseDocument.GetSelection()``, while 
   GetSelection also selects tags and materials.
   
.. function:: FindObject(name, start=None, matchfunc=None, *args, **kwargs)

   Find object with name 'name'.

   :param c4d.BaseObject start: object from where the search should begin.
       Can also be a ``str`` representing the name of a ``c4d.BaseObject``.
   :param function matchfunc: can be used to customize the matching logic 
       by providing the name of a custom function. This function 
       will be passed a potential candidate object plus any 
       remaining args. It should return True or False.
   
.. function:: FindObjects(name)
   
   Find all objects in the scene with the name 'name'
   
.. function:: CreateObject(typ, name, undo=True)

   Create a object of type 'typ', with name 'name'.
   
   This calls ``c4d.StopAllThreads()`` internally.
   
.. function:: CreateReplaceObject(typ, name)

   Create object with name 'name' removing and replacing any object with the same name.
   
   This calls :py:func:`CreateObject` internally.

.. function:: UniqueSequentialName(name_base, template=u'%(name)s.%(num)s')
   
   Return a new sequential name based on a naming template and a 
   base name such that the name uniquely identifies an object in 
   the scene.
   
   By default, mimicks the names generated by CINEMA 4D when 
   multiple objects of the same type are created in quick succession.
   
   For example if the scene had the following objects::
      
      Cube
      Cube.1
      Cube.12
   
   Using the default template, the function would return ``Cube.13`` 
   as a new name.
   

.. function:: InsertUnderNull(objs, grp=None, name="Group", copy=False)

   Inserts objects under a group (null) object, optionally creating the group.

   Note: currently does not reset obj's coordinate frame 
   to that of the new parent.
   
   :param c4d.BaseObject objs:  can be a single object or a list of objects
   :param c4d.BaseObject grp:   the group to place the objects under. If None 
                                a new null object will be created.
   :param str name:             name for the new group
   :param bool copy:            copy the objects if True
   
.. function:: GetGlobalPosition(obj)

.. function:: GetGlobalRotation(obj)

.. function:: GetGlobalScale(obj)

.. function:: SetGlobalPosition(obj, pos)

.. function:: SetGlobalRotation(obj, rot)
   
   Please remember, like most 3D engines 
   CINEMA 4D handles rotation in radians.

   Example for ``H=10, P=20, B=30``:

   .. code:: 
   
      import c4d
      from c4d import utils
      # ...
      hpb = c4d.Vector(utils.Rad(10), utils.Rad(20), utils.Rad(30))
      SetGlobalRotation(obj, hpb) # object's rotation is 10, 20, 30
   
      
.. function:: SetGlobalScale(obj, scale)

.. function:: SetAxisRotation(obj, rot, local=False)

   Set the rotation of the object axis (i.e. keeping points in place).
    
   :param obj:   object
   :param rot:   vector
   
   Courtesy of Scott Ayers (`source <http://www.plugincafe.com/forum/forum_posts.asp?TID=5663&PID=23480#23480>`_)
   
   
.. function:: CenterObjectAxis(obj, center="midpoint")

   Center the object's axis. 
   
   This is equivalent to moving the object to the new center 
   and then moving all the points back to the old spot.

   :param str center: can be ``midpoint`` to use the center 
      of the object's bounding box, or ``gravity`` to use the 
      object's center of gravity. The difference is that in the
      latter case single points at extreme distances from the
      object's core aren't given as much weight.

.. function:: MakeEditable(obj)

   Run the Make Editible command on obj or a list of objects.
