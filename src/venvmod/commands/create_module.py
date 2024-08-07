"""Commands to create a modulefile."""

from pathlib import Path
from typing import List

from ..tools import get_std_name
from . import get_parser
from .append_module import module_load, read_env as read_env_vars
from ..modulefile import (ModuleInstaller, upgrade_modulefile, create_modulefile,
                          upgrade_venv, test_if_already_init)

from ..tools import PACKAGE_NAME, check_raise, remove_duplicates


def initialize(virtual_env: Path = None,
               version_or_path: str = "5.4.0",
               read_env: bool = False) -> int:
    """Initialize a venv-modulefile environment

    Parameters
    ----------
    virtual_env : Path, optional
        If None, arguments are read from :func:`venvmod.commands.get_parser` function,
        else the path to the virtual env, by default None
    version_or_path : str, optional
        Modulefile version to use if not found or version < 4.6.
        It can be a source directory to avoid donloading, by default "5.4.0"
    read_env : bool, optional
        Read environment variables associated to the appli, by default False

    Returns
    -------
    int
        return code
    """

    if virtual_env is None:
        options = get_parser(
            description="Initialize Modulefile in venv.",
            positionals=None,
            with_appli=False,
            options=[("modulefile-version", version_or_path,
                      "Modulefile version to use if not found or version < 4.6."
                      " It can be a source directory to avoid downloading"),
                     ("activate-log", "", "Log message when the module is loaded."),
                     ("read-env", False, "Read environment variables. 'See cmd-read-env'")])
        virtual_env = Path(options.virtual_env).absolute()
        if options.modulefile_version:
            version_or_path = options.modulefile_version
        read_env = options.read_env

    test_if_already_init(virtual_env=virtual_env)

    install_prefix = virtual_env / "opt" / "modulefiles"
    if not (install_prefix / "init").exists():
        ModuleInstaller(install_prefix=install_prefix,
                        version_or_path=version_or_path,
                        cache_directory=virtual_env / ".cache").run(
                            verbose=options.verbose)

        upgrade_modulefile(virtual_env=virtual_env, module_prefix=install_prefix)

    create_modulefile(virtual_env=virtual_env,
                      module_name=get_std_name(virtual_env.name),
                      module_category=PACKAGE_NAME,
                      log_load=options.activate_log)

    if read_env:
        read_env_vars(arguments=(virtual_env, get_std_name(virtual_env.name)))

    return upgrade_venv(virtual_env=virtual_env)


def add_appli(virtual_env: Path = None,
              applis: List[str] = None,
              read_env: bool = False,
              disconnect: bool = False) -> int:
    """Add application modulefiles to the environment.

    This call also use the :func:`venvmod.commands.append_module.read_env` function for each appli.

    Parameters
    ----------
    virtual_env : Path, optional
        If None, arguments are read from :func:`venvmod.commands.get_parser` function,
        else the path to the virtual env, by default None
    applis : List[str], optional
        List of module file to create in addition to those given through cli, by default None
    read_env : bool, optional
        Read environment variables associated to the appli, by default False
    disconnect : bool, optional
        True to avoid loading appli when virtual env is loaded, by default False
    """
    if virtual_env is None:
        options = get_parser(description="Initialize Modulefile for an application.",
                             positionals=[("APPLI", [],
                                          "Appli name(s) to add to the environment.", '+')],
                             with_appli=False,
                             options=[
                                 ("read-env", False,
                                  "Read environment variables. 'See cmd-read-env'"),
                                 ("disconnect", False,
                                  "Disconnects applis loading at activate.")
                             ])
        virtual_env = Path(options.virtual_env).absolute()
        virtual_env_name = get_std_name(virtual_env.name)
        read_env = options.read_env
        disconnect = options.disconnect
    else:
        virtual_env_name = virtual_env.name

    fails = []
    for appli in remove_duplicates(options.APPLI + (applis if applis else [])):
        appli_name = get_std_name(appli)
        module_name = f"{virtual_env_name}-{appli_name}"
        if create_modulefile(virtual_env=virtual_env,
                             module_name=module_name,
                             module_category=f"{PACKAGE_NAME}-{appli_name}"):
            fails.append(appli)

        if read_env:
            read_env_vars(arguments=(virtual_env, appli_name))
        if not disconnect:
            module_load(arguments=(virtual_env, "", module_name))

    check_raise(condition=len(fails) > 0,
                exception_type=RuntimeError,
                message=f"The installation of the folowing appli failed : {fails}")
    return 0
