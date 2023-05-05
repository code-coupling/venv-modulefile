"""
To append instructions in modulefile.
"""
import os
from pathlib import Path
from typing import Tuple

from . import get_module_filename, get_parser
from venvmod.modulefile import add_command

def append_command(arguments: Tuple[str, str, str],
                   description: str,
                   help_arguments: str,
                   command: str):
    """Append a command to a modulefile.

    Parameters
    ----------
    arguments : Tuple[str, str, str]
        If None, arguments are read from :func:`venvmod.commands.get_parser.get_parser` function,
        else ``(virtual_env, appli, arguments)`` given as str
    description : str
        Description of the command provided to ``get_parser`` function if ``arguments`` is None.
    help_arguments : str
        Help of the command provided to ``get_parser`` function if ``arguments`` is None.
    command : str
        Name of the command
    """
    if arguments is None:
        options = get_parser(description=description,
                             help_arguments=help_arguments,
                             with_appli=True)
        arguments = " ".join(options.arguments)
        appli = options.appli
        virtual_env = options.virtual_env
    else:
        virtual_env, appli, arguments = arguments

    add_command(filename=get_module_filename(virtual_env_name=virtual_env,
                                             appli_name=appli),
                line=f"{command} {arguments}")


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
                   help_arguments="path1 path2 ...",
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
                   help_arguments="module1 module2 ...",
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
                   help_arguments="SHELL script [arg...]",
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
                   help_arguments="ENV_VAR paths/to/add/No1 paths/to/add/No2 ...",
                   command="prepend-path")


def append_path(arguments: Tuple[str, str, str] = None):
    """Add a 'append-path' command to a modulefile.

    PEnv var + paths to append are given as str in the last value of ``arguments``.

    Parameters
    ----------
    arguments : Tuple[str, str, str], optional
        See ``append_command`` function, by default None
    """
    append_command(arguments,
                   description="Append value to environment variable.",
                   help_arguments="ENV_VAR paths/to/add/No1 paths/to/add/No2 ...",
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
                   help_arguments="ENV_VAR value",
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
                   help_arguments="ENV_VAR value",
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
                   help_arguments="alias command",
                   command="set-aliases")


def read_env(arguments: Tuple[str, str] = None):
    """Add commands to a modulefile from environment variables.

    Parse ``os.environ`` to look at variable starting with 'appli' (case insensitive) name.

    For thoses variables, append commands for the following suffixes:
     - "LD_LIBRARY_PATH", "PYTHONPATH", "PATH": ``prepend``
     - "MODULE_USE": ``module use``
     - "MODULEFILES": ``module load``
     - "SOURCEFILES": ``source-sh`` for each element separated by ';'
     - "EXPORTS": ``setenv`` for each element separated by ' '
     - "ALIASES": ``set-aliases`` for each element separated by ' '
     - "REMOVE_PATHS": ``remove-path`` for each element separated by ' '

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
        appli = str(Path(appli).name)  #virtual_env may be a path
        virtual_env = options.virtual_env
    else:
        virtual_env, appli = arguments

    path_to_prepend = ["LD_LIBRARY_PATH", "PYTHONPATH", "PATH"]
    for envvar, value in os.environ.items():
        if not envvar.lower().startswith(appli.lower()):
            continue

        for path in path_to_prepend:
            if envvar.endswith(path):
                prepend_path(arguments=(virtual_env, appli, path + " " + value.replace(":", " ")))
                break

        if envvar.endswith("MODULE_USE"):
            module_use(arguments=(virtual_env, appli, value))

        if envvar.endswith("MODULEFILES"):
            module_load(arguments=(virtual_env, appli, value))

        if envvar.endswith("SOURCEFILES"):
            for var in value.split(";"):
                source_sh(arguments=(virtual_env, appli, var))

        if envvar.endswith("EXPORTS"):
            for var in value.split():
                setenv(arguments=(virtual_env, appli, var.replace("=", " ")))

        if envvar.endswith("ALIASES"):
            for var in value.split():
                set_aliases(arguments=(virtual_env, appli, var.replace("=", " ")))

        if envvar.endswith("REMOVE_PATHS"):
            for var in value.split():
                remove_path(arguments=(virtual_env, appli, var.replace("=", " ")))
