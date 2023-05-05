
import os
from pathlib import Path
from typing import List

from packaging import version

from . import get_parser
from .append_module import module_load, read_env
from ..modulefile import (get_version, ModuleInstaller, upgrade_modulefile, create_modulefile,
                          upgrade_venv)

from ..tools import PACKAGE_NAME, check_raise, remove_duplicates


def initialize(virtual_env: Path = None,
               version_or_path: str = "5.2.0") -> int:
    """Initialize a venv-modulefile environment

    Parameters
    ----------
    virtual_env : Path, optional
        If None, arguments are read from :func:`venvmod.commands.get_parser` function,
        else the path to the virtual env, by default None
    version_or_path : str, optional
        Modulefile version to use if not found or version < 4.6.
        It can be a source directory to avoid donloading, by default "5.2.0"

    Returns
    -------
    int
        return code
    """

    if virtual_env is None:
        options = get_parser(
            description="Initialize Modulefile in venv.",
            help_arguments="Log message when the module is loaded.",
            with_appli=False,
            with_verbose=True,
            options=[("modulefile-version",
                      version_or_path,
                      "Modulefile version to use if not found or version < 4.6."
                      " It can be a source directory to avoid downloading")])
        virtual_env = Path(options.virtual_env).absolute()
        if options.modulefile_version:
            version_or_path = options.modulefile_version

    if version.parse(get_version()) < version.parse("14.6"):

        install_prefix=virtual_env / "opt" / "modulefiles"
        if not install_prefix.exists():
            code = ModuleInstaller(install_prefix=install_prefix,
                                version_or_path=version_or_path,
                                cache_directory=virtual_env / ".cache"
                                ).run(verbose=options.verbose, do_raise=True)
            if code:
                return code

            code = upgrade_modulefile(virtual_env=virtual_env, module_prefix=install_prefix)
            if code:
                return code

    code = create_modulefile(virtual_env=virtual_env,
                             module_name=virtual_env.stem,
                             module_category=PACKAGE_NAME,
                             log_load=" ".join(options.arguments))
    if code:
        return code

    code = upgrade_venv(virtual_env=virtual_env)

def add_appli(virtual_env: Path = None,
              applis: List[str] = None):
    """Add application modulefiles to the environment.

    This call also use the :func:`venvmod.commands.append_module.read_env` function for each appli.

    Parameters
    ----------
    virtual_env : Path, optional
        If None, arguments are read from :func:`venvmod.commands.get_parser` function,
        else the path to the virtual env, by default None
    applis : List[str], optional
        List of module file to create in addition to those given through cli, by default None
    """

    if virtual_env is None:
        options = get_parser(description="Initialize Modulefile for an application.",
                             help_arguments="Appli name(s) to add to the environment.",
                             with_appli=False,
                             with_verbose=True)
        virtual_env = Path(options.virtual_env).absolute()

    fails = []
    for appli in remove_duplicates(options.arguments + (applis if applis else [])):
        module_name = f"{virtual_env.stem}-{appli}"
        code = create_modulefile(virtual_env=virtual_env,
                                module_name=module_name,
                                module_category=f"{PACKAGE_NAME}-{appli}")
        if code:
            fails.append(appli)

        read_env(arguments=(virtual_env, appli))
        module_load(arguments=(virtual_env, virtual_env.stem, module_name))

    check_raise(condition=len(fails) > 0,
                exception_type=RuntimeError,
                message=f"The installation of the folowing appli failed : {fails}")

