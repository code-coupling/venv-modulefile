"""This module defines commands available to cli.
"""
import argparse
import logging
from pathlib import Path
from typing import Any, List, Tuple

from ..modulefile import get_module_file_directory
from ..tools import logger, get_std_name


def get_parser(  # name: str,  # pylint: disable=too-many-arguments
               description: str,  # pylint: disable=too-many-arguments
               positionals: List[Tuple[str, Any, str, Any]] = None,
               with_appli: bool = False,
               options: List[Tuple[str, Any, str]] = None,
               args: List = None) -> argparse.Namespace:
    """Create a parser for entry-points.

    Parameters
    ----------
    description : str
        Description of the command
    positionals: List[Tuple[str, Any, str, Any]], optional
        list of positionals ('name', default, 'help', nargs), by default None
    with_appli : bool, optional
        True to enable '--appli' option, by default False
    options: List[Tuple[str, Any, str]], optional
        list of options defined as ('--option-name', default, 'help'), by default None
    args : List, optional
        list of arguments if not given throug cli, by default None

    Returns
    -------
    argparse.Namespace
        parsed arguments
    """

    parser = argparse.ArgumentParser(description=description)

    parser.add_argument("virtual_env", metavar="VIRTUAL_ENV",
                        help="Path to the virtual env to modify")

    parser.add_argument('--verbose', action='store_true', help='To display the result.')

    if with_appli:
        parser.add_argument('--appli', metavar='appli', default="",
                            help='Name of the appli modulefile (case insensitive)')
    if positionals:
        for positional in positionals:
            print("get_parser positional", positional)
            parser.add_argument(positional[0],
                                metavar=positional[0].replace("-", "_"),
                                default=positional[1],
                                help=positional[2],
                                nargs=positional[3])

    if options:
        for option in options:
            parser.add_argument(f"--{option[0]}",
                                metavar=option[0].replace("-", "_"),
                                default=option[1],
                                help=option[2])

    parsered = parser.parse_args(args)
    if parsered.verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    if not Path(parsered.virtual_env).absolute().is_dir():
        raise FileNotFoundError(f"virtual environment '{parsered.virtual_env}' does not exist.")

    return parsered


def get_module_filepath(virtual_env: Path, appli_name: str = None) -> str:
    """_summary_

    Parameters
    ----------
    virtual_env : pathlib.Path
        name or path to the virtual env
    appli_name : str, optional
        name of the application, by default None

    Returns
    -------
    Path
        name of the module file associated to the appli
    """
    module_name = get_std_name(f"{virtual_env.name}-{appli_name}"
                               if appli_name and appli_name != virtual_env.name
                               else virtual_env.name)

    logger.debug("get_module_filepath: module name = '%s' appli name = '%s' venv name = '%s'",
                 module_name, appli_name, virtual_env.name)
    return get_module_file_directory(virtual_env=virtual_env) / module_name
