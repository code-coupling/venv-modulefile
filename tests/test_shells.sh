#!/usr/bin/env bash
set -euo pipefail
unalias -a
readonly current_script_directory="$( cd "$( dirname "${0}" )" &> /dev/null && pwd )"

script_to_run=$1
shift
shell_names=($@)

for shell in "${shell_names[@]}"; do
    if [ "$(command -v ${shell})" ]; then
        echo "testing '${shell} ${script_to_run}'"
        ${shell} ${script_to_run}
    else
        echo "${shell} not found to test ${script_to_run}"
    fi
done

for item in "${myArray[@]}"; do
    echo "${item}"
done
