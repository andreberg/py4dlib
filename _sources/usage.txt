Usage
-----

Simply import any modules you'd like to use in your scripts or plugins, 
like you normally would::

    import py4dlib
    from py4dlib.objects import ObjectIterator

To see if everything is working correctly you can try running an example  
script.  

Make a new scene, create a sphere and make it editable, then select it in   
the Object Manager.  

Open the Python script editor and run the following script::

		import c4d
		from c4d import gui
		#Welcome to the world of Python

		from py4dlib.utils import ClearConsole
		from py4dlib.examples import ShowPolygonNumber


		if __name__=='__main__':
		    ClearConsole()
		    doc = c4d.documents.GetActiveDocument()
		    ShowPolygonNumber.main(doc)

The result should be something like this:

.. image:: img/ShowPolygonNumber.png
   :width: 422.25 px
   :height: 351 px
   :alt: ShowPolygonNumber


Best Practices
--------------

What can you do if your plugin depends on **py4dlib** but  
the end user doesn't have the library installed?

Well, you could try downloading the library using Python
itself, but I'd caution against it. Running a plugin 
shouldn't start a connection to some random website to
download stuff on the end user's computer.

No, there are better ways to deal with this issue.
For example, you could:

1) kindly ask the user to download the library herself
2) include the library with your script or plugin
3) copy and paste the methods you are using into your own script or plugin

Asking The User
~~~~~~~~~~~~~~~

In the first case a sensible thing you can do, is check for 
prerequisite dependencies at the time the plugin is actually 
executed and if dependencies are missing display a message to 
the user and politely ask to download the library.

You can find a complete example in the :ref:`Extract` plugin 
included in the :ref:`py4dlib.examples`, but I shall give a 
brief overview here.

At the top of your plugin set a constant indicating the state
of the dependency prerequisite and wrap any py4dlib imports in 
a try/except block, catching ``ImportError``::

   PY4DLIB_FOUND = False
   
   try:
       from py4dlib.objects import DeselectAll, Select, GetGlobalRotation
       # more dependency imports ...
       PY4DLIB_FOUND = True
   except ImportError:
       pass
       
Now, when the time comes to execute the plugin and do the bulk
of the actual work, check if your prerequisite constant is True
and if not display a message dialog, for example, like so::

   PY4DLIB_NOT_FOUND_MSG = """This plugin needs py4dlib which is missing.

   Please download and install it free of charge
   from http://github.com/andreberg/py4dlib.
   """
   
   # ...
   
   def run(self):
       if not PY4DLIB_FOUND:
           c4d.gui.MessageDialog(PY4DLIB_NOT_FOUND_MSG)
           return False
      # ...

Including The Library
~~~~~~~~~~~~~~~~~~~~~

In the second case you can put the py4dlib source folder into a subdirectory
included in your plugin or script distribution. To import the library you
can then modify ``sys.path`` at the top of your script before any py4dlib
imports. For example if you have the following directory structure::

   icons/
   res/
   lib/
   Plugin.pyp
   
you can put the ``py4dlib`` folder under ``lib/`` and then modify ``sys.path``
at the top of your plugin/script, like so::

   import sys, os
   sys.path.insert(1, os.path.realpath('lib'))  # use 1 not 0!
   
Note that we are using insert here instead of append. You can also use 
append but in that case the user's version of py4dlib will be loaded 
before your included one if the user has py4dlib installed.

In case you are developing a script and not a plugin, it is the same, really.
It just means you have to distribute an actual folder structure where a simple 
file would have done. But if you want to include icons you'd have to do that 
anyway.

Copy And Paste Methods
~~~~~~~~~~~~~~~~~~~~~~

If you don't want to make the user install anything and you also don't want to
include the library, then you will have to copy and paste the py4dlib methods 
you are using into your plugin.

In that case I recommend developing your plugin or script with the usual
dependency imports until you have it just right. Then before you deliver
the final version to your users, create a version with just the neccessary
methods inlined. 

Special care was given to make the py4dlib API not too self-entangled so 
ripping stuff out to copy+paste it into your own scripts shouldn't prove
too difficult.



