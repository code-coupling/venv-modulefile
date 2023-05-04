
import importlib
from typing import List
from . import get_parser


def _test_module_import(module_name: str, verbose: bool) -> str:
    """Test module import.

    Parameters
    ----------
    module_name : str
        Name of the module to test.
    verbose : bool
        True to print result.

    Returns
    -------
    str
        Import error description if any. Else None.
    """

    error = None
    try:
        module = importlib.import_module(module_name)
    except ImportError as err:
        error = err

    if verbose:
        print(">>> import {}:".format(module_name))
        if error:
            print("  FAILED {}".format(error))
        else:
            print("  {}".format(module.__file__))
    return error

def test_imports(arguments: List[str] = None) -> int:
    """Test import modules

    Parameters
    ----------
    arguments : List[str], optional
        modules to test, by default None

    Returns
    -------
    int
        return code
    """
    if arguments is None:
        options = get_parser(description="Test module import.",
                             help_arguments="List of Python modules to test.",
                             with_appli=False,
                             with_verbose=True)
        arguments = options.arguments

    if options.verbose:
        print("Testing env :")

    failed = {}

    for module in set(arguments):
        error = _test_module_import(module, options.verbose)
        if error:
            failed[module] = error

    return len(failed)

