# -*- coding: utf-8 -*-
# 
#  utils.py
#  py4dlib
#  
#  Created by André Berg on 2012-09-28.
#  Copyright 2012 Berg Media. All rights reserved.
#
#  andre.bergmedia@googlemail.com
# 
# pylint: disable-msg=F0401

'''py4dlib.utils -- utility toolbelt for great convenience.'''

import os
import warnings

__version__ = (0, 6)
__date__ = '2012-09-27'
__updated__ = '2013-08-08'


DEBUG = 0 or ('DebugLevel' in os.environ and os.environ['DebugLevel'] > 0)
TESTRUN = 0 or ('TestRunLevel' in os.environ and os.environ['TestRunLevel'] > 0)


from subprocess import Popen, PIPE
from functools import wraps, partial

try:
    import c4d #@UnresolvedImport
except ImportError:
    if TESTRUN == 1:
        pass


def ClearConsole():
    version = c4d.GetC4DVersion()
    if version > 12999:
        cmd = 13957 # R14 (and R13?)
    else:
        cmd = 1024314 # R12
    c4d.CallCommand(cmd)


def FuzzyCompareStrings(a, b, limit=20):
    """ Fuzzy string comparison. 
    
    Two strings are deemed equal if they have 
    the same byte sequence for up to 'limit' chars.
    
    Limit can be an int or a percentage string
    like for example '60%' in which case 2 strings
    are deemed equal if at least '60%' relative to 
    the longest string match.
    """
    result = True
    maxchars = limit
    if isinstance(limit, basestring):
        try:
            maxp = int(limit[:-1]) # chop off '%'
            maxlen = max(len(a), len(b)) # percentage relative to longest str
            maxchars = int((maxp/100.0) * maxlen)
        except:
            raise ValueError("E: param 'limit' must be one of [str, int] " +
                             "where str indicates a percentage, e.g. '75%'.")
    idx = 0
    for char in a:
        if idx >= maxchars: 
            break
        try:
            if char != b[idx]:
                result = False
        except IndexError:
            result = False
        idx += 1
    return result


def EscapeUnicode(s):
    ur""" CINEMA 4D's CPython integration stores high-order chars (``ord > 126``) 
        as 4-byte unicode escape sequences with upper case hex letters.
        
        For example the character ``ä`` (LATIN SMALL LETTER A WITH DIAERESIS)
        would be stored as the byte sequence ``\u00E4``. This function replaces
        high-order chars with a unicode escape sequence suitable for CINEMA 4D.
    """
    result = ""
    if c4d.GetC4DVersion() > 12999:
        try:
            s = s.decode('utf-8')
        except UnicodeEncodeError:
            # already unicode?
            pass
    for b in s:
        if ord(b) > 126:
            result += r"\\u%04X" % (ord(b),)
        else:
            result += b
    return result


def UnescapeUnicode(s):
    ur""" CINEMA 4D's CPython integration stores high-order chars (``ord > 126``) 
        as 4-byte unicode escape sequences with upper case hex letters.
        
        This function converts unicode escape sequences used by CINEMA 4D to their
        corresponding high-order characters.
    """
    try:
        return s.decode('unicode_escape')
    except UnicodeEncodeError:
        # already unicode?
        return s


def VersionString(versionTuple):
    """ (x,y,z .. n) -> 'x.y.z...n' """
    return '.'.join(str(x) for x in versionTuple)


def PPLLString(ll):
    """ Returns a pretty-printed string of a ``list<list>`` structure. """
    s = " " + repr(ll)[1:-2]
    lines = s.split('],')
    result = '],\n'.join(lines)
    return result + ']'


def System(cmd, args=None):
    '''
    Convenience function for firing off commands to 
    the System console. Used instead of `subprocess.call`_
    so that shell variables will be expanded properly.
    
    Not the same as `os.system`_ as here it captures 
    returns ``stdout`` and ``stderr`` in a tuple in
    Python 2.5 and lower or a ``namedtuple`` in 2.6
    and higher. So you can use ``result[0]`` in the
    first case and ``result.out`` in the second.

    :param cmd: a console command line
    :type cmd: ``string``
    :param args: a list of arguments that 
                 will be expanded in cmd 
                 starting with ``$0``
    :type args: ``list``
    :return: ``tuple`` or ``namedtuple``
    '''
    if args is None:
        fullcmd = cmd
    else:
        args = ["'{}'".format(s.replace(r'\\', r'\\\\')
                               .replace("'", r"\'")) for s in args]
        fullcmd = "%s %s" % (cmd, ' '.join(args))
    out, err = Popen(fullcmd, stdout=PIPE, shell=True).communicate()
    System.out = out
    System.err = err
    try:
        from collections import namedtuple
        StdStreams = namedtuple('StdStreams', ['out', 'err'])
        return StdStreams(out=out, err=err)
    except ImportError:
        return (out, err)


def benchmark(func=None, prec=3, unit='auto', name_width=0, time_width=8):
    """
    A decorator that prints the time a function takes
    to execute per call and cumulative total. 
    
    Accepts the following keyword arguments:
    
    :param unit:         ``str``     time unit for display. one of `[auto, us, ms, s, m]`.
    :param prec:         ``int``     radix point precision. 
    :param name_width:   ``int``     width of the right-aligned function name field.
    :param time_width:   ``int``     width of the right-aligned time value field.
       
    For convenience you can also set attributes on the benchmark
    function itself with the same name as the keyword arguments
    and the value of those will be used instead. This saves you
    from having to call the decorator with the same arguments each
    time you use it. Just set, for example, ``benchmark.prec = 5``
    after the import and before you use it for the first time.
    """
    import time
    if hasattr(benchmark, 'prec'):
        prec = getattr(benchmark, 'prec')
    if hasattr(benchmark, 'unit'):
        unit = getattr(benchmark, 'unit')
    if hasattr(benchmark, 'name_width'):
        name_width = getattr(benchmark, 'name_width')
    if hasattr(benchmark, 'time_width'):
        time_width = getattr(benchmark, 'time_width')
    if func is None:
        return partial(benchmark, prec=prec, unit=unit, 
                        name_width=name_width, time_width=time_width)
    @wraps(func)
    def wrapper(*args, **kwargs):  # IGNORE:W0613
        def _get_unit_mult(val, unit):
            multipliers = {'us': 1000000.0, 'ms': 1000.0, 's': 1.0, 'm': (1.0 / 60.0)}
            if unit in multipliers:
                mult = multipliers[unit]
            else:  # auto
                if val >= 60.0:
                    unit = "m"
                elif val >= 1.0:
                    unit = "s"
                elif val <= 0.001:
                    unit = "us"
                else:
                    unit = "ms"
                mult = multipliers[unit]
            return (unit, mult)
        t = time.clock()
        res = func(*args, **kwargs)
        td = (time.clock() - t)
        wrapper.total += td
        wrapper.count += 1
        tt = wrapper.total
        cn = wrapper.count
        tdu, tdm = _get_unit_mult(td, unit)
        ttu, ttm = _get_unit_mult(tt, unit)
        td *= tdm
        tt *= ttm
        print(" -> {0:>{8}}() @ {1:>03}: {3:>{7}.{2}f} {4:>2}, total: {5:>{7}.{2}f} {6:>2}"
              .format(func.__name__, cn, prec, td, tdu, tt, ttu, time_width, name_width))
        return res
    wrapper.total = 0
    wrapper.count = 0
    return wrapper


def require(*args, **kwargs):
    '''
    Decorator that enforces types for function/method args.
    
    Two ways to specify which types are required for each arg.
     
    1) 2-tuples, where first member specifies arg index or arg name,
       second member specifies a type or a tuple of types.
    2) kwargs style, e.g. `argname`=`types` where `types` again can 
       be a type or a tuple of types.
    
    None is always a valid type, to allow for optional args.
    '''
    _required = []
    _args = args
    _kwargs = kwargs
    def wrapper(func):
        if hasattr(func, "wrapped_args"):
            wrapped_args = getattr(func, "wrapped_args")
        else:
            code = func.func_code
            wrapped_args = list(code.co_varnames[:code.co_argcount])
        @wraps(func)
        def wrapped_fn(*args, **kwargs):
            def _check_type(_funcname, _locator, _arg, _types):
                if _arg is not None and not isinstance(_arg, _types):
                        pluralstr = "one " if isinstance(_types, (list, tuple)) else ""  # IGNORE:W0311
                        raise TypeError("E: for %s(): param %r must be %sof %r, but is %r" %  # IGNORE:W0311
                                        (_funcname, str(_locator), pluralstr, _types, type(_arg)))
            def _get_index(param_name):
                codeobj_varnames = wrapped_args
                try:
                    _idx = codeobj_varnames.index(param_name)
                    return _idx
                except ValueError:
                    raise NameError(param_name)
            for i in _args:
                locator = i[0]
                types = i[1]
                idx = None
                if isinstance(locator, int):
                    idx = locator
                elif isinstance(locator, basestring):
                    name = locator
                    idx = _get_index(name)
                    if name in kwargs:
                        _check_type(func.__name__, name, kwargs[name], types)
                if idx >= len(args):
                    break
                _check_type(func.__name__, idx, args[idx], types)
            for k, v in _kwargs.iteritems():
                name = k
                types = v
                if name in kwargs:
                    _check_type(func.__name__, name, kwargs[name], types)
                else:
                    idx = _get_index(name)
                    if idx >= len(args):
                        break
                    _check_type(func.__name__, name, args[idx], types)
            return func(*args, **kwargs)
        wrapped_fn.wrapped_args = wrapped_args
        return wrapped_fn
    return wrapper


def deprecated(level=1, since=None, info=None):
    """This decorator can be used to mark functions as deprecated.
        
    :param int level: severity level. 
        0 = warnings.warn(category=DeprecationWarning)
        1 = warnings.warn_explicit(category=DeprecationWarning)
        2 = raise DeprecationWarning()
    :param string since: the version where deprecation was introduced.
    :param string info: additional info. normally used to refer to the new 
        function now favored in place of the deprecated one.
    """
    def __decorate(func):
        if since is None:
            msg = 'Method %s() is deprecated.' % func.__name__
        else:
            msg = 'Method %s() has been deprecated since version %s.' % (func.__name__, str(since))
        if info:
            msg += ' ' + info
        @wraps(func)
        def __wrapped(*args, **kwargs): # IGNORE:C0111
            if level <= 0:
                warnings.warn(msg, category=DeprecationWarning, stacklevel=2)
                func(*args, **kwargs)
            elif level == 1:
                warnings.warn_explicit(msg, category=DeprecationWarning, 
                                       filename=func.func_code.co_filename, 
                                       lineno=func.func_code.co_firstlineno + 1)
            elif level >= 2:
                raise DeprecationWarning(msg)
        return __wrapped
    return __decorate


def cache(func):
    """Classic cache decorator."""
    saved = {}
    @wraps(func)
    def wrapped_fn(*args):
        if args in saved:
            return saved[args]
        result = func(*args)
        saved[args] = result
        return result
    return wrapped_fn

    
def memoize(func):
    """Classic memoization decorator."""
    mem_cache = {}
    @wraps(func)
    def wrapped_fn(*args, **kw):
        key = (args, tuple(sorted(kw.items())))
        if key not in mem_cache:
            mem_cache[key] = func(*args, **kw)
        return mem_cache[key]
    return wrapped_fn


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
