"""Test ``venvmod`` package"""

import os
from pathlib import Path
import shutil
import subprocess
from typing import Dict, List


from venvmod.tools import get_shell_command


def get_results(result: subprocess.CompletedProcess, xfail: bool = False) -> bool:
    """Gets result informations.

    Parameters
    ----------
    result : subprocess.CompletedProcess
        Subprocess result
    xfail : bool, optional
        Expeted to fail if True, by default False

    Returns
    -------
    bool
        True if success
    """
    success = (result.returncode != 0) if xfail else (result.returncode == 0)
    print(('\033[92m' if success else '\033[91m') + f"cmd: '{result.args[0]}' xfail: '{xfail}'")
    for out_typ, content in {'stderr': result.stderr, 'stdout': result.stdout}.items():
        print(f"{out_typ}: {content.decode()}")
    print('\033[0m')
    return success


def venvmod_cmd(args: List[str], xfail: bool, err_msg: str = None, env: Dict[str, str] = None):
    """Execute command

    Parameters
    ----------
    args : List[str]
        Argument list
    xfail : bool
        Expeted to fail if True
    err_msg : str, optional
        Error message to check, default = None
    env : Dict[str, str]
        Environment to pass to subprocess, default = None
    """
    result = subprocess.run(args=args + ["--verbose"],  # pylint: disable=subprocess-run-check
                            stderr=subprocess.PIPE, stdout=subprocess.PIPE, env=env)
    success = get_results(result=result, xfail=xfail)

    if err_msg:
        assert err_msg in result.stderr.decode()

    assert success


def all_venvmod_commands(venv_path: Path, test_scripts: List, appli: str = None):
    """Tests all cli venvmod commands.

    Parameters
    ----------
    venv_path : Path
        venv directory
    appli : str, optional
        appli name if any, by default None
    """

    appli = ["--appli", appli] if appli else []

    venv_pathname = str(venv_path)

    venvmod_cmd(args=["venvmod-cmd-module-use", venv_pathname] + appli,
                xfail=True, err_msg="the following arguments are required: PATH")
    venvmod_cmd(args=["venvmod-cmd-module-use", venv_pathname,
                      "/path/to/toto"] + appli, xfail=False)
    venvmod_cmd(args=["venvmod-cmd-module-use", venv_pathname,
                      "/path/to/toto1", "/path/to/toto2"] + appli, xfail=False)

    venvmod_cmd(args=["venvmod-cmd-module-load", venv_pathname] + appli,
                xfail=True, err_msg="the following arguments are required: MODULE")
    venvmod_cmd(args=["venvmod-cmd-module-load", venv_pathname,
                      "test_module"] + appli, xfail=False)
    venvmod_cmd(args=["venvmod-cmd-module-load", venv_pathname,
                      "test_module1", "test_module2"] + appli, xfail=False)

    venvmod_cmd(args=["venvmod-cmd-source-sh", venv_pathname] + appli,
                xfail=True, err_msg="the following arguments are required: SHELL, SCRIPT")
    venvmod_cmd(args=["venvmod-cmd-source-sh", venv_pathname, "bash"] + appli,
                xfail=True, err_msg="the following arguments are required: SCRIPT")
    venvmod_cmd(args=["venvmod-cmd-source-sh", venv_pathname,
                      "bash", f"{test_scripts[0]}"] + appli, xfail=False)
    venvmod_cmd(args=["venvmod-cmd-source-sh", venv_pathname,
                      "bash", f"{test_scripts[1]}", "arg"] + appli, xfail=False)
    venvmod_cmd(args=["venvmod-cmd-source-sh", venv_pathname,
                      "bash", f"{test_scripts[2]}", "arg1", "arg2"] + appli, xfail=False)

    venvmod_cmd(args=["venvmod-cmd-prepend-path", venv_pathname] + appli,
                xfail=True, err_msg="the following arguments are required: ENV_VAR, PATH")
    venvmod_cmd(args=["venvmod-cmd-prepend-path", venv_pathname, "PATH"] + appli,
                xfail=True, err_msg="the following arguments are required: PATH")
    venvmod_cmd(args=["venvmod-cmd-prepend-path", venv_pathname,
                      "PATH", "value"] + appli, xfail=False)
    venvmod_cmd(args=["venvmod-cmd-prepend-path", venv_pathname,
                      "PATH", "value1", "value2"] + appli, xfail=False)

    venvmod_cmd(args=["venvmod-cmd-append-path", venv_pathname] + appli,
                xfail=True, err_msg="the following arguments are required: ENV_VAR, PATH")
    venvmod_cmd(args=["venvmod-cmd-append-path", venv_pathname, "PATH"] + appli,
                xfail=True, err_msg="the following arguments are required: PATH")
    venvmod_cmd(args=["venvmod-cmd-append-path", venv_pathname,
                      "PATH", "value"] + appli, xfail=False)
    venvmod_cmd(args=["venvmod-cmd-append-path", venv_pathname,
                      "PATH", "value1", "value2"] + appli, xfail=False)

    venvmod_cmd(args=["venvmod-cmd-setenv", venv_pathname] + appli,
                xfail=True, err_msg="the following arguments are required: VARIABLE, VALUE")
    venvmod_cmd(args=["venvmod-cmd-setenv", venv_pathname, "TEST_VAR"] + appli,
                xfail=True, err_msg="the following arguments are required: VALUE")
    venvmod_cmd(args=["venvmod-cmd-setenv", venv_pathname,
                      "TEST_VAR", "test_value"] + appli, xfail=False)
    venvmod_cmd(args=["venvmod-cmd-setenv", venv_pathname,
                      "TEST_VAR2", "test_value1", "test_value2"] + appli,
                xfail=True, err_msg="unrecognized arguments: test_value2")

    venvmod_cmd(args=["venvmod-cmd-remove-path", venv_pathname] + appli,
                xfail=True, err_msg="the following arguments are required: VARIABLE, PATH")
    venvmod_cmd(args=["venvmod-cmd-remove-path", venv_pathname, "TEST_PATH"] + appli,
                xfail=True, err_msg="the following arguments are required: PATH")
    venvmod_cmd(args=["venvmod-cmd-remove-path", venv_pathname,
                      "TEST_PATH", "test_path"] + appli, xfail=False)
    venvmod_cmd(args=["venvmod-cmd-remove-path", venv_pathname,
                      "TEST_PATH2", "test_path1", "test_path2"] + appli,
                xfail=True, err_msg="unrecognized arguments: test_path2")

    venvmod_cmd(args=["venvmod-cmd-set-alias", venv_pathname] + appli,
                xfail=True, err_msg="the following arguments are required: ALIAS, VALUE")
    venvmod_cmd(args=["venvmod-cmd-set-alias", venv_pathname, "test_cmd"] + appli,
                xfail=True, err_msg="the following arguments are required: VALUE")
    venvmod_cmd(args=["venvmod-cmd-set-alias", venv_pathname,
                      "test_cmd", "cmd1"] + appli, xfail=False)
    venvmod_cmd(args=["venvmod-cmd-set-alias", venv_pathname,
                      "test_cmd", "cmd1", "cmd2"] + appli,
                xfail=True, err_msg="unrecognized arguments: cmd2")


def check_venv() -> Path:
    """Check virtual environment.

    Returns
    -------
    Path
        Path to the virtual environment.

    Raises
    ------
    EnvironmentError
        If not executed in a virtual environment.
    """

    if "VIRTUAL_ENV" not in os.environ:
        raise EnvironmentError("Expected to be run a venv.")

    venv_path = Path(os.environ["VIRTUAL_ENV"])

    if (venv_path / "bin" / "_activate").exists():
        shutil.copyfile(src=venv_path / "bin" / "_activate",
                        dst=venv_path / "bin" / "activate")
    else:
        shutil.copyfile(src=venv_path / "bin" / "activate",
                        dst=venv_path / "bin" / "_activate")

    for subdir in ["etc", "opt", ".cache"]:
        if (venv_path / subdir).exists():
            shutil.rmtree(venv_path / subdir)

    return venv_path


def test_venvmod_cmds(): #  pylint: disable=too-many-statements
    """Tests all commands."""

    venv_path = check_venv()

    # xfail before initialize
    venvmod_cmd(args=["venvmod-cmd-setenv", str(venv_path), "VAR", "value"],
                xfail=True, err_msg="You can\'t add command to non exsting modulefile")

    # xfail not a venv
    venvmod_cmd(args=["venvmod-initialize", "/not/a/dir"], xfail=True)

    # Initialize
    test_scripts = ["test_script", "test_script1", "test_script2"]
    (venv_path / "etc" / "modulefiles").mkdir(exist_ok=True, parents=True)
    for index, test_script in enumerate(test_scripts):
        test_scripts[index] = venv_path / "etc" / "modulefiles" / test_script
        test_scripts[index].write_text(data="echo $@\n", encoding='utf-8')
    for test_module in ["test_module", "test_module1", "test_module2"]:
        (venv_path / "etc" / "modulefiles" / test_module).write_text(
            data="#%Module -*- tcl -*-\n", encoding='utf-8')

    def create_subenv(prefix: str):
        sub_env = os.environ.copy()
        sub_env.update({
            f"{prefix}_LD_LIBRARY_PATH": "/path/to/lib1:/path/to/lib2",
            f"{prefix}_PYTHONPATH": "/path/to/packages1:/path/to/packages2",
            f"{prefix}_PATH": "/path/to/bin1:/path/to/bin2",
            f"{prefix}_MODULE_USE": "/path/to/modules1 /path/to/modules2",
            f"{prefix}_MODULEFILES": "test_module1 test_module2",
            f"{prefix}_SOURCEFILES": f"bash {test_scripts[0]} arg1 arg2; bash {test_scripts[1]}",
            f"{prefix}_EXPORTS": "VAR1=value1 VAR2=value2",
            f"{prefix}_ALIASES": "alias-1='cmd1' alias-2='cmd2'",
            f"{prefix}_REMOVE_PATHS": "PATH1=/obsolete/path",
            })
        return sub_env
    venvmod_cmd(args=["venvmod-initialize", str(venv_path),
                      "--read-env", "--activate-log", "This is test modulefile."],
                xfail=False,
                env=create_subenv(venv_path.name.upper().replace("-", "_").replace(".", "_")))
    venvmod_cmd(args=["venvmod-initialize", str(venv_path)],
                xfail=True, err_msg="is already a venv-modulefile environment.")

    assert (venv_path / "etc" / "modulefiles").exists()
    assert (venv_path / "etc" / "modulefiles" / venv_path.name.lower().replace("_", "-")).exists()

    venvmod_cmd(args=["venvmod-cmd-setenv", str(venv_path), "TEST_VAR", "test_value"], xfail=False)

    all_venvmod_commands(venv_path, test_scripts)

    appli_name = "Ap-p_Li.1"

    # xfail before add-appli
    venvmod_cmd(args=["venvmod-cmd-setenv", str(venv_path),
                      "--appli", appli_name, "TEST_VAR", "test_value"],
                xfail=True, err_msg="You can\'t add command to non exsting modulefile")

    venvmod_cmd(args=["venvmod-add-appli", str(venv_path), appli_name, "--verbose"], xfail=False)
    venvmod_cmd(args=["venvmod-cmd-setenv", str(venv_path),
                      "--appli", appli_name, "TEST_VAR", "test_value"],
                xfail=False)

    all_venvmod_commands(venv_path, test_scripts, appli=appli_name)

    # Appli 2 : load from env var
    venvmod_cmd(args=["venvmod-add-appli", str(venv_path), "appli-2", "--verbose"], xfail=False)

    venvmod_cmd(args=["venvmod-cmd-read-env", venv_path, "--appli", "appli-2"],
                xfail=False, env=create_subenv("APPLI_2"))

    # Appli 3 : load from env var at creation
    venvmod_cmd(args=["venvmod-add-appli", str(venv_path), "appli-3",
                      "--read-env", "--verbose"], xfail=False, env=create_subenv("APPLI_3"))

    # Appli 4 : disconnected appli
    venvmod_cmd(args=["venvmod-add-appli", str(venv_path), "disconnected-appli",
                      "--disconnect", "--verbose"], xfail=False, env=create_subenv("APPLI_4"))

    # Appli 5 : toremove appli
    venvmod_cmd(args=["venvmod-add-appli", str(venv_path), "toremove-appli",
                      "--verbose"], xfail=False) # add 1
    venvmod_cmd(args=["venvmod-add-appli", str(venv_path), "toremove-appli1", "toremove-appli2",
                      "--verbose"], xfail=False) # add 2
    venvmod_cmd(args=["venvmod-add-appli", str(venv_path), "toremove-appli-d",
                      "--disconnect", "--verbose"], xfail=False) # add disconnected
    venvmod_cmd(args=["venvmod-rm-appli", str(venv_path), "toremove-appli", "toremove-appli-d",
                      "--verbose"], xfail=False) # remove independant
    venvmod_cmd(args=["venvmod-rm-appli", str(venv_path), "toremove-appli1",
                      "--verbose"], xfail=False) # remove 1
    venvmod_cmd(args=["venvmod-rm-appli", str(venv_path), "toremove-appli2",
                      "--verbose"], xfail=False) # remove 2

    result = subprocess.run(  # pylint: disable=subprocess-run-check
        args=[get_shell_command(), "-c", f". {(venv_path / 'bin' / 'activate')}"],
        stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    assert get_results(result=result)

    assert "This is test modulefile" in result.stderr.decode()

    venvmod_cmd(args=["venvmod-test-import", str(venv_path), "venvmod", "typing", "sys"],
                xfail=False)

    venvmod_cmd(args=["venvmod-test-import", str(venv_path), "not_a_module"],
                xfail=True)

    initial_path = os.environ['PATH']

    result = subprocess.run(  # pylint: disable=subprocess-run-check
        f'. {venv_path}/bin/activate && echo "PATH=$PATH" && deactivate && echo "PATH=$PATH"',
        shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE,
        executable=get_shell_command())

    assert result.returncode == 0, f"{result.stderr.decode().splitlines()}"

    path_lines: List[str] = []
    # print("result.stdout", result.stdout.decode())
    # print("result.stderr", result.stderr.decode())
    # print(Path(f"{venv_path}/bin/activate").read_text())
    for line in result.stdout.decode().splitlines():
        if line.startswith("PATH="):
            path_lines.append(line)

    # print(path_lines)
    assert len(path_lines) == 2, f"{path_lines}, {result.stdout.decode().splitlines()}"
    assert "value1:value2" in path_lines[0]
    assert path_lines[0] != path_lines[1]

    new_path = path_lines[1].replace("PATH=", "").replace(f"{venv_path}/opt/modulefiles/bin:", "")
    if "HOME" in os.environ:
        new_path.replace("~", os.environ["HOME"])
        initial_path.replace("~", os.environ["HOME"])
    assert new_path == initial_path

def test_subscript_module_version():
    """Tests if module version in sub script is correct."""

    venv_path = Path(os.environ["VIRTUAL_ENV"])

    result1 = subprocess.run(  # pylint: disable=subprocess-run-check
        f'. {venv_path}/bin/activate && echo "$(module --version)"',
        shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE,
        executable=get_shell_command())
    print(f"result1='''{result1.stderr}'''")

    result2 = subprocess.run(  # pylint: disable=subprocess-run-check
        f'. {venv_path}/bin/activate && echo "$({Path(__file__).resolve().parent / "test.sh"})"',
        shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE,
        executable=get_shell_command())
    print(f"result2='''{result2.stderr}'''")

    assert result2.stderr == result1.stderr

if __name__ == "__main__":
    test_venvmod_cmds()
