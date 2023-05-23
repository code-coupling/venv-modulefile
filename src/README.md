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
  - `venvmod-cmd-append-path` / `venvmod-cmd-prepend-path`: modifies an environment variable
  - `venvmod-cmd-module-load`: loads a modulefile
  - `venvmod-cmd-module-use`: adds a search path for modulefile
  - `venvmod-cmd-remove-path`: removes path from environment variable
  - `venvmod-cmd-setenv`: defines an environment variable
  - `venvmod-cmd-set-aliases`: defines an alias
  - `venvmod-cmd-source-sh`: sources a script

- `venvmod-cmd-read-env`: reads modifications to do from environment variable:
  - `[NAME]_LD_LIBRARY_PATH`, `[NAME]_PYTHONPATH`, `[NAME]_PATH`: ``prepend`` for each element separated by ':'
  - `[NAME]_MODULE_USE`: ``module use`` for each element 'module' separated by ' '
  - `[NAME]_MODULEFILES`: ``module load`` for each element '/path/' separated by ' '
  - `[NAME]_SOURCEFILES`: ``source-sh`` for each element 'shell script [args...]' separated by ';'
  - `[NAME]_EXPORTS`: ``setenv`` for each element 'var=value' separated by ' '
  - `[NAME]_ALIASES`: ``set-aliases`` for each element 'var="value"' separated by ' '
  - `[NAME]_REMOVE_PATHS`: ``remove-path`` for each element 'var=value' separated by ' '
  where `[NAME]` is the name of the environment module (case insensitive, "-" and "." are replaced by "_").

- `venvmod-add-appli` allows to create sub modulefile. `--appli` option of the above commands
  permit to modify these modulefiles.

- `venvmod-test-import`: tests the import of modules given as argument

See `--help` option for cli description of each command.

The sequence to modify the environment respects the sequence of call of the different functions.
