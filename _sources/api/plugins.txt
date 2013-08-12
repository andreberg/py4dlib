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
      >>> print(defaults.Get('setting'))
      value
      >>> print(defaults.Get('does-not-exist', default='use default instead'))
      use default instead
   
   :param str filepath: usually ``res/settings.ini`` relative to the 
       source code file of the plugin, that uses the config store.
   :param defaults: ``dict`` default values to be used if the config
      file needs to be created. It is also possible to pass None
      here and then use the :py:func:`Set` and :py:func:`Save` functions 
      to set inidividual settings after creation of the config object.
   :param str header: the name for a section in the .ini file.
       Usually you can get away with leaving it at the default.
       This will add a header ``[Settings]`` under which your
       settings will appear. If you have more advanced uses
       you are advised to modify the config parser state 
       directly through ``self.state``.
   
   .. function:: Get(self, name, section=None, default=None, valuetype="str")
      
      Retrieve a previously stored value from the config object.

      :param str name: name of the setting
      :param str section: the section name. ``self.header`` if None.
      :param any default: a default value to use in case name wasn't found.
      :param str valuetype: type of the value to get. can be one of ``[str, bool, int, float]``.
      :return: ``str`` on success, None or *default* on failure.
          this will always return a string even if the value was
          stored as another type previously. So the caller is
          responsible for the convertion to the wanted data type.

   .. function:: GetInt(self, name, section=None, default=None)

      Retrieve a previously stored integer value from the config object.

      :param str name:  name of the setting
      :param str section: the section name. ``self.header`` if None.
      :param any default: a default value to use in case name wasn't found.
      :return: ``int`` on success, None or 'default' on failure.

   .. function:: GetFloat(self, name, section=None, default=None)

      Retrieve a previously stored float value from the config object.

      :param str name:  name of the setting
      :param str section: the section name. ``self.header`` if None.
      :param any default: a default value to use in case name wasn't found.
      :return: ``float`` on success, None or 'default' on failure.

   .. function:: GetBool(self, name, section=None, default=None)

      Retrieve a previously stored boolean value from the config object.

      :param str name:  name of the setting
      :param str section: the section name. ``self.header`` if None.
      :param any default: a default value to use in case name wasn't found.
      :return: ``bool`` on success, None or 'default' on failure.
      
   .. function:: Set(self, name, value, section=None)
      
      Store a value in the config object for later retrieval.

      :param str name: name of the setting
      :param any value: value to set.
      :param str section: the section name. ``self.header`` if None.
      :return: True if successful, False otherwise.
      
   .. function:: Read(self)
      
      Read state from configuration file.

      :return: True if successful.
      :raise OSError: if config file couldn't be read.
      
   .. function:: Save(self, config=None, filepath=None)
      
      Save settings to a configuration file.
      
      :param ConfigParser config: the config object to save. 
          If None, uses ``self.config`` instead.
      :param str filepath: allows for specifying another path
          than ``self.filepath`` in order to save a copy
          of the config object.
      :return: True if successful, False otherwise.
      
      