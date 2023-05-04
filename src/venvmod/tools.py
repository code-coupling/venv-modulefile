"""Regroups tool for the package.
"""
import logging
import os
from pathlib import Path
import shlex
from subprocess import run as _run_process, CompletedProcess, PIPE
from typing import List

from . import __name__ as PACKAGE_NAME

logger = logging.getLogger(__name__)

def check_raise(condition: bool, exception_type: Exception, message: str):
    """Chack if a condition is True to raise

    Parameters
    ----------
    condition : bool
        Condition to be True to raise
    exception_type : Exception
        Exception to raise
    message : str
        Message for the exception

    Raises
    ------
    exception_type
        _description_
    """
    if condition:
        logger.error(message)
        raise exception_type(message)


def get_shell_name_command() -> str:
    """Gets command to get shell name..

    Returns
    -------
    str
        Command as str.
    """
    return '"import os; print(os.path.basename(os.readlink(os.path.join(os.sep, \'proc\', str(os.getppid()), \'exe\'))))"'
    # return '"import os; print(os.path.basename(os.environ[\'SHELL\']))"'

def get_shell_name() -> str:
    """Gets current shell name.

    Returns
    -------
    str
        shell name
    """
    return os.path.basename(os.environ["SHELL"])
    return os.path.basename(os.readlink(os.path.join(os.sep, "proc", str(os.getppid()), "exe")))


def get_process_result(command: str, capture_output: bool, cwd: str or Path = None) -> CompletedProcess:
    """Run procces and get results

    Parameters
    ----------
    command : str
        command to run
    capture_output : bool
        True to capture output
    cwd : str or Path, optional
        execution directory, by default None

    Returns
    -------
    CompletedProcess
        Process result
    """

    pipe = PIPE if capture_output else None
    return _run_process([get_shell_name(), '-c', command], stderr=pipe, stdout=pipe, cwd=cwd)


def run_process(command: str, verbose: bool, do_raise: bool, cwd: str or Path = None) -> int:
    """Run process

    Parameters
    ----------
    command : str
        command to run
    verbose : bool
        to enable verbosity
    do_raise : bool
        If True, raise if fails
    cwd : str or Path, optional
        execution directory, by default None

    Returns
    -------
    int
        return code
    """

    result = get_process_result(command=command, capture_output=not verbose, cwd=cwd)
    if do_raise:
        result.check_returncode

    return result.returncode

def remove_duplicates(input_list: List) -> List:
    """Removes duplicate values in a list.

    Parameters
    ----------
    input_list : List
        Input list.

    Returns
    -------
    List
        Output list.
    """
    return [value for index, value in enumerate(input_list) if value not in input_list[index+1:]]
