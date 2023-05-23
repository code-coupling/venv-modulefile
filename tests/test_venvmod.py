

import os
from pathlib import Path
import shutil
import subprocess
from typing import List

import venvmod

def venvmod_cmd(args: List[str], xfail: bool, err_msg: str = None):
    """Execute command

    Parameters
    ----------
    args : List[str]
        Argument list
    xfail : bool
        Expeted to fail if True
    """
    result = subprocess.run(args=args + ["--verbose"],
                 stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    success = (result.returncode != 0) if xfail else (result.returncode == 0)
    if not success:
        print("stderr", result.stderr.decode())
        print("stdout", result.stdout.decode())

    if err_msg:
        assert err_msg in result.stderr.decode()

    assert success


def test_venvmod_cmds():

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
    venvmod_cmd(args=["venvmod-initialize", str(venv_path)], xfail=False)

    assert (venv_path / "etc" / "modulefiles").exists()
    assert (venv_path / "etc" / "modulefiles" / venv_path.name.lower().replace("_","-")).exists()

    venvmod_cmd(args=["venvmod-cmd-setenv", str(venv_path), "TEST_VAR", "test_value"], xfail=False)

    appli_name = "Ap-p_Li.1"

    # xfail before add-appli
    venvmod_cmd(args=["venvmod-cmd-setenv", str(venv_path),
                      "--appli", appli_name, "TEST_VAR", "test_value"],
                xfail=True, err_msg="Can\'t add command to non exsting file")

    venvmod_cmd(args=["venvmod-add-appli", str(venv_path), appli_name, "--verbose"], xfail=False)
    venvmod_cmd(args=["venvmod-cmd-setenv", str(venv_path),
                      "--appli", appli_name, "TEST_VAR", "test_value"],
                xfail=False)
