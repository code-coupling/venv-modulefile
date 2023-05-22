# venv-modulefile

[<img src="https://www.python.org/static/community_logos/python-logo-master-v3-TM.png" height="30"/>](Python)
[<img src="https://raw.githubusercontent.com/cea-hpc/modules/v5.2.0/doc/img/modules_red.svg" height="30" style="background-color: white"/>](Environment_Module)

- [venv-modulefile](#venv-modulefile)
  - [Description](#description)
  - [Quick start](#quick-start)
  - [Available commands](#available-commands)

## Description

Tool to create Python complient environment from non-pythonic tools in a Python virtual
environment.

It is based on [Environment Module](https://modules.readthedocs.io/en/latest/) to
modify the virtual environment.

The package offers several commands to build environment modules activated by the virtual
environnment

## Quick start

The following example adds `foo/bar/baz` to `LD_LIBRARY_PATH` when the environment is loaded

```bash

venvmod-initialize ${VIRTUAL_ENV}
venvmod-prepend-path ${VIRTUAL_ENV} LD_LIBRARY_PATH foo/bar/baz

```

## Available commands

The list of available commands is the following:

- `venvmod-initialize` is the first command to call. It is expected before everithing as it upgrades
  the virtual environment with modulefile.

- The following commands modify the modulefile of the virtual environment:
  - `venvmod-cmd-append-path` / `venvmod-cmd-prepend-path`
  - `venvmod-cmd-module-load`:
  - `venvmod-cmd-module-use`
  - `venvmod-cmd-read-env`
  - `venvmod-cmd-remove-path`
  - `venvmod-cmd-setenv`
  - `venvmod-cmd-set-aliases`
  - `venvmod-cmd-source-sh`

- `venvmod-add-appli` allows to create sub modulefile. `--appli` option of the above commands
  permit to modify these modulefiles.

- `venvmod-test-import`: tests the import of modules given as argument

See `--help` option for cli description.
