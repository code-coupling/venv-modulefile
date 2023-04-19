import argparse
from pathlib import Path
from typing import List

from ..modulefile import get_module_file_directory

def get_parser(description: str,
               help_arguments: str = None,
               with_appli: bool = False,
               with_verbose: bool = False,
               args: List = None) -> argparse.Namespace:

    parser = argparse.ArgumentParser(description=description)

    parser.add_argument("virtual_env",
                        help="Path to the virtual env to modify")
    if with_verbose:
        parser.add_argument('--verbose', action='store_true', help='To display the result.')

    if with_appli:
        parser.add_argument('--appli', metavar='appli', default="",
                        help='Name of the appli modulefile (case insensitive)')
    if help_arguments:
        parser.add_argument('arguments', nargs='+', default=[], help=help_arguments)

    return parser.parse_args(args)

def get_module_filename(virtual_env_name: str, appli_name: str = None) -> str:
    virtual_env = Path(virtual_env_name).absolute()
    name = (appli_name if appli_name else virtual_env.name).lower()
    virtual_env = virtual_env / get_module_file_directory(virtual_env)
    return str(virtual_env / name)
