# ICoCo API - Version 2 (02/2021)

- [ICoCo API - Version 2 (02/2021)](#icoco-api---version-2-022021)
  - [Documentation](#documentation)
  - [Developpement environment](#developpement-environment)
  - [Source code](#source-code)
  - [Code testing](#code-testing)
  - [Code documentation](#code-documentation)

This project implements ICoCo API in Python based on *medcoupling*.

## Documentation

See [the documentation of the package](https://icoco-python.readthedocs.io/en/latest/index.html)

See also [the ogirinal documentation](https://github.com/cea-trust-platform/icoco-coupling) for full reference.

## Developpement environment

First create the environment:

```bash
. ./create_environment.sh
```

It creates a *venv* virtual environment *environment-icoco* and adds extra paths to run medcoupling
in it.

It also adds the following aliases:

- **icoco-pytest**: to run use cases tests
- **icoco-use-cases**: to run use cases implemented in *test_* functions (using *pytest*)
- **icoco-pylint**: to run pylint for all python files of the project
- **icoco-sphinx**: to initialize sphinx doc
- **icoco-sphinx-build**: to rebuild sphinx doc from previous structure

**Note:** *deactivate* function of *venv* is not able to revert the modified **PYTHONPATH** and the
aliases defined.

## Source code

Source code shared between use cases is expected to be in **src** directory implemented as package(s).
See its [README](src/README.md) for more details.

## Code testing

Code testing is powered by **pytest**.
See its [README](tests/README.md) for more details.

## Code documentation

A basic sphinx documentation can be generated.
See its [README](docs/README.md) for more details.
