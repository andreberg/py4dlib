Utils
-----

Utility toolbelt for great convenience.

.. function:: ClearConsole()
   
   Clears the console across multiple CINEMA 4D versions.
   
.. function:: FuzzyCompareStrings(a, b, limit=20)
   
   Fuzzy string comparison. 
   
   Two strings are deemed equal if they have 
   the same byte sequence for up to 'limit' chars.
   
   Limit can be an int or a percentage string
   like for example ``60%`` in which case 2 strings
   are deemed equal if at least ``60%`` relative to 
   the longest string match.
   
.. function:: EscapeUnicode(s)

   CINEMA 4D R12's CPython integration stores high-order chars (``ord > 126``) 
   as 4-byte unicode escape sequences with upper case hex letters.

   For example the character ``ä`` (*LATIN SMALL LETTER A WITH DIAERESIS*)
   would be stored as the byte sequence ``\u00E4``. This function replaces
   high-order chars with a unicode escape sequence suitable for CINEMA 4D R12.

   If you use this function in R12 you probably need to balance each call with a
   call to :py:func:`UnescapeUnicode` when the time comes to use, display or
   compare your string to a string returned by some internal function of C4D R12.
   
   For example, if you ask an object named ``Würfel`` (German for cube) 
   for its name::
   
      opname = op.GetName() 
       
      # opname now prints as "W\ürfel" but is actually "W\u00FCrfel"
      # if you UnescapeUnicode now you will get a Python byte string 
      # with proper encoding
      
      opname_unescaped = UnescapeUnicode(opname)
      
      # opname_unescaped is now "W\xfcrfel" (latin-1) and you can compare 
      # it to other Python byte strings with no additional fuzz. If you want
      # to change the byte string and then pass it to C4D to set an object's
      # new name you would have to escape the byte string to get a string
      # that uses an escape sequence similar to the one shown at the beginning
      
      new_opname_escaped = EscapeUnicode(opname_unescaped) 
      
      op.SetName(new_opname_escaped)
      
      # Remember this is only relevant for R12. In R13 and R14 both functions
      # are practically no-ops.

   In R13 and R14 it returns the string untouched since in those versions
   the CPython intergration handles Unicode encoded strings properly.

.. function:: UnescapeUnicode(s)

   CINEMA 4D R12's CPython integration stores high-order chars (``ord > 126``) 
   as 4-byte unicode escape sequences with upper case hex letters.

   This function converts unicode escape sequences used by CINEMA 4D when passing 
   bytes (e.g. ``\u00FC`` -> ``\xfc``) to their corresponding high-order characters.

   It should be used in R12 only and should balance out any calls made to 
   :py:func:`EscapeUnicode`.

   In R13 and R14 the string is returned untouched since in those versions
   the CPython intergration handles Unicode encoded strings properly.

.. function:: VersionString(versionTuple)
   
   ``(x,y,z, .. n) -> 'x.y.z...n'``

.. function:: PPLLString(ll)

   Returns a pretty-printed string of a ``list<list>`` structure.

.. function:: System(cmd, args=None)
   
   Convenience function for firing off commands to 
   the system console. Used instead of `subprocess.call`_ 
   so that shell variables will be expanded properly.
   
   Not the same as `os.system`_ as here it captures 
   ``stdout`` and ``stderr`` in a tuple for Python 2.5 
   and lower or a ``namedtuple`` in 2.6 and higher. 
   So you can use ``result[0]`` in the first case and 
   ``result.out`` in the second.

   :param str cmd: a console command line string
   :param list args: a list of arguments that will be 
      expanded in cmd starting with ``$0``
   :return: ``tuple`` or ``namedtuple``
       
Decorators
----------

.. function:: benchmark(func=None, prec=3, unit='auto', name_width=0, time_width=8)
   
   A decorator that prints the time a function takes
   to execute per call and cumulative total. 
   
   Accepts the following keyword arguments
   
   :param str unit:        time unit for display. one of ``[auto, us, ms, s, m]``.
   :param int prec:        radix point precision. 
   :param int name_width:  width of the right-aligned function name field.
   :param int time_width:  width of the right-aligned time value field.
   
   For convenience you can also set attributes on the benchmark
   function itself with the same name as the keyword arguments
   and the value of those will be used instead. This saves you
   from having to call the decorator with the same arguments each
   time you use it. Just set, for example, ``benchmark.prec = 5``
   after the import and before you use it for the first time.
   
   Usage example:
   
   .. code::
   
      @benchmark
      def factorial(x):
          ''' Return factorial of x. '''
          result = 1
          for i in range(x):
              result = result * (i + 1)
          return result
   
   Output:
   
   .. code::

      -> factorial() @ 001: 10.000 us, total: 10.000 us
      -> factorial() @ 002: 22.000 us, total: 32.000 us
   
   Output for ``@benchmark(unit='ms', time_width=6)``:
   
   .. code::
   
      -> factorial() @ 001:  0.009 ms, total:  0.009 ms
      -> factorial() @ 002:  0.023 ms, total:  0.032 ms
   
.. function:: require(*args, **kwargs)
   
   Decorator that enforces types for function/method args.
   
   Two ways to specify which types are required for each arg.
    
   1) 2-tuples, where first member specifies arg index or arg name,
      second member specifies a type or a tuple of types.
   2) kwargs style, e.g. ``argname=types`` where ``types`` again can 
      be a type or a tuple of types.
   
   None is always a valid type, to allow for optional args.
   
   Usage example:
   
   .. code::
      
      @require(x=int, y=float)
      def func(x, y):
         return  x / y

.. function:: deprecated(level=1, since=None, info=None)

   Can be used to mark functions as deprecated.

   :param int level: severity level. 
      0 = warnings.warn(category=DeprecationWarning)
      1 = warnings.warn_explicit(category=DeprecationWarning)
      2 = raise DeprecationWarning()
   :param string since: the version where deprecation was introduced.
   :param string info: additional info. normally used to refer to the new 
      function now favored in place of the deprecated one.

.. function:: cache(func)
   
   Classic cache decorator.
   
.. function:: memoize(func)
   
   Classic memoization decorator.
   
   
.. _subprocess.call: http://docs.python.org/library/subprocess.html?highlight=subprocess.call#subprocess.call
.. _os.system: http://docs.python.org/library/os.html?highlight=os.system#os.system