

import os
from pathlib import Path
import shutil
import subprocess
from typing import Dict, List

import venvmod

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
    result = subprocess.run(args=args + ["--verbose"],
                 stderr=subprocess.PIPE, stdout=subprocess.PIPE, env=env)
    success = (result.returncode != 0) if xfail else (result.returncode == 0)
    if not success or True:
        print("stderr", result.stderr.decode())
        print("stdout", result.stdout.decode())

    if err_msg:
        assert err_msg in result.stderr.decode()

    assert success

def all_venvmod_commands(venv_path: Path, appli: str = None):
    """Tests all cli venvmod commands.

    Parameters
    ----------
    venv_path : Path
        venv directory
    appli : str, optional
        appli name if any, by default None
    """

    appli = ["--appli", appli] if appli else []

    venv_path = str(venv_path)

    venvmod_cmd(args=["venvmod-cmd-module-use", venv_path] + appli, xfail=True)
    venvmod_cmd(args=["venvmod-cmd-module-use", venv_path, "/path/to/toto"] + appli, xfail=False)
    venvmod_cmd(args=["venvmod-cmd-module-use", venv_path,
                      "/path/to/toto1", "/path/to/toto2"] + appli, xfail=False)

    venvmod_cmd(args=["venvmod-cmd-module-load", venv_path] + appli, xfail=True)
    venvmod_cmd(args=["venvmod-cmd-module-load", venv_path, "test_module"] + appli, xfail=False)
    venvmod_cmd(args=["venvmod-cmd-module-load", venv_path,
                      "test_module1", "test_module2"] + appli, xfail=False)

    venvmod_cmd(args=["venvmod-cmd-source-sh", venv_path] + appli, xfail=True)
    venvmod_cmd(args=["venvmod-cmd-source-sh", venv_path, "bash"] + appli, xfail=True)
    venvmod_cmd(args=["venvmod-cmd-source-sh", venv_path,
                      "bash", "test_script"] + appli, xfail=False)
    venvmod_cmd(args=["venvmod-cmd-source-sh", venv_path,
                      "bash", "test_script1", "arg"] + appli, xfail=False)
    venvmod_cmd(args=["venvmod-cmd-source-sh", venv_path,
                      "bash", "test_script2", "arg1", "arg2"] + appli, xfail=False)

    venvmod_cmd(args=["venvmod-cmd-prepend-path", venv_path] + appli, xfail=True)
    venvmod_cmd(args=["venvmod-cmd-prepend-path", venv_path, "PATH"] + appli, xfail=True)
    venvmod_cmd(args=["venvmod-cmd-prepend-path", venv_path, "PATH", "value"] + appli, xfail=False)
    venvmod_cmd(args=["venvmod-cmd-prepend-path", venv_path,
                      "PATH", "value1", "value2"] + appli, xfail=False)

    venvmod_cmd(args=["venvmod-cmd-append-path", venv_path] + appli, xfail=True)
    venvmod_cmd(args=["venvmod-cmd-append-path", venv_path, "PATH"] + appli, xfail=True)
    venvmod_cmd(args=["venvmod-cmd-append-path", venv_path, "PATH", "value"] + appli, xfail=False)
    venvmod_cmd(args=["venvmod-cmd-append-path", venv_path,
                      "PATH", "value1", "value2"] + appli, xfail=False)

    venvmod_cmd(args=["venvmod-cmd-setenv", venv_path] + appli, xfail=True)
    venvmod_cmd(args=["venvmod-cmd-setenv", venv_path, "TEST_VAR"] + appli, xfail=True)
    venvmod_cmd(args=["venvmod-cmd-setenv", venv_path,
                      "TEST_VAR", "test_value"] + appli, xfail=False)
    venvmod_cmd(args=["venvmod-cmd-setenv", venv_path,
                      "TEST_VAR2", "test_value1", "test_value2"] + appli, xfail=True)

    venvmod_cmd(args=["venvmod-cmd-remove-path", venv_path] + appli, xfail=True)
    venvmod_cmd(args=["venvmod-cmd-remove-path", venv_path, "TEST_PATH"] + appli, xfail=True)
    venvmod_cmd(args=["venvmod-cmd-remove-path", venv_path,
                      "TEST_PATH", "test_path"] + appli, xfail=False)
    venvmod_cmd(args=["venvmod-cmd-remove-path", venv_path,
                      "TEST_PATH2", "test_path1", "test_path2"] + appli, xfail=True)

    venvmod_cmd(args=["venvmod-cmd-set-aliases", venv_path] + appli, xfail=True)
    venvmod_cmd(args=["venvmod-cmd-set-aliases", venv_path, "test_cmd"] + appli, xfail=True)
    venvmod_cmd(args=["venvmod-cmd-set-aliases", venv_path,
                      "test_cmd", "'ls -altr'"] + appli, xfail=False)
    venvmod_cmd(args=["venvmod-cmd-set-aliases", venv_path,
                      "test_cmd", "'ls -altr'", "cmd2"] + appli, xfail=True)


def test_venvmod_cmds():
    """Tests all commands

    Raises
    ------
    EnvironmentError
        If not run in a virtual environment.
    """

    if "VIRTUAL_ENV" not in os.environ:
        raise EnvironmentError("Expected to be run a venv.")

    venv_path=Path(os.environ["VIRTUAL_ENV"])

    for subdir in ["etc", "opt"]:
        if (venv_path / subdir).exists():
            shutil.rmtree(venv_path / subdir)

    # xfail before initialize
    venvmod_cmd(args=["venvmod-cmd-setenv", str(venv_path), "VAR", "value"],
                xfail=True, err_msg="Can\'t add command to non exsting file")

    # Initialize
    sub_env = os.environ.copy()
    venv_var_name = venv_path.name.upper().replace("-","_").replace(".","_")
    sub_env[f"{venv_var_name}_LD_LIBRARY_PATH"] = "/path/to/lib1:/path/to/lib2"
    sub_env[f"{venv_var_name}_PYTHONPATH"] = "/path/to/packages1:/path/to/packages2"
    sub_env[f"{venv_var_name}_PATH"] = "/path/to/bin1:/path/to/bin2"
    sub_env[f"{venv_var_name}_MODULE_USE"] = "/path/to/modules1 /path/to/modules2"
    sub_env[f"{venv_var_name}_MODULEFILES"] = "module1 module2"
    sub_env[f"{venv_var_name}_SOURCEFILES"] = "bash script1 arg1 arg2; bash script2"
    sub_env[f"{venv_var_name}_EXPORTS"] = "VAR1=value1 VAR2=value2"
    sub_env[f"{venv_var_name}_ALIASES"] = "alias-1='cmd1' alias-2='cmd2'"
    sub_env[f"{venv_var_name}_REMOVE_PATHS"] = "PATH1=/obsolete/path"
    venvmod_cmd(args=["venvmod-initialize", str(venv_path),
                      "--read-env", "True",
                      "--activate-log", "This is test modulefile."], xfail=False)

    assert (venv_path / "etc" / "modulefiles").exists()
    assert (venv_path / "etc" / "modulefiles" / venv_path.name.lower().replace("_","-")).exists()

    venvmod_cmd(args=["venvmod-cmd-setenv", str(venv_path), "TEST_VAR", "test_value"], xfail=False)

    all_venvmod_commands(venv_path)

    appli_name = "Ap-p_Li.1"

    # xfail before add-appli
    venvmod_cmd(args=["venvmod-cmd-setenv", str(venv_path),
                      "--appli", appli_name, "TEST_VAR", "test_value"],
                xfail=True, err_msg="Can\'t add command to non exsting file")

    venvmod_cmd(args=["venvmod-add-appli", str(venv_path), appli_name, "--verbose"], xfail=False)
    venvmod_cmd(args=["venvmod-cmd-setenv", str(venv_path),
                      "--appli", appli_name, "TEST_VAR", "test_value"],
                xfail=False)

    all_venvmod_commands(venv_path, appli=appli_name)

    # Appli 2 : load from env var
    venvmod_cmd(args=["venvmod-add-appli", str(venv_path), "appli-2", "--verbose"], xfail=False)
    sub_env = os.environ.copy()
    sub_env["APPLI_2_LD_LIBRARY_PATH"] = "/path/to/lib1:/path/to/lib2"
    sub_env["APPLI_2_PYTHONPATH"] = "/path/to/packages1:/path/to/packages2"
    sub_env["APPLI_2_PATH"] = "/path/to/bin1:/path/to/bin2"
    sub_env["APPLI_2_MODULE_USE"] = "/path/to/modules1 /path/to/modules2"
    sub_env["APPLI_2_MODULEFILES"] = "module1 module2"
    sub_env["APPLI_2_SOURCEFILES"] = "bash script1 arg1 arg2; bash script2"
    sub_env["APPLI_2_EXPORTS"] = "VAR1=value1 VAR2=value2"
    sub_env["APPLI_2_ALIASES"] = "alias-1='cmd1' alias-2='cmd2'"
    sub_env["APPLI_2_REMOVE_PATHS"] = "PATH1=/obsolete/path"
    venvmod_cmd(args=["venvmod-cmd-read-env", venv_path, "--appli", "appli-2"],
                xfail=False, env=sub_env)

    # Appli 3 : load from env var at creation
    sub_env = os.environ.copy()
    sub_env["APPLI_3_LD_LIBRARY_PATH"] = "/path/to/lib1:/path/to/lib2"
    sub_env["APPLI_3_PYTHONPATH"] = "/path/to/packages1:/path/to/packages2"
    sub_env["APPLI_3_PATH"] = "/path/to/bin1:/path/to/bin2"
    sub_env["APPLI_3_MODULE_USE"] = "/path/to/modules1 /path/to/modules2"
    sub_env["APPLI_3_MODULEFILES"] = "module1 module2"
    sub_env["APPLI_3_SOURCEFILES"] = "bash script1 arg1 arg2; bash script2"
    sub_env["APPLI_3_EXPORTS"] = "VAR1=value1 VAR2=value2"
    sub_env["APPLI_3_ALIASES"] = "alias-1='cmd1' alias-2='cmd2'"
    sub_env["APPLI_3_REMOVE_PATHS"] = "PATH1=/obsolete/path"

    venvmod_cmd(args=["venvmod-add-appli", str(venv_path), "appli-3",
                      "--read-env", "True", "--verbose"], xfail=False)

    venvmod_cmd(args=["venvmod-test-import", str(venv_path), "venvmod", "typing", "sys"],
                xfail=False)
