Objects
-------

Functions for working with CINEMA 4D's objects.

.. class:: ObjectIterator(startobj, stopobj=None, children_only=True, startlvl=-1)

   Iterator over specific objects in the object manager tree.

   Using a depth first traversal scheme, return a tuple in the form
   ``(op, lvl)``, where op is a ``c4d.BaseObject`` representing the current 
   object and lvl is an integer indicating the current depth level.

   :param startobj:        the object whose hierarchy should be iterated over
   :param stopobj:         an object or a list of objects at which traversal 
                           should stop (optional)
   :param children_only:   if True, iterate through the sub-hierarchy under
                           startobj and stop as soon as startobj's parent or
                           stopobj (if given) is reached. This excludes startobj
                           from the iteration.
   :param startlvl:        base indentation level 
                           
.. class:: ObjectEntry(op, lvl=-1, parents=None)

   Wraps ``c4d.BaseObject`` and makes them hashable, 
   so they can be used as keys in dictionaries.
   
   :param op: the object to wrap.
   :param lvl: the depth level within the hierarchy.
   :param parents: a list of parent objects   

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
   provided with the ``get()`` function, namely the subset that
   coincides with syntax for wildcard and regular epxression 
   expansion. This makes it easy to select a subset of objects,
   based on parent-name relationships.
   
   :param filtertype:    only recognize objects of this c4d type
   
   .. function:: pprint(stopobj=None, filtertype=None, tabsize=4)
   
      Print an indented, tree-like representation of an object manager hierarchy.
      
   .. function:: get(path)
      
      Get a list of ``c4d.BaseObject`` for the key path given by 'path'.

      Key path can contain wildcards (``*`` or ``?``) or regular expression
      syntax. Prepend a '!' to 'path' if you want to forego wildcard expansion
      and thus ensure it is used as a verbatim regular expression pattern instead.
      
      Note that 'path' must match the whole key it is tested against.
      
      Returns a list of all objects for which 'path', expanded, matches a 
      concatenated parent path. 
      
      Returns an empty list if no objects could be located for 'path'.

.. function:: select(obj)

.. function:: selectAdd(obj)

   Same as :py:func:`select` but uses a slightly different mechanism.
   
   See also ``BaseDocument.SetSelection(sel, mode)``.
   
.. function:: selectGroupMembers(grp)
   
.. function:: selectObjects(objs)
   
.. function:: deselectAll(inObjMngr=False)

   Not the same as ``BaseSelect.DeselectAll()``.

   :param inObjMngr:    if True, run the deselect command for the Object Manager, 
                        else the general one for the editor viewport.
   
   
.. function:: groupObjects(objs, name="Group")
   
   ``CallCommand`` based grouping of objects from a list. 
   Generally unreliable, because selection state matters.
    
   Use :py:func:`insertUnderNull` for better effect.

.. function:: groupSelected(name="Group")
   
   ``CallCommand`` based grouping of selected objects. 
   Generally unreliable, because selection state matters.
   
   Use :py:func:`insertUnderNull` for better effect.

.. function:: recurseBranch(obj)
   
.. function:: getNextObject(obj, stopobjs=None)
   
   Return the next object in the hierarchy using a depth-first traversal scheme.
   
   If stopobjs is a ``c4d.BaseObject`` or a list of ``c4d.BaseObjects`` and the next
   operation would encounter this object (or the first object in the list) None
   will be returned. This is so that this function can be used in a while loop.

.. function:: getActiveObjects(doc)

   Same as ``BaseDocument.GetSelection()``, while 
   GetSelection also selects tags and materials.
   
.. function:: findObject(name, start=None, matchfunc=None, *args, **kwargs)

   Find object with name 'name'.

   :param start: a ``c4d.BaseObject`` or a str representing the name
       of a ``c4d.BaseObject`` from where the search should begin.
   :param matchfunc: can be used to customize the matching logic 
       by providing the name of a custom function. This function 
       will be passed a potential candidate object plus any 
       remaining args. It should return True or False.
   
.. function:: findObjects(name)
   
   Find all objects in the scene with the name 'name'
   
.. function:: createObject(typ, name, undo=True)

   Create a object of type 'typ', with name 'name'.
   This calls ``c4d.StopAllThreads()`` internally.

.. function:: insertUnderNull(objs, grp=None, name="Group", copy=False)

   Inserts objects under a group (null) object, optionally creating the group.

   Note: currently does not reset obj's coordinate frame 
   to that of the new parent.
   
   :param objs:  ``BaseObject``      can be a single object or a list of objects
   :param grp:   ``BaseObject``      the group to place the objects under 
                                     (if None a new null object will be created)
   :param name:  ``str``             name for the new group
   :param copy:  ``bool``            copy the objects if True
   
.. function:: getGlobalPosition(obj)

.. function:: getGlobalRotation(obj)

.. function:: getGlobalScale(obj)

.. function:: setGlobalPosition(obj, pos)

.. function:: setGlobalRotation(obj, rot)
   
   Please remember, like most 3D engines 
   CINEMA 4D handles rotation in radians.

   Example for ``H=10, P=20, B=30``:

      .. code:: 
      
         import c4d
         from c4d import utils
         # ...
         hpb = c4d.Vector(utils.Rad(10), utils.Rad(20), utils.Rad(30))
         SetGlobalRotation(obj, hpb) # object's rotation is 10, 20, 30
   
      
.. function:: setGlobalScale(obj, scale)

.. function:: setAxisRotation(obj, rot, local=False)

   Set the rotation of the object axis (i.e. keeping points in place).
    
   :param obj:   object
   :param rot:   vector
   
   Courtesy of Scott Ayers (`source <http://www.plugincafe.com/forum/forum_posts.asp?TID=5663&PID=23480#23480>`_)
   
   
.. function:: centerObjectAxis(obj)

