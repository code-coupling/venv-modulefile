# Introduction

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
