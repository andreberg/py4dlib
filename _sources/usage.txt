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

		from py4dlib.utils import clearConsole
		from py4dlib.examples import ShowPolygonNumber


		if __name__=='__main__':
		    clearConsole()
		    doc = c4d.documents.GetActiveDocument()
		    ShowPolygonNumber.main(doc)
