"""Run linters"""

import os
import pathlib

import pytest

@pytest.mark.linter
def test_pylint():
    """Function to run the use case with pytest"""

    root_directory = os.path.realpath(os.path.dirname(os.path.dirname(__file__)))
    src_directory = os.path.join(root_directory, "src")
    use_cases_directory = os.path.join(root_directory, "use_cases")
    tests_directory = os.path.join(root_directory, "tests")

    files_to_test = [
        str(f) for f in pathlib.Path(src_directory).glob("**/*.py") if f.is_file()] + [
        str(f) for f in pathlib.Path(use_cases_directory).glob("**/*.py") if f.is_file()] + [
        str(f) for f in pathlib.Path(tests_directory).glob("**/*.py") if f.is_file()]

    print("Files to check:\n    {}".format(
        "\n    ".join([path.replace(root_directory + "/", "") for path in files_to_test])))

    try:
        from pylint.lint import Run as PylintRunner # pylint: disable=import-outside-toplevel
    except ModuleNotFoundError as error:
        raise error

    args = files_to_test + [
            "--reports", "y",
            "--rcfile", f"{root_directory}/.pylintrc",
            "--output-format", "text"]

    pylint_result = PylintRunner(args, exit=False)

    pylint_stats = pylint_result.linter.stats
    global_note = "global_note"
    if hasattr(pylint_stats, global_note):
        global_note = getattr(pylint_stats, global_note)
    elif isinstance(pylint_stats, dict) and global_note in pylint_stats: # pylint: disable=unsupported-membership-test
        global_note = pylint_stats[global_note] # pylint: disable=unsubscriptable-object
    else:
        from pylint import version # pylint: disable=import-outside-toplevel
        raise AssertionError(
            f"Ne sait pas retrouver la note globale avec la version pylint {version}")

    minimal_note = 10.0
    success = global_note >= minimal_note
    print(f"Succes: {success} ({global_note} / {minimal_note})")
    assert success
