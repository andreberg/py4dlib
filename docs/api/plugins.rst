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
         >>> defaults.set('key', 'value')
         >>> defaults.save()
   
   If filepath points to an existing file, it will 
   use that file and initializing a new config object 
   by reading from it.
   
   If you later want to read in the config file:
   
      .. code::
         
         >>> defaults.read()
         >>> print defaults.get('setting')
         value
         >>> print defaults.get('does-not-exist', default='use default instead')
         use default instead
   
      :param filepath: usually ``res/settings.ini`` relative to the 
          source code file of the plugin, that uses the config store.
      :type filepath: ``str``
      :param defaults: default values to be used if the config
          file needs to be created.
      :type defaults: ``dict``
      :param header: the name for a section in the .ini file.
          Usually you can get away with leaving it at the default.
          This will add a header "[Settings]" under which your
          settings will appear. If you have more advanced uses
          you are advised to modify the config parser state 
          directly through ``self.state``.
      :type header: ``str``
   
   .. function:: get(self, name, section=None, default=None)
      
      Retrieve a previously stored value from the config object.

      :param name: name of the setting
      :type name: ``str``
      :param section: the section name. ``self.default_section`` if None.
      :type section: ``str``
      :param default: a default value to use in case name wasn't found.
      :type default: any
      :return: ``str`` on success, None or 'default' on failure.
          this will always return a string even if the value was
          stored as another type previously. So the caller is
          responsible for the convertion to the wanted data type.
      
   .. function:: set(self, name, value, section=None)
      
      Store a value in the config object for later retrieval.

      :param name: name of the setting
      :type name: ``str``
      :param value: value to set.
      :type value: any
      :param section: the section name. ``self.default_section`` if None.
      :type section: ``str``
      :return: True if successful, False otherwise.
      
   .. function:: read(self)
      
      Read state from configuration file.

      :return: True if successful.
      :raise OSError: if config file couldn't be read.
      
   .. function:: save(self, config=None, filepath=None)
      
      Save settings to a configuration file.
      
      :param config: 
          the config object to save. 
          If None, uses ``self.config`` instead.
      :type config: ``ConfigParser``
      :param filepath: 
          allows for specifying another path
          than ``self.filepath`` in order to save a copy
          of the config object.
      :type filepath: ``str``
      :return: True if successful, False otherwise.
      
      