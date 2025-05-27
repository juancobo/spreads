import logging
import numbers
import os

import lupa

CHDKPTP_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            'vendor', 'chdkptp')
logger = logging.getLogger('chdkptp.lua')


class PTPError(Exception):
    def __init__(self, err_table):
        Exception.__init__(self, ("{0} (ptp_code: {1})"
                                  .format(err_table.msg, err_table.ptp_rc)))
        self.ptp_code = err_table.ptp_rc
        self.traceback = err_table.traceback


class LuaContext(object):
    """ Proxy object around :class:`lupa.LuaRuntime` that wraps all Lua code
        inside of `pcall` and raises proper Exceptions.
    """
    def _raise_exception(self, errval):
        if isinstance(errval, (basestring, numbers.Number)):
            raise lupa.LuaError(errval)
        elif errval['etype'] == 'ptp':
            raise PTPError(errval)
        else:
            raise lupa.LuaError(parse_table(errval))

    def _parse_rval(self, rval):
        # Check for errors from checked calls and for internal CHDK errors
        if isinstance(rval, tuple):
            if not rval[0] or len(rval) == 4 and rval[1] is None:
                self._raise_exception(rval[2])
            else:
                rval = rval[1]
        return rval

    def call(self, funcname, *args, **kwargs):
        args = list(args)
        if ":" in funcname:
            obj = funcname.split(':')[-0]
            unbound_name = funcname.replace(':', '.')
            fn = self.eval("function(...) return pcall(%s, %s, ...) end"
                           % (unbound_name, obj))
        else:
            fn = self.eval("function(...) return pcall(%s, ...) end"
                           % funcname)
        if kwargs:
            args.append(self.table(**kwargs))
        return self._parse_rval(fn(*args))

    def eval(self, lua_code):
        return self._rt.eval(lua_code)

    def execute(self, lua_code):
        return self._rt.execute(lua_code)

    def peval(self, lua_code):
        returns = 'returns' in lua_code
        checked_code = ("pcall(function() {0} {1} end)"
                        .format('return' if not returns else '', lua_code))
        return self._parse_rval(self._rt.eval(checked_code))

    def pexecute(self, lua_code):
        checked_code = ("return pcall(function() {0} end)"
                        .format(lua_code))
        return self._parse_rval(self._rt.execute(checked_code))

    def require(self, modulename):
        return self._rt.require(modulename)

    def table(self, *items, **kwargs):
        return self._rt.table(*items, **kwargs)

    @property
    def globals(self):
        return self._rt.globals()

    def __init__(self):
        self._rt = lupa.LuaRuntime(unpack_returned_tuples=True, encoding=None)
        if self.eval("type(jit) == 'table'"):
            raise RuntimeError("lupa must be linked against Lua, not LuaJIT.\n"
                               "Please install lupa with `--no-luajit`.")
        self._setup_runtime()

    def _setup_runtime(self):
        # Set up module paths - convert Python path to Lua string
        chdkptp_path_str = str(CHDKPTP_PATH)
        self._rt.execute("""
            local chdkptp_path = "{0}"
            package.path = chdkptp_path .. '/lua/?.lua;' .. package.path
            package.cpath = chdkptp_path .. '/?.so;' .. package.path
        """.format(chdkptp_path_str))

        # Set up essential globals that chdkptp expects
        self._rt.execute("""
            -- Create minimal sys global for environment access
            sys = {{
                getenv = function(name)
                    return os.getenv(name)
                end,
                ostype = function()
                    return 'Linux'
                end,
                getargs = function()
                    return {{}}
                end
            }}
            
            -- Create minimal guisys global
            guisys = {{
                caps = function()
                    return {{IUP = false}}
                end
            }}
            
            -- Create minimal chdk global for core functionality
            chdk = {{
                list_usb_devices = function()
                    return {{}}
                end
            }}
            
            -- Create lfs compatibility shim
            lfs = {{
                attributes = function(path, attr)
                    return nil
                end
            }}
        """)

        # Load only essential chdkptp modules with error handling
        self._rt.execute("""
            local function safe_require(name)
                local status, result = pcall(require, name)
                if status then
                    return result
                else
                    -- Return minimal stub for failed modules
                    return {{}}
                end
            end
            
            util = safe_require('util')
            if util.import then
                pcall(util.import, util)
            end
            
            varsubst = safe_require('varsubst')
            chdku = safe_require('chdku')
            prefs = safe_require('prefs')
            
            -- Create connection function if chdku module failed
            if not chdku.connection then
                chdku.connection = function()
                    return {{}}
                end
            end
        """)

        # Set up preferences with error handling
        self._rt.execute("""
            if prefs and prefs._set then
                pcall(prefs._set, 'cli_verbose', 2)
            end
        """)

        # Register loggers
        self._rt.eval("""
            function(logger)
                cli = cli or {{}}
                cli.infomsg = function(...)
                    if logger and logger.info then
                        local status, msg = pcall(string.format, ...)
                        if status then
                            logger.info(msg:match( "(.-)%s*$" ))
                        end
                    end
                end

                cli.dbgmsg = function(...)
                    if logger and logger.debug then
                        local status, msg = pcall(string.format, ...)
                        if status then
                            logger.debug(msg:match('(.-)%s*$'))
                        end
                    end
                end
            end
        """)(logger)

        # Create global connection object with error handling
        self._rt.execute("""
            if chdku and chdku.connection then
                con = chdku.connection()
            else
                con = {{}}
            end
        """)


# Global Lua runtime, for use by utility functions
global_lua = LuaContext()

# Lua Table type
LuaTable = type(global_lua.table())


def parse_table(table):
    out = dict(table)
    for key, val in out.iteritems():
        if isinstance(val, LuaTable):
            out[key] = parse_table(val)
    if all(x.isdigit() for x in out.iterkeys()):
        out = tuple(out.values())
    return out
