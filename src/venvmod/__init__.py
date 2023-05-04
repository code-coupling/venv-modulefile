import pathlib as _pathlib

from . import modulefile
from . import tools

__version__ = (_pathlib.Path(__file__).parent.resolve() / "VERSION").read_text(
    encoding="utf-8").strip()

__copyright__ = '2023, CEA'
__author__ = 'CEA'
