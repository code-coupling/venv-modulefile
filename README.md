# venv-modulefile

[<img src="https://www.python.org/static/community_logos/python-logo-master-v3-TM.png" height="30"/>](Python)
[<img src="https://raw.githubusercontent.com/cea-hpc/modules/v5.2.0/doc/img/modules_red.svg" height="30" style="background-color: white"/>](Environment_Module)

- [venv-modulefile](#venv-modulefile)
  - [Description](#description)
  - [Quick start](#quick-start)

## Description

Tool to create Python complient environment from non-pythonic tools in a Python virtual
environment.

It is based on [Environment Module](https://modules.readthedocs.io/en/latest/) to
modify the virtual environment.

See [source documentation](src/README.md) for more details.

## Quick start

```bash

venvmod-initialize ${VIRTUAL_ENV}
venvmod-prepend-path ${VIRTUAL_ENV} LD_LIBRARY_PATH toto/tata/tutu

venvmod-add-appli ${VIRTUAL_ENV} APPLI_NAME --environ
venvmod-prepend-path ${VIRTUAL_ENV} --appli APPLI_NAME LD_LIBRARY_PATH toto/tata/tutu

```
