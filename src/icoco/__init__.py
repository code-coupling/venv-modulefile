"""
ICoCo file common to several codes
Version 2 -- 02/2021

WARNING: this file is part of the official ICoCo API and should not be modified.
The official version can be found at the following URL:

https://github.com/cea-trust-platform/icoco-coupling

The package ICoCo (Interface for code coupling) encompasses all the classes
and methods needed for the coupling of codes.
See :class:`icoco.problem.Problem` to start with.

"""

import os

with open(os.path.join(os.path.dirname(__file__), "VERSION")) as file:
    __version__ = file.read().strip()

from .utils import ICOCO_VERSION, ICOCO_MAJOR_VERSION, ICOCO_MINOR_VERSION, ValueType
try:
    from .utils import medcoupling
except ImportError:
    pass

from .exception import WrongContext, WrongArgument, NotImplementedMethod

from .problem_wrapper import ProblemWrapper
from .problem import Problem
