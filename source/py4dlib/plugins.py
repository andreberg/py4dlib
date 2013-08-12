# -*- coding: utf-8 -*-
# 
#  plugins.py
#  py4dlib
#  
#  Created by André Berg on 2012-09-26.
#  Copyright 2012 Berg Media. All rights reserved.
#
#  andre.bergmedia@googlemail.com
# 
# pylint: disable-msg=F0401

'''py4dlib.plugins -- functions for helping you write py4d plugins.'''

import os
import ConfigParser

__version__ = (0, 5)
__date__ = '2012-09-26'
__updated__ = '2013-08-13'

DEBUG = 0 or ('DebugLevel' in os.environ and os.environ['DebugLevel'] > 0)
TESTRUN = 0 or ('TestRunLevel' in os.environ and os.environ['TestRunLevel'] > 0)


class UserDefaults(object):
    """ 
    Support for reading and writing settings files 
    in .ini format.
    
    This can be used to provide state persistence 
    for UI elements of a plugin.
    
    Examples:
    
    Initialize a new config object, modify and 
    then save it:
    
        >>> filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "res", "settings.ini")
        >>> defaults = UserDefaults(filepath=filepath)
        >>> defaults.Set('key', 'value')
        >>> defaults.Save()
    
    If filepath points to an existing file, it will 
    use that file and initializing a new config object 
    by reading from it.
    
    If you later want to read in the config file:
    
        >>> defaults.Read()
        >>> print defaults.Get('setting')
        value
        >>> print defaults.Get('does-not-exist', default='use default instead')
        use default instead
    """
       
    def __init__(self, filepath, defaults=None, header='Settings'):
        """
        Initializes a new user defaults object by either reading or creating
        a settings file at 'filepath'.
        
        :param filepath: ``str`` 
            usually ``res/settings.ini``relative to the 
            source code file of the plugin, that uses the config store.
        :param defaults: ``dict`` default values to be used if the config
            file needs to be created. It is also possible to pass None
            here and then use the :py:func:`Set` and :py:func:`Save` functions 
            to set inidividual settings after creation of the config object.
        :param header: ``str``  the name for a section in the .ini file.
            Usually you can get away with leaving it at the default.
            This will add a header "[Settings]" under which your
            settings will appear. If you have more advanced uses
            you are advised to modify the config parser state 
            directly through ``self.state``.
        """
        super(UserDefaults, self).__init__()
        if not isinstance(filepath, basestring):
            raise TypeError("E: param 'filepath': expected type 'str', but got %s" % type(filepath))
        if not isinstance(header, basestring):
            raise TypeError("E: param 'header': expected type 'str', but got %s" % type(header))
        if defaults and not isinstance(defaults, dict):
            raise TypeError("E: param 'defaults': expected type 'dict', but got %s" % type(defaults))
        if defaults and not os.path.exists(filepath):
            # check if any values in defaults are not of type string 
            # since ConfigParser needs string - always.
            _defaults = defaults.copy()
            for k, v in _defaults.iteritems():
                if not isinstance(v, basestring):
                    defaults[k] = str(v)
            config = ConfigParser.ConfigParser(defaults)
        else:
            config = ConfigParser.ConfigParser()
        self.state = config
        self.filepath = filepath
        self.header = header
        if os.path.exists(filepath):
            if DEBUG:
                print("reading existing settings file at path %r" % filepath)
            self.Read()
        else:
            self.state.add_section(header)
            self.Save(config, filepath)
            if DEBUG:
                print("saving new state %r to settings file at path %r" % (self.state, filepath))
            
    def __str__(self, *args, **kwargs):
        return ("%r, header = %s, filepath = %s, state = %s" % 
                (self, self.header, self.filepath, self.state))
        
    def Get(self, name, section=None, default=None, valuetype="str"):
        """
        Retrieve a previously stored value from the config object.
         
        :param str name:  name of the setting
        :param str section: the section name. ``self.header`` if None.
        :param any default: a default value to use in case name wasn't found.
        :param str valuetype: type of the value to get. can be one of ``[str, bool, int, float]``.
        :return: ``valuetype`` on success, None or 'default' on failure.
        """
        if section is None:
            section = self.header
        result = default
        try:
            if valuetype == "bool":
                result = self.state.getboolean(section, name)
            elif valuetype == "int":
                result = self.state.getint(section, name)
            elif valuetype == "float":
                result = self.state.getfloat(section, name)
            else:
                result = self.state.get(section, name)
        except ConfigParser.NoOptionError, noe:  # IGNORE:W0612 @UnusedVariable
            pass
        except Exception, e:
            print("*** Caught exception while getting %r: %s" % (name, e))
        return result
    
    def GetInt(self, name, section=None, default=None):
        """
        Retrieve a previously stored integer value from the config object.
         
        :param str name:  name of the setting
        :param str section: the section name. ``self.header`` if None.
        :param any default: a default value to use in case name wasn't found.
        :return: ``int`` on success, None or 'default' on failure.
        """
        return self.Get(name, section=section, default=default, valuetype="int")
    
    def GetFloat(self, name, section=None, default=None):
        """
        Retrieve a previously stored float value from the config object.
         
        :param str name:  name of the setting
        :param str section: the section name. ``self.header`` if None.
        :param any default: a default value to use in case name wasn't found.
        :return: ``float`` on success, None or 'default' on failure.
        """
        return self.Get(name, section=section, default=default, valuetype="float")
    
    def GetBool(self, name, section=None, default=None):
        """
        Retrieve a previously stored boolean value from the config object.
         
        :param str name:  name of the setting
        :param str section: the section name. ``self.header`` if None.
        :param any default: a default value to use in case name wasn't found.
        :return: ``bool`` on success, None or 'default' on failure.
        """
        return self.Get(name, section=section, default=default, valuetype="bool")
    
    def Set(self, name, value, section=None):  #@ReservedAssignment
        """
        Store a value in the config object for later retrieval.
        
        :param name: ``str`` name of the setting
        :param value: ``any`` value to set.
        :param section: ``str`` the section name. ``self.header`` if None.
        :return: True if successful, False otherwise.
        """
        if section is None:
            section = self.header
        result = False
        try:
            self.state.set(section, name, str(value))
            result = True
        except Exception, e:  # IGNORE:W0703
            print("*** Caught exception while setting %r to %r: %s" % (name, value, e))
        return result
        
    def Read(self):
        """
        Read state from configuration file.
        
        :return: True if successful or None, if config file couldn't be read.
        """
        read_ok = self.state.read(self.filepath)
        if len(read_ok) == 0:
            if DEBUG:
                print("could not read config file at path %r" % self.filepath)
            return None
        return True
        
    def Save(self, config=None, filepath=None):
        """
        Save settings to a configuration file.
        
        :param config: ``ConfigParser``
            the config object to save. 
            If None, uses ``self.config`` instead.
        :param filepath: ``str``
            allows for specifying another path
            than ``self.filepath`` in order to save a copy
            of the config object.
        :return: True if successful, False otherwise.
        """
        if filepath is None:
            filepath = self.filepath
        elif not isinstance(filepath, basestring):
            raise TypeError("E: param 'filepath': expected type 'str', but got %s" % type(filepath))
        if config and not isinstance(config, ConfigParser.ConfigParser):
            raise TypeError("E: param 'config': expected type 'ConfigParser', but got %r" % config)
        else:
            config = self.state
        result = False
        try:
            with open(filepath, 'wb') as configfile:
                config.write(configfile)
            result = True
        except Exception, e: # IGNORE:W0703
            print("*** Caught exception while writing config: %r ***" % e)
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
