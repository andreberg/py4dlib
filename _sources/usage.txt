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

The only sensible thing you can do, is check for a prerequisite
dependency check at the time the plugin is actually executed
and if dependencies are missing display a message to the user
and politely ask to download the library.

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



