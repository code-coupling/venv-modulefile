"""Please comment the content of the file here."""
# Test files are expected to start with 'test_' prefix

# You can import pytest and use its features.
# import pytest


import icoco as appli

# Test functions are expected to start with 'test_' prefix
def test_version():
    # Test description:
    """Tests version of ICoCo from the module."""

    # Assert to check if test is ok
    assert appli.ICOCO_VERSION == '2.0'
