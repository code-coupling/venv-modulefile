"""
ICoCo file common to several codes
Version 2 -- 02/2021

WARNING: this file is part of the official ICoCo API and should not be modified.
The official version can be found at the following URL:

https://github.com/cea-trust-platform/icoco-coupling
"""

from enum import Enum

try:
    import medcoupling # pylint: disable=unused-import
except ImportError:
    import warnings
    warnings.warn(message="medcoupling module not found",
                  category=ImportWarning)

ICOCO_VERSION="2.0"
ICOCO_MAJOR_VERSION=2
ICOCO_MINOR_VERSION=0

class ValueType(Enum):
    """The various possible types for fields or scalar values."""

    Double = 0
    """Double scalar value or field type"""
    Int = 1
    """Int scalar value or field type"""
    String = 2
    """String scalar value or field type"""

try:
    from mpi4py.MPI import Intracomm as MPIComm # type: ignore # pylint: disable=unused-import
except ModuleNotFoundError:
    class MPIComm: # pylint: disable=too-few-public-methods
        """Basic class for type hinting when mi4py is not available"""
