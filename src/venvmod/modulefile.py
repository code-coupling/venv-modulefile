"""Environment module modification/installation."""

import os
import shutil
from pathlib import Path
import pathlib
import subprocess
import tarfile

import inspect
from packaging import version
import requests

from venvmod.tools import (get_std_name, get_shell_command, check_raise,
                           get_shell_name, PACKAGE_NAME)


def get_module_file_directory(virtual_env: Path) -> Path:
    """Gets the modulefiles directory

    Parameters
    ----------
    virtual_env : Path
        Path to virtual env

    Returns
    -------
    Path
        virtual_env path + "/etc/modulefiles"
    """
    return virtual_env.absolute() / "etc" / "modulefiles"


ACTIVATE_HEADER_LINE = (f"# This file is generated from {PACKAGE_NAME}"
                        " from regular venv or virtualenv file.")


def test_if_already_init(virtual_env: Path):
    """checks if venv-modulefile is already initialized.

    Parameters
    ----------
    virtual_env : Path
        Path to virtual env
    """
    with (virtual_env / "bin" / "activate").open(mode="r", encoding='utf-8') as src_file:
        check_raise(ACTIVATE_HEADER_LINE in src_file.read(), AssertionError,
                    f"{virtual_env} is already a venv-modulefile environment.")


class ModuleInstaller:  # pylint: disable=too-few-public-methods
    """Class to install Environment Module.
    """

    def __init__(self,
                 version_or_path: str,
                 install_prefix: str or Path,
                 cache_directory: str or Path) -> None:

        self._version_or_path: str = version_or_path
        self._install_prefix: Path = Path(install_prefix)
        self._cache_directory: Path = Path(cache_directory)

    def run(self, verbose: bool = False):
        """run installer

        Parameters
        ----------
        verbose : bool, optional
            True to enable verbosity, by default False
        """

        self._cache_directory.mkdir(parents=True, exist_ok=True)
        if Path(self._version_or_path).exists():
            build_directory = self._cache_directory / Path(self._version_or_path).name
            shutil.copytree(Path(self._version_or_path), build_directory, symlinks=True)
        else:
            check_raise(condition=version.parse(self._version_or_path) < version.parse("4.6"),
                        exception_type=ValueError,
                        message="Version number for Modulefile must be >= 4.6,"
                                f" found {self._version_or_path}."
                        )
            build_directory = self._cache_directory / f"modules-{self._version_or_path}"
            if not build_directory.exists():
                cwd = os.getcwd()
                os.chdir(self._cache_directory)
                try:
                    tar_file = (Path(__file__).parent.absolute().resolve() /
                                "modulefiles_src" / f"modules-{self._version_or_path}.tar.gz")
                    if tar_file.exists():
                        file = tarfile.open(  # pylint: disable=consider-using-with
                            tar_file,
                            mode="r|gz")
                    else:
                        file = tarfile.open(  # pylint: disable=consider-using-with
                            fileobj=requests.get(
                                url="https://github.com/cea-hpc/modules/releases/download/"
                                    f"v{self._version_or_path}/"
                                    f"modules-{self._version_or_path}.tar.gz",
                                stream=True,
                                timeout=120.0).raw,
                            mode="r|gz")
                    try:
                        if 'filter' in inspect.signature(file.extractall).parameters:
                            file.extractall(filter='tar')
                        else:
                            file.extractall()
                    finally:
                        file.close()
                finally:
                    os.chdir(cwd)

        pipe = subprocess.PIPE if not verbose else None
        for command in [
                [f"{build_directory}/configure"] + [
                 f"--prefix={self._install_prefix}",
                 f"--with-modulepath={self._install_prefix.parent.parent / 'etc' / 'modulefiles'}",
                 "--enable-modulespath",
                 "--with-python=$(which python3)"] + (
                     ["--enable-set-shell-startup"] if "BASH_ENV" in os.environ else []),
                ["make", "clean"],
                ["make"],
                ["make", "install"]]:
            subprocess.run([get_shell_command(), "-c", " ".join(command)],
                           stderr=pipe, stdout=pipe, cwd=build_directory, check=True)


def upgrade_modulefile(virtual_env: Path, module_prefix: Path):
    """Upgrade modulefile in venv

    Parameters
    ----------
    virtual_env : Path
        Path to virtual env
    module_prefix : Path
        Modulefile install prefix
    """

    activate_src = virtual_env / "bin" / "activate"
    check_raise(not activate_src.is_file(), AssertionError,
                f'"activate" file {activate_src} not found.')

    with open(activate_src, "r", encoding='utf-8') as src_file:
        src_lines = src_file.readlines()

    tmp_path = virtual_env / "tmp" / PACKAGE_NAME
    tmp_path.mkdir(parents=True, exist_ok=True)

    activate_tmp = tmp_path / "activate"

    init_file_path = module_prefix / "init"

    init_file = init_file_path / get_shell_name()
    check_raise(not os.path.isfile(init_file), AssertionError,
                f'Environment Module "init" file {init_file} not found.')

    with open(activate_tmp, "w", encoding='utf-8') as tmp_file:
        for line in src_lines:
            tmp_file.write(line)
            if "you cannot run it directly" in line.lower():
                tmp_file.write("\n"f". {init_file_path}{os.sep}$(ps -ocomm= -q $$)\n")
    pathlib.Path.replace(activate_tmp, activate_src)


MODULE_TEMPLATES = {"TCL": """#%Module -*- tcl -*-
##
## modulefile for __name__
##
#Global infos
set              category             __category__
set              name                 __name__

proc ModulesHelp { } {
  puts stderr "\tAdds $name to your environment,"
}

module-whatis "adds $name to your environment"

__log_load__

#conflicts, prereq
conflict $category

"""}


def create_modulefile(virtual_env: Path,
                      module_name: str = PACKAGE_NAME,
                      module_category: str = None,
                      log_load: str = ""):
    """Creates a modulefile.

    Parameters
    ----------
    module_name : str
        Name of the module to create
    module_directory : Path
        Module directory
    module_category : str, optional
        Module category, by default None
    log_load : str, optional
        Loag edited at load, by default ""
    """

    module_directory = get_module_file_directory(virtual_env=virtual_env)
    module_directory.mkdir(parents=True, exist_ok=True)

    module_file_name = module_directory / module_name

    module_file = MODULE_TEMPLATES["TCL"].replace("__name__", module_name)
    module_file = module_file.replace("__category__", module_category)

    to_replace = ""
    if log_load:
        log_load = log_load.replace('[', r'\[').replace(']', r'\]')
        to_replace = ('if { [ module-info mode load ] } {\n'
                      f'    puts stderr "{log_load}"\n'
                      '}')
    module_file = module_file.replace("__log_load__", to_replace)

    with open(module_file_name, "w", encoding='utf-8') as mod_file:
        mod_file.write(module_file)


SHELL_TEST_DEACTIVATE_STATUS = """
function _test_deactivate_status(){
    module_status=( $module_unuse_status $module_unload_status )
    unset module_unuse_status
    unset module_unload_status
    unset -f _test_deactivate_status
    for return_code in $module_status ; do
        if (( $return_code > 0 )); then return $return_code; fi
    done
}

"""

UNLOAD_MODULES = """
    # Unload non-Python dependencies
    module unload '{}'
    module_unload_status=$?
    module unuse '{}'
    module_unuse_status=$?

"""

LOAD_MODULES = """
# Load non-Python dependencies
module use '{}'
module_use_status=$?
module load '{}'
module_load_status=$?
"""

SHELL_TEST_ACTIVATE_STATUS = """
function _test_activate_status(){
    module_status=( $module_use_status $module_load_status )
    unset module_use_status
    unset module_load_status
    unset -f _test_activate_status
    for return_code in $module_status ; do
       if (( $return_code > 0 )); then return $return_code; fi
    done
}
_test_activate_status
"""


def upgrade_venv(virtual_env: Path):
    """Ugrade virtual env with modulefile at activate and deactivate.

    Parameters
    ----------
    env_prefix : Path
        Path to environment.

    Raises
    ------
    AssertionError
        If the activate script is not found.
    AssertionError
        If the module is already loaded frome the script but from another modulefile directory.
    """

    activate_src = virtual_env / "bin" / "activate"
    check_raise(not activate_src.is_file(), AssertionError,
                f'{activate_src} file not found.')

    modulefile_name = get_std_name(virtual_env.name)
    module_directory = get_module_file_directory(virtual_env=virtual_env)

    test_if_already_init(virtual_env=virtual_env)

    with open(activate_src, "r", encoding='utf-8') as src_file:
        src_lines = src_file.readlines()

    tmp_path = virtual_env / "tmp" / PACKAGE_NAME
    tmp_path.mkdir(exist_ok=True, parents=True)

    activate_tmp = tmp_path / "activate"

    with activate_tmp.open("w", encoding='utf-8') as tmp_file:

        for count, line in enumerate(src_lines):
            to_write = ()
            if count == 2:
                to_write = (0, f"{ACTIVATE_HEADER_LINE}\n")
            elif "deactivate () {" in line:
                to_write = (0, SHELL_TEST_DEACTIVATE_STATUS)
            elif "unset -f deactivate" in line:
                to_write = (1, "        _test_deactivate_status\n        return $?\n")
            elif line.split() == ["unset", "VIRTUAL_ENV"]:
                to_write = (1, UNLOAD_MODULES.format(modulefile_name, str(module_directory)))
            elif "deactivate nondestructive" in line:
                to_write = (1, LOAD_MODULES.format(str(module_directory), modulefile_name))
            else:
                to_write = (0, "")

            tmp_file.write(line + to_write[1] if to_write[0] else to_write[1] + line)

        tmp_file.write(SHELL_TEST_ACTIVATE_STATUS)

    shutil.copyfile(activate_tmp, activate_src)
    shutil.rmtree(tmp_path)
