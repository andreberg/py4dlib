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

__version__ = (0, 1)
__date__ = '2012-09-26'
__updated__ = '2013-07-30'


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
        >>> defaults.set('key', 'value')
        >>> defaults.save()
    
    If filepath points to an existing file, it will 
    use that file and initializing a new config object 
    by reading from it.
    
    If you later want to read in the config file:
    
        >>> defaults.read()
        >>> print defaults.get('setting')
        value
        >>> print defaults.get('does-not-exist', default='use default instead')
        use default instead
    """
       
    def __init__(self, filepath, defaults=None, header='Settings'):
        """
        Initializes a new user defaults object by either reading or creating
        a settings file at 'filepath'.
        
        @param filepath: usually C{res/settings.ini}relative to the 
            source code file of the plugin, that uses the config store.
        @type filepath: C{str}
        @param defaults: default values to be used if the config
            file needs to be created.
        @type defaults: C{dict}
        @param header: the name for a section in the .ini file.
            Usually you can get away with leaving it at the default.
            This will add a header "[Settings]" under which your
            settings will appear. If you have more advanced uses
            you are advised to modify the config parser state 
            directly through C{self.state}.
        @type header: C{str}
        """
        super(UserDefaults, self).__init__()
        if not isinstance(filepath, basestring):
            raise TypeError("param 'filepath': expected type 'str', but got %s" % type(filepath))
        if not isinstance(header, basestring):
            raise TypeError("param 'default_section': expected type 'str', but got %s" % type(header))
        if defaults is None:
            config = ConfigParser.ConfigParser()
        elif not isinstance(defaults, dict):
            raise TypeError("param 'defaults': expected type 'dict', but got %s" % type(defaults))
        else:
            config = ConfigParser.ConfigParser(defaults)
        self.state = config
        self.filepath = filepath
        self.header = header
        if os.path.exists(filepath):
            self.read()
        else:
            self.state.add_section(header)
            self.save(config, filepath)
    
    def get(self, name, section=None, default=None):
        """
        Retrieve a previously stored value from the config object.
         
        @param name: name of the setting
        @type name: C{str}
        @param section: the section name. C{self.default_section} if None.
        @type section: C{str}
        @param default: a default value to use in case name wasn't found.
        @type default: any
        @return C{str} on success, None or 'default' on failure.
            this will always return a string even if the value was
            stored as another type previously. So the caller is
            responsible for the convertion to the wanted data type.
        """
        if section is None:
            section = self.header
        result = default
        try:
            result = self.state.get(section, name)
        except ConfigParser.NoOptionError, noe: # IGNORE:W0612 @UnusedVariable
            pass
        except Exception, e:
            print("*** Caught exception while getting %r: %s" % (name, e))
        return result
    
    def set(self, name, value, section=None): #@ReservedAssignment
        """
        Store a value in the config object for later retrieval.
        
        @param name: name of the setting
        @type name: C{str}
        @param value: value to set.
        @type value: any
        @param section: the section name. C{self.default_section} if None.
        @type section: C{str}
        @return True if successful, False otherwise.
        """
        if section is None:
            section = self.header
        result = False
        try:
            self.state.set(section, name, value)
            result = True
        except Exception, e: # IGNORE:W0703
            print("*** Caught exception while setting %r to %r: %s" % (name, value, e))
        return result
        
    def read(self):
        """
        Read state from configuration file.
        
        @return True if successful.
        @raise OSError: if config file couldn't be read.
        """
        read_ok = self.state.read(self.filepath)
        if len(read_ok) == 0:
            raise OSError("could not read config file at path %r" % self.filepath)
        return True
        
    def save(self, config=None, filepath=None):
        """
        Save settings to a configuration file.
        @param config: 
            the config object to save. 
            If None, uses C{self.config} instead.
        @type config: C{ConfigParser}
        @param filepath: 
            allows for specifying another path
            than C{self.filepath} in order to save a copy
            of the config object.
        @type filepath: C{str}
        @return True if successful, False otherwise.
        """
        if filepath is None:
            filepath = self.filepath
        elif not isinstance(filepath, basestring):
            raise TypeError("param 'filepath': expected type 'str', but got %s" % type(filepath))
        if config and not isinstance(config, ConfigParser.ConfigParser):
            raise TypeError("param 'config': expected type 'ConfigParser', but got %r" % config)
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
