"""
ICoCo file common to several codes
Version 2 -- 02/2021

WARNING: this file is part of the official ICoCo API and should not be modified.
The official version can be found at the following URL:

https://github.com/cea-trust-platform/icoco-coupling

This module contains the exceptions for ICoCo specifications.
"""


class WrongContext(Exception):
    """Exception raised when an ICoCo method is called at the wrong place.

    This exception is raised whenver an ICoCo method is called when it shouldn't.
    This is for example the case if the icoco.Problem.initTimeStep() method is called when
    icoco.Problem.initialize() hasn't been called yet.
    """

    def __init__(self, prob: str, method: str, precondition: str) -> None:
        """Constructor.

        Parameters
        ----------
        prob : str
            problem name
        method : str
            name of the method where the exception occurred
        precondition : str
            detail of the condition that wasn't met
        """
        super().__init__(f"WrongContext in Problem instance with name: '{prob}'""\n"
                         f" in method '{method}' : {precondition}")


class WrongArgument(ValueError):
    """Exception raised when an ICoCo method is called with an invalid argument.

    This exception is raised whenver an ICoCo method is called with inappropriate arguments.
    This is for example the case if the Problem::getOutputField() is called with a non-existing
    field name.
    """

    def __init__(self, prob: str, method: str, arg: str, condition: str) -> None:
        """Constructor.

        Parameters
        ----------
        prob : str
            problem name
        method : str
            name of the method where the exception occurred
        arg : str
            name of the faulty argument
        condition : str
            condition detail of the condition that wasn't met
        """
        super().__init__(f"WrongArgument in Problem instance with name: '{prob}'""\n"
                         f" in method '{method}', argument '{arg}' : {condition}")

class NotImplementedMethod(NotImplementedError):
    """Exception raised when one tries to call an ICoCo method which is not implemented.

    By default all ICoCo methods raise this exception. The code implementing the norm
    should derive the Problem class and override (at least partially) this default
    implementation.
    """

    def __init__(self, prob: str, method: str) -> None:
        """Constructor.

        Parameters
        ----------
        prob : str
            problem name
        method : str
            name of the method where the exception occurred
        """
        super().__init__(f"NotImplemented in Problem instance with name: '{prob}'""\n"
                         f" in method '{method}'")
