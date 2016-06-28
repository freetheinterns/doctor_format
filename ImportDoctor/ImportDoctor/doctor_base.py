import re

class ImportNurse(object):
    ignore_indented = True      # Grabs indented imports
    group_by_module_type = True # Separates system modules from local ones
    descending = True           # Primary order on sort: True => BIG to small
    one_import_per_line = True  # Separates grouped imports onto their own lines
    exclude_from = True         # Sort on string before 'import' for 'from' imports
    import_ontop = True         # Place all 'from' imports below standard imports
    wrap_strict = False         # If true, wrap_depth will be strictly enforced
    
    # These variables are controlled through getters and setters.
    _alpha_order = False        # Sorts by alphabetical instead of length
    _newline_padding = 1        # How many empty lines after end of imports
    _isolation = []             # Groups of imports to separate by name
    _wrap_depth = 0             # The character count at which line wrapping begins
    
    # groups as follows: from [AModule] import ([A, B, C])
    _from_statement = re.compile('from +([a-zA-Z._]+) +import +\\(?([ a-zA-Z.,_]+)\\)? *')
    # groups as follows: import ([AModule, BModule])
    _import_statement = re.compile('import \\(?([ a-zA-Z.,_]+)\\)? *')
    
    # primary filtering function
    _filter = lambda n: n
    
    def __init__(self, **kwargs):
        if not set(kwargs.keys()) <= self.__vars__():
            raise ValueError('Unexpected arguements passed.')
        for key, value in kwargs.iteritems():
            setattr(self, key, value)
        self._filter = (lambda n: n) if self._alpha_order else (lambda n: len(n))
    
    def __vars__(self):
        return set([x for x in dir(self) if not x.startswith('__') 
                    and not callable(getattr(self, x))])
    
    @property
    def regex_find_import(self):
        return self._import_statement
    
    @regex_find_import.setter
    @_purge_state
    def regex_find_import(self, value):
        if isinstance(value, basestring):
            self._import_statement = re.compile(str(value))
        elif isinstance(value, type(self._import_statement)):
            self._import_statement = value
        else:
            raise ValueError('Value must be a string or compiled regex search object.')
    
    @property
    def regex_find_from(self):
        return self._from_statement
    
    @regex_find_from.setter
    @_purge_state
    def regex_find_from(self, value):
        if isinstance(value, basestring):
            self._from_statement = re.compile(str(value))
        elif isinstance(value, type(self._from_statement)):
            self._from_statement = value
        else:
            raise ValueError('Value must be a string or compiled regex search object.')
    
    @property
    def order_alphabetically(self):
        return self._alpha_order
    
    @order_alphabetically.setter
    @_purge_state
    def order_alphabetically(self, value):
        value = bool(value)
        self._alpha_order = value
        self._filter = (lambda n: n) if value else (lambda n: len(n))
        
    @property
    def wrap_depth(self):
        return self._wrap_depth
    
    @wrap_depth.setter
    def wrap_depth(self, value):
        if type(value) is not int:
            raise ValueError('wrap_depth must be integer')
        if value < 25:
            raise ValueError('There is no reason to wrap code at 25 characters or less')
        self._wrap_depth = value
       
    @property
    def newline_padding(self):
        return self._newline_padding
    
    @newline_padding.setter
    def newline_padding(self, value):
        if type(value) is not int:
            raise ValueError('newline_padding must be an integer')
        if value < 0:
            raise ValueError('Padding must be a positive value')
        self._newline_padding = value
        
    @property
    def isolated_groups(self):
        return self._isolation[:]
    
    @isolated_groups.setter
    def isolated_groups(self, value):
        if type(value) is not list:
            raise ValueError('isolated_groups must be a list of module names')
        self._isolation = value[:]
        
    # This function defines a decorator that resets the data parsed if a
    # function decorated with this is called.
    def _purge_state(func):
        def oncall(self, *args, **kwargs):
            func(self, *args, **kwargs)
            if self.Q or self.source:
                print 'Critical variable ({}) modified. Resetting Queue.'.format(func.__name__)
            self.Q = None
            self.source = None
        return oncall

# Checks to see if a string matches any of the current system level modules
def is_sys_module(name):
    if name not in sys.modules.keys():
        return False
    pathname = os.path.dirname(inspect.getfile(sys.modules[name]))
    # System modules either come from standard python libraries or from venvs
    for path in sys.path:
        if pathname.startswith(path):
            return True
    return False

# returns a long line with \\\n inserted after a space
# segmenting the line into depth sized chunks
def wrap_word(line, depth, strict):
    line = line.strip()
    if depth < 30:
        return line
    result = ''
    split_point = line.find(' ')
    while len(line) > depth:
        if split_point == -1:
            break
        next_blank = split_point
        while next_blank <= depth:
            split_point = next_blank
            next_blank = line.find(' ', next_blank + 1)
            if next_blank == -1:
                if strict:
                    result += line[:split_point + 1] + '\\\n'
                    line = '    ' + line[split_point + 1:]
                return result + line
        result += line[:split_point + 1] + '\\\n'
        line = '    ' + line[split_point + 1:]
        split_point = line.find(' ', 5)
    return result + line
        
builtin_python_modules = [
    'string', 're', 'difflib', 'textwrap', 'unicodedata', 'stringprep', 'readline', 
    'rlcompleter', 'struct', 'codecs', 'datetime', 'calendar', 'collections', 
    'collections', 'heapq', 'bisect', 'array', 'weakref', 'types', 'copy', 'pprint', 
    'reprlib', 'enum', 'numbers', 'math', 'cmath', 'decimal', 'fractions', 'random', 
    'statistics', 'itertools', 'functools', 'operator', 'pathlib', 'os', 'fileinput', 
    'stat', 'filecmp', 'tempfile', 'glob', 'fnmatch', 'linecache', 'shutil', 'macpath', 
    'pickle', 'copyreg', 'shelve', 'marshal', 'dbm', 'sqlite', 'zlib', 'gzip', 'bz', 
    'lzma', 'zipfile', 'tarfile', 'csv', 'configparser', 'netrc', 'xdrlib', 'plistlib', 
    'hashlib', 'hmac', 'os', 'io', 'time', 'argparse', 'getopt', 'logging', 'logging', 
    'logging', 'getpass', 'curses', 'curses', 'curses', 'curses', 'platform', 'errno', 
    'ctypes', 'threading', 'multiprocessing', 'concurrent', 'subprocess', 'sched', 'queue', 
    'dummy', 'socket', 'ssl', 'select', 'selectors', 'asyncio', 'asyncore', 'asynchat', 
    'signal', 'mmap', 'email', 'json', 'mailcap', 'mailbox', 'mimetypes', 'base', 
    'binhex', 'binascii', 'quopri', 'uu', 'html', 'html', 'html', 'xml', 'xml', 
    'xml', 'xml', 'xml', 'xml', 'xml', 'xml', 'xml', 'webbrowser', 'cgi', 'cgitb', 
    'wsgiref', 'urllib', 'urllib', 'urllib', 'urllib', 'urllib', 'urllib', 'http', 
    'http', 'ftplib', 'poplib', 'imaplib', 'nntplib', 'smtplib', 'smtpd', 'telnetlib', 
    'uuid', 'socketserver', 'http', 'http', 'http', 'xmlrpc', 'xmlrpc', 'xmlrpc', 
    'ipaddress', 'audioop', 'aifc', 'sunau', 'wave', 'chunk', 'colorsys', 'imghdr', 
    'sndhdr', 'ossaudiodev', 'gettext', 'locale', 'turtle', 'cmd', 'shlex', 'tkinter', 
    'tkinter', 'tkinter', 'tkinter', 'typing', 'pydoc', 'doctest', 'unittest', 'unittest', 
    'unittest', 'test', 'test', 'bdb', 'faulthandler', 'pdb', 'timeit', 'trace', 
    'tracemalloc', 'distutils', 'ensurepip', 'venv', 'zipapp', 'sys', 'sysconfig', 
    'builtins', 'warnings', 'contextlib', 'abc', 'atexit', 'traceback', 'gc', 'inspect', 
    'site', 'fpectl', 'code', 'codeop', 'zipimport', 'pkgutil', 'modulefinder', 'runpy', 
    'importlib', 'parser', 'ast', 'symtable', 'symbol', 'token', 'keyword', 'tokenize', 
    'tabnanny', 'pyclbr', 'py', 'compileall', 'dis', 'pickletools', 'formatter', 'msilib', 
    'msvcrt', 'winreg', 'winsound', 'posix', 'pwd', 'spwd', 'grp', 'crypt', 'termios', 
    'tty', 'pty', 'fcntl', 'pipes', 'resource', 'nis', 'syslog', 'optparse', 'imp'
]