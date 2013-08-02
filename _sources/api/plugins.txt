Plugins
-------


.. class:: UserDefaults(filepath, defaults=None, header='Settings')

   Support for reading and writing settings files 
   in .ini format.
   
   This can be used to provide state persistence 
   for UI elements of a plugin.
   
   Examples:
   
   Initialize a new config object, modify and 
   then save it:
   
   .. code::
   
      >>> filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "res", "settings.ini")
      >>> defaults = UserDefaults(filepath=filepath)
      >>> defaults.Set('key', 'value')
      >>> defaults.Save()
   
   If filepath points to an existing file, it will 
   use that file and initializing a new config object 
   by reading from it.
   
   If you later want to read in the config file:
   
   .. code::
      
      >>> defaults.Read()
      >>> print defaults.Get('setting')
      value
      >>> print defaults.Get('does-not-exist', default='use default instead')
      use default instead
   
   :param filepath: ``str`` 
       usually ``res/settings.ini`` relative to the 
       source code file of the plugin, that uses the config store.
   :param defaults: ``dict`` default values to be used if the config
       file needs to be created.
   :param header: ``str``  the name for a section in the .ini file.
       Usually you can get away with leaving it at the default.
       This will add a header ``[Settings]`` under which your
       settings will appear. If you have more advanced uses
       you are advised to modify the config parser state 
       directly through ``self.state``.
   
   .. function:: Get(self, name, section=None, default=None)
      
      Retrieve a previously stored value from the config object.

      :param name: ``str``  name of the setting
      :param section: ``str`` the section name. ``self.default_section`` if None.
      :param default: ``any`` a default value to use in case name wasn't found.
      :return: ``str`` on success, None or *default* on failure.
          this will always return a string even if the value was
          stored as another type previously. So the caller is
          responsible for the convertion to the wanted data type.
      
   .. function:: Set(self, name, value, section=None)
      
      Store a value in the config object for later retrieval.

      :param name: ``str`` name of the setting
      :param value: ``any`` value to set.
      :param section: ``str`` the section name. ``self.default_section`` if None.
      :return: True if successful, False otherwise.
      
   .. function:: Read(self)
      
      Read state from configuration file.

      :return: True if successful.
      :raise OSError: if config file couldn't be read.
      
   .. function:: Save(self, config=None, filepath=None)
      
      Save settings to a configuration file.
      
      :param config: ``ConfigParser``
          the config object to save. 
          If None, uses ``self.config`` instead.
      :param filepath: ``str``
          allows for specifying another path
          than ``self.filepath`` in order to save a copy
          of the config object.
      :return: True if successful, False otherwise.
      
      