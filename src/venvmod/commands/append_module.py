"""
To append instructions in modulefile.
"""
import os
from pathlib import Path
from typing import Any, List, Tuple

from venvmod.tools import get_std_name, logger
from venvmod.modulefile import add_command

from . import get_module_filepath, get_parser


def append_command(arguments: Tuple[str, str, str],
                   description: str,
                   positionals: List[Tuple[str, Any, str, Any]],
                   command: str):
    """Append a command to a modulefile.

    Parameters
    ----------
    arguments : Tuple[str, str, str]
        If None, arguments are read from :func:`venvmod.commands.get_parser.get_parser` function,
        else ``(virtual_env, appli, arguments)`` given as str
    description : str
        Description of the command provided to ``get_parser`` function if ``arguments`` is None.
    positionals: List[Tuple[str, Any, str, Any]], optional
        list of positionals ('name', default, 'help', nargs), by default None
    command : str
        Name of the command
    """
    if arguments is None:
        options = get_parser(description=description,
                             positionals=positionals,
                             with_appli=True)
        virtual_env = options.virtual_env
        logger.debug("append_command virtual_env '%s'", virtual_env)
        appli = options.appli
        logger.debug("append_command appli '%s'", appli)
        arguments = ""
        for positional in positionals:
            values = vars(options)[positional[0]]
            logger.debug("append_command positional '%s': '%s'", positional, values)
            arguments += " " + " ".join(values)
    else:
        virtual_env, appli, arguments = arguments

    filepath = get_module_filepath(virtual_env=Path(virtual_env).absolute(), appli_name=appli)

    add_command(filename=filepath, line=f"{command} {arguments}")


def module_use(arguments: Tuple[str, str, str] = None):
    """Add a 'module use' command to a modulefile.

    Paths to use are given as str in the last value of ``arguments``.

    Parameters
    ----------
    arguments : Tuple[str, str, str], optional
        See ``append_command`` function, by default None
    """
    append_command(arguments,
                   description="Add dir(s) to MODULEPATH variable.",
                   positionals=[("PATH", [], "List of paths to use to locate modules", '+')],
                   command="module use")


def module_load(arguments: Tuple[str, str, str] = None):
    """Add a 'module load' command to a modulefile.

    Modules to load are given as str in the last value of ``arguments``.

    Parameters
    ----------
    arguments : Tuple[str, str, str], optional
        See ``append_command`` function, by default None
    """
    append_command(arguments,
                   description="Load modulefile(s).",
                   positionals=[("MODULE", [], "List of environment module to load", '+')],
                   command="module load")


def source_sh(arguments: Tuple[str, str, str] = None):
    """Add a 'source-sh' command to a modulefile.

    Shell + file to source + args are given as str in the last value of ``arguments``.

    Parameters
    ----------
    arguments : Tuple[str, str, str], optional
        See ``append_command`` function, by default None
    """
    append_command(arguments,
                   description="Script(s) to source.",
                   positionals=[("SHELL", [], "Shell name", 1),
                                ("SCRIPT", [], "Script path", 1),
                                ("ARG", [], "Script arguments", "*")],
                   command="source-sh")


def prepend_path(arguments: Tuple[str, str, str] = None):
    """Add a 'prepent-path' command to a modulefile.

    Env var + paths to prepend are given as str in the last value of ``arguments``.

    Parameters
    ----------
    arguments : Tuple[str, str, str], optional
        See ``append_command`` function, by default None
    """
    append_command(arguments,
                   description="Prepend value to environment variable.",
                   positionals=[("ENV_VAR", [], "Variable to prepend", 1),
                                ("PATH", [], "List of paths to prepend", '+')],
                   command="prepend-path")


def append_path(arguments: Tuple[str, str, str] = None):
    """Add a 'append-path' command to a modulefile.

    Env var + paths to append are given as str in the last value of ``arguments``.

    Parameters
    ----------
    arguments : Tuple[str, str, str], optional
        See ``append_command`` function, by default None
    """
    append_command(arguments,
                   description="Append value to environment variable.",
                   positionals=[("ENV_VAR", [], "Variable to append", 1),
                                ("PATH", [], "List of paths to append", '+')],
                   command="append-path")


def setenv(arguments: Tuple[str, str, str] = None):
    """Add a 'setenv' command to a modulefile.

    Env var + value to define are given as str in the last value of ``arguments``.

    Parameters
    ----------
    arguments : Tuple[str, str, str], optional
        See ``append_command`` function, by default None
    """
    append_command(arguments,
                   description="Define environment variable.",
                   positionals=[("VARIABLE", [], "Environment variable to define", 1),
                                ("VALUE", [], "Value associated to the variable", 1)],
                   command="setenv")


def remove_path(arguments: Tuple[str, str, str] = None):
    """Add a 'remove-path' command to a modulefile.

    Env var + value to remove are given as str in the last value of ``arguments``.

    Parameters
    ----------
    arguments : Tuple[str, str, str], optional
        See ``append_command`` function, by default None
    """
    append_command(arguments,
                   description="Remove value from environment variable.",
                   positionals=[("VARIABLE", [], "Environment variable to modify", 1),
                                ("PATH", [], "Path to remove from variable", 1)],
                   command="remove-path")


def set_aliases(arguments: Tuple[str, str, str] = None):
    """Add a 'set-aliases' command to a modulefile.

    Alias to define are given as str in the last value of ``arguments``.

    Parameters
    ----------
    arguments : Tuple[str, str, str], optional
        See ``append_command`` function, by default None
    """
    append_command(arguments,
                   description="Define aliases.",
                   positionals=[("ALIAS", [], "Alias name", 1),
                                ("VALUE", [], "Alias value", 1)],
                   command="set-aliases")


def read_env(arguments: Tuple[str, str] = None):  # pylint: disable=too-many-branches
    """Add commands to a modulefile from environment variables.

    Parse ``os.environ`` to look at variable starting with 'appli' (case insensitive) name.

    For thoses variables, append commands for the following suffixes:
     - "LD_LIBRARY_PATH", "PYTHONPATH", "PATH": ``prepend``
     - "MODULE_USE": ``module use``
     - "MODULEFILES": ``module load``
     - "SOURCEFILES": ``source-sh`` for each element 'shell script [args...]' separated by ';'
     - "EXPORTS": ``setenv`` for each element 'var=value' separated by ' '
     - "ALIASES": ``set-aliases`` for each element 'var=value' separated by ' '
     - "REMOVE_PATHS": ``remove-path`` for each element 'var=value' separated by ' '

    Examples
    --------
    The following ::

        $ export MY_APPLI_LD_LIBRARY_PATH="/path/to/lib1:/path/to/lib2"
        $ venvmod-cmd-read-env --appli MY_APPLI

    will prepend "LD_LIBRARY_PATH" with "/path/to/lib1:/path/to/lib2" in "my_appli" module.

    Parameters
    ----------
    arguments : Tuple[str, str], optional, by default None
        If None, arguments are read from ``get_parser`` function,
        else ``(virtual_env, appli)`` given as str
    """
    if arguments is None:
        options = get_parser(description="Read environment variable to extend modulefile.",
                             with_appli=True)
        appli = options.appli if options.appli else options.virtual_env
        appli = get_std_name(str(Path(appli).name))  # virtual_env may be a path
        virtual_env = options.virtual_env
    else:
        virtual_env, appli = arguments

    # List env vars
    appli_env_vars = {envvar: value for envvar, value in os.environ.items()
                      if get_std_name(envvar).startswith(appli.replace('.', '_'))}

    print(f"read_env: os.environ = '{os.environ}'")
    print(f"read_env: appli_env_vars = '{appli_env_vars}'")

    logger.debug("read_env: os.environ = '%s'", os.environ)
    logger.debug("read_env: appli_env_vars = '%s'", appli_env_vars)

    # Source file in first
    for envvar, value in appli_env_vars.items():
        if envvar.endswith("SOURCEFILES"):
            for var in value.split(";"):
                if var:
                    source_sh(arguments=(virtual_env, appli, var))
            appli_env_vars.pop(envvar)
            break

    path_to_prepend = ["LD_LIBRARY_PATH", "PYTHONPATH", "PATH"]
    for envvar, value in appli_env_vars.items():

        for var_path in path_to_prepend:
            if envvar.endswith(var_path):
                for var in reversed(value.split(":")):
                    if var:
                        prepend_path(arguments=(virtual_env, appli, f"{var_path} {var}"))
                break

        for suffix, function in {
                "MODULE_USE": module_use,
                "MODULEFILES": module_load}.items():
            if envvar.endswith(suffix):
                function(arguments=(virtual_env, appli, value))

        for suffix, function in {
                "EXPORTS": setenv,
                "ALIASES": set_aliases,
                "REMOVE_PATHS": remove_path}.items():
            if envvar.endswith(suffix):
                for var in value.split():
                    if var:
                        function(arguments=(virtual_env, appli, var.replace("=", " ")))
