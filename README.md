Introduction
============

The `py4dlib` library is a collection of Python modules to be used   
with MAXON's [CINEMA 4D](http://www.maxon.net "CINEMA 4D") 3D application.

It's goal is to provide essentials but also convenience functions   
left out by CINEMA 4D's current Python SDK so that repetition and   
code duplication can be avoided.

It currently includes routines for working with c4d objects,   
polygonal modelling tasks, some utilities and tools for writing   
plugins plus a small library of math routines needed for 3D work.

You can view the current [documentation](http://andreberg.github.io/py4dlib "py4dlib docs") online.

Installation
============

Take the `py4dlib` folder which you can find under `/source` in   
this repository, and put it under the following path:

    <USER_FOLDER>/library/python/packages/<OS>
    
`<USER_FOLDER>` is the prefs directory for CINEMA 4D in your home   
directory and `<OS>` is the name of the operating system you are   
running. 

For example on OS X this path could be:

    /Users/<USER>/Library/Preferences/MAXON/CINEMA 4D R<VERSIONSTRING>/library/python/packages/osx

On Windows this path could be:

    %APPDATA%\MAXON\CINEMA 4D R<VERSIONSTRING>\library\python\packages\win64


Usage
=====

Simply import any modules you'd like to use in your scripts or plugins, 
like you normally would:

    import py4dlib
    from py4dlib.objects import ObjectIterator
    
To see if everything is working correctly you can try running an example  
script.  

Make a new scene, create a sphere and make it editable, then select it in   
the Object Manager.  

Open the Python script editor and run the following script:

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

![result](http://andreberg.github.io/py4dlib/_images/ShowPolygonNumber.png "Show Polygon Number")


See also the [Best Practices](http://andreberg.github.io/py4dlib/usage.html#best-practices "Best Practices") section in the online docs.


Contributions
=============

I'd be very happy to accept code contributions. If you'd like to contribute  
please fork this repository, commit your changes to your local fork and then  
send me a pull request.

If that’s too much of a hassle, you can also go ahead and create a gist or a   
pastebin post (or whatever copypasta service you fancy) and send me the URL so   
that I can include the code manually.


Acknowledgements
================

a.k.a. **The Hall of Fame**

In no particular order.

Lennart Wåhlin (TCA Studios)  
Per-Anders Edwards  
Adam Swaab  
NitroMan (Nitro4D)  
Robert Leger  
Niklas Rosenstein  
Scott Ayers  

Thanks for making some of your C.O.F.F.E.E. and Python scripts   
free and for often not denying the ability to take a look.


License
=======

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

      http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
