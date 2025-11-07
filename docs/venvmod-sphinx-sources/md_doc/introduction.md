# Introduction

```{image} https://www.python.org/static/community_logos/python-logo-master-v3-TM.png
:alt: Python
:width: 200px
```

```{image} https://raw.githubusercontent.com/cea-hpc/modules/v5.2.0/doc/img/modules_red.svg
:alt: Environment_Module
:width: 200px
```

## Installation

```sh
python3 -m pip install venv-modulefile
```

## Quick start

```bash

venvmod-initialize ${VIRTUAL_ENV}
venvmod-prepend-path ${VIRTUAL_ENV} LD_LIBRARY_PATH toto/tata/tutu

venvmod-add-appli ${VIRTUAL_ENV} APPLI_NAME --environ
venvmod-prepend-path ${VIRTUAL_ENV} --appli APPLI_NAME LD_LIBRARY_PATH toto/tata/tutu

```

See [the cli](#command-line-interface) for more details.

## Description

This package contains tools to create Python complient environment from non-pythonic tools in a
Python virtual environment.

It is based on [Environment Module](https://modules.readthedocs.io/en/latest/) to
modify the virtual environment.

The principle is to insert `module load`/`module unload` commands in the `activate` script of a
virtual env. The `activate` script is also modified such that the last returned code is the one
provided by the `module load` command.

Two levels of modules can be defined:

- 1 global module: this module is directly activated/deactivated by the `activate` script.
- several applicaltion modules: sub modules (loaded by the global module) can be created separately.

During the whole loading process, the module commands will be applied by order of creation: the
global module loads application modules by creation order.

Commands can be added either to global module or application modules.

Three APIs are available.

## Command Line Interface

The cli is composed of commands starting by `venvmod-` prefix:

- `venvmod-initialize <venv_name>` is used to initialize the virtual environment with modulefile.
- `venvmod-add-appli <appli_name>` is used to add an appli (sub module) to the virtual env
(which can be removed with `venvmod-rm-appli`).
- `venvmod-cmd-<name> [--appli appli_name] <venv_name> <args>` is used to add a command to the
  global module or an appli if `--appli` argument is provided.

The following shows the full command help:

- First initialize the environment
```{program-output} venvmod-initialize --help
```

- Eventually add sub modules
```{program-output} venvmod-add-appli --help
```

- It is possible to remove them after
```{program-output} venvmod-rm-appli --help
```

- Modify the modules
```{program-output} venvmod-cmd-append-path --help
```

```{program-output} venvmod-cmd-module-load --help
```

```{program-output} venvmod-cmd-module-use --help
```

```{program-output} venvmod-cmd-prepend-path --help
```

```{program-output} venvmod-cmd-read-env --help
```

```{program-output} venvmod-cmd-remove-path --help
```

```{program-output} venvmod-cmd-setenv --help
```

```{program-output} venvmod-cmd-set-alias --help
```

```{program-output} venvmod-cmd-source-sh --help
```

```{program-output} venvmod-test-import --help
```

## Environment Variable Interface

This interface is called durung the `venvmod-add-appli` command.

```{eval-rst}
See :func:`venvmod.commands.append_module.read_env` function.
```

## The Python API

You can also use directly the Python API of the package.
