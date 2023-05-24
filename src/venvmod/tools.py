"""Regroups tool for the package.
"""
import logging
from typing import List

import shellingham

from venvmod import __name__ as PACKAGE_NAME

logger = logging.getLogger(PACKAGE_NAME)


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


def get_shell_name() -> str:
    """Gets current shell name.

    Returns
    -------
    str
        shell name
    """
    return shellingham.detect_shell()[0]


def get_shell_command() -> str:
    """Gets current shell name.

    Returns
    -------
    str
        shell command
    """
    return shellingham.detect_shell()[1]


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


def get_std_name(name: str) -> str:
    """Transform a name in standard name:
        - lower case
        - '_' -> '-'

    Parameters
    ----------
    name : str
        input name

    Returns
    -------
    str
        standardized name
    """

    return name.lower().replace("_", "-")
