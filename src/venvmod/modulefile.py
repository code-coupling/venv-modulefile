"""Environment module modification/installation."""

import os
import shutil
from pathlib import Path
import pathlib
import tarfile
from typing import List

from packaging import version
import requests

from venvmod.tools import (get_std_name, get_process_result, run_process, check_raise,
                           get_shell_name, PACKAGE_NAME, logger)


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


def add_command(filename: Path, line: str):
    """Appends a command to a modulefile

    Parameters
    ----------
    filename : Path
        File to modify
    line : str
        Line to append

    Raises
    ------
    FileNotFoundError
        If filename is not found
    """
    if not filename.exists():
        raise FileNotFoundError(f"Can't add command to non exsting file {filename}.")
    with open(filename, mode='a', encoding='utf-8') as modulefile:
        modulefile.write(line + "\n")


def get_version() -> str:
    """Gets modulefile version

    Returns
    -------
    str
        version as 'x.y.z', '0.0.0' if not found
    """
    result = get_process_result(command="module --version", capture_output=True)
    print(f"get_version: {result}")
    print(f"get_version: {result.stderr.decode()}")
    print(f"get_version: {result.stdout.decode()}")
    logger.debug(f"get_version: {result}")
    logger.debug(f"get_version: {result.stderr.decode()}")
    logger.debug(f"get_version: {result.stdout.decode()}")
    if 'VERSION=' in result.stderr.decode().split()[0]: # version < 4.0
        return result.stderr.decode().split()[0].split("=")[1]
    if 'Modules' == result.stderr.decode().split()[0]:
        return result.stderr.decode().split()[2]
    return "0.0.0"


def get_version_list(index: int = 0) -> List[int] or int:
    """Gets version as list

    Parameters
    ----------
    index : int, optional
        index in version, by default 0

    Returns
    -------
    List[int] or int
        version numbers or version number if index > 0
    """
    version_list = [int(id) for id in get_version().split(".")]
    return version_list[index-1] if index else version_list


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

    def run(self, verbose: bool = False, do_raise: bool = True) -> int:
        """run installer

        Parameters
        ----------
        verbose : bool, optional
            True to enable verbosity, by default False
        do_raise : bool, optional
            True to raise if fails, by default True

        Returns
        -------
        int
            return code
        """

        self._cache_directory.mkdir(parents=True, exist_ok=True)
        if Path(self._version_or_path).exists():
            src_directory = Path(self._version_or_path)
            build_directory = self._cache_directory / src_directory.name
        else:
            check_raise(condition=version.parse(self._version_or_path) < version.parse("4.6"),
                        exception_type=ValueError,
                        message="Version number for Modulefile must be >= 4.6"
                        )
            src_directory = self._cache_directory / f"modules-{self._version_or_path}"
            if not src_directory.exists():
                cwd = os.getcwd()
                os.chdir(self._cache_directory)
                try:
                    file = tarfile.open(  # pylint: disable=consider-using-with
                        fileobj=requests.get(
                            url="https://github.com/cea-hpc/modules/releases/download/"
                                f"v{self._version_or_path}/modules-{self._version_or_path}.tar.gz",
                            stream=True).raw,
                        mode="r|gz")
                    try:
                        file.extractall()
                    finally:
                        file.close()
                finally:
                    os.chdir(cwd)
            build_directory = src_directory

        build_directory.mkdir(parents=True, exist_ok=True)
        code = run_process(command=f"{src_directory}/configure --prefix={self._install_prefix}"
                                   " --with-python=$(which python3)",
                           verbose=verbose,
                           cwd=build_directory,
                           do_raise=do_raise)
        if code:
            return code

        return run_process(command="make clean && make && make install",
                           verbose=verbose,
                           cwd=build_directory,
                           do_raise=do_raise)


def upgrade_modulefile(virtual_env: Path, module_prefix: Path) -> int:
    """Upgrade modulefile in venv

    Parameters
    ----------
    virtual_env : Path
        Path to virtual env
    module_prefix : Path
        Modulefile install prefix

    Returns
    -------
    int
        return code
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
            if "you cannot run it directly" in line:
                tmp_file.write("\n"f". {init_file_path}{os.sep}$(ps -ocomm= -q $$)\n")
    pathlib.Path.replace(activate_tmp, activate_src)

    return 0


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

""",
    }


def create_modulefile(virtual_env: Path,
                      module_name: str = PACKAGE_NAME,
                      module_category: str = None,
                      log_load: str = "") -> int:
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
        return 0

    return 1


USE_MODULE_TEMPLATE = """module use "__module_dir__"
module_use_status=( $module_use_status $? )
"""
LOAD_MODULE_TEMPLATE = """module load '__module_name__'
module_load_status=( $module_load_status $? )
"""

UNLOAD_MODULE_TEMPLATE = """    module unload '__module_name__'
    module_unload_status=( $module_unload_status $? )
"""
UNUSE_MODULE_TEMPLATE = """    module unuse "__module_dir__"
    module_unuse_status=( $module_unuse_status $? )
"""


def upgrade_venv(virtual_env: Path):  # pylint: disable=too-many-branches,too-many-locals,too-many-statements
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
    bin_dir = virtual_env / "bin"

    activate_src = bin_dir / "activate"
    check_raise(not activate_src.is_file(), AssertionError,
                f'"activate" file is expected in {bin_dir}.')

    header_line = f"# This file is generated from {PACKAGE_NAME}"\
                  " from regular venv or virtualenv file."

    modulefile_name = get_std_name(virtual_env.name)
    module_directory = get_module_file_directory(virtual_env=virtual_env)
    unuse_module = UNUSE_MODULE_TEMPLATE.replace("__module_dir__", str(module_directory))
    unload_module = UNLOAD_MODULE_TEMPLATE.replace("__module_name__", modulefile_name)

    load_module = LOAD_MODULE_TEMPLATE.replace("__module_name__", modulefile_name)
    use_module = USE_MODULE_TEMPLATE.replace("__module_dir__", str(module_directory))

    with open(activate_src, "r", encoding='utf-8') as src_file:
        file_read = src_file.read()
        check_raise(header_line in file_read, AssertionError,
                    f"{virtual_env} is already a venv-modulefile environment.")

    with open(activate_src, "r", encoding='utf-8') as src_file:
        src_lines = src_file.readlines()

    tmp_path = virtual_env / "tmp" / PACKAGE_NAME
    tmp_path.mkdir(exist_ok=True, parents=True)

    activate_tmp = tmp_path / "activate"

    with open(activate_tmp, "w", encoding='utf-8') as tmp_file:

        def _write_in_file(tmp_file, line, to_write):
            if to_write:
                if to_write[0] == -1:
                    tmp_file.write(to_write[1])
                    tmp_file.write(line)
                elif to_write[0] == 1:
                    tmp_file.write(line)
                    tmp_file.write(to_write[1])
                elif to_write[0] == 0:
                    tmp_file.write(line)

        reset_is_done = 0
        deactivate_nondestructive = 0
        for count, line in enumerate(src_lines):
            to_write = None
            if count == 2:
                to_write = (-1, f"{header_line}\n")
            elif "deactivate () {" in line:
                to_write = (-1, """
function _test_deactivate_status(){
module_status=( $module_unuse_status $module_unload_status )
unset module_unuse_status
unset module_unload_status
unset -f _test_deactivate_status
for return_code in $module_status ; do
    if (( $return_code > 0 )); then return $return_code; fi
done
}\n\n""")
            elif "unset -f deactivate" in line:
                to_write = (1, "        _test_deactivate_status\n        return $?\n")
            elif "reset old environment variables" in line:
                to_write = (-1, "\n    # Unload non-Python dependencies\n"
                           + unload_module + unuse_module + "\n")
                reset_is_done += 1
            elif "deactivate nondestructive" in line:
                to_write = (1, "\n# Load non-Python dependencies\n" + use_module + load_module)
                deactivate_nondestructive += 1
            else:
                to_write = (0, "")

            _write_in_file(tmp_file, line, to_write)

        if reset_is_done != 1:
            logger.error(
                "'reset old environment variables' has been found %s"
                " times in activate script. It is expectet to be 1 time.", reset_is_done)
        if deactivate_nondestructive != 1:
            logger.error(
                "'deactivate nondestructive' has been found %s"
                " times in activate script. It is expectet to be 1 time.",
                deactivate_nondestructive)

        tmp_file.write("""
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
""")

    shutil.copyfile(activate_tmp, activate_src)
    shutil.rmtree(tmp_path)
