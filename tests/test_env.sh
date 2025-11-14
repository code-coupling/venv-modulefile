set -euo pipefail
unalias -a
readonly current_script_directory="$( cd "$( dirname "${0}" )" &> /dev/null && pwd )"
readonly root_dir="$(dirname ${current_script_directory})"
readonly shell_name=$(/usr/bin/basename "$(/usr/bin/ps -p $$ -ocomm=)")

readonly venv_test_dir=${current_script_directory}/.venv-test-${shell_name}
python3 -m venv ${venv_test_dir}
. ${venv_test_dir}/bin/activate

echo ${VIRTUAL_ENV}

pip install -e ${root_dir}

readonly venv_mod_dir=${current_script_directory}/.venv-mod-${shell_name}
if [ -d "${venv_mod_dir}" ]; then
    rm -rf ${venv_mod_dir}
fi
python3 -m venv ${venv_mod_dir}

venvmod-initialize ${venv_mod_dir}

. ${venv_mod_dir}/bin/activate

version_cur=$(module --version)
version_sub=$(${root_dir}/tests/test.sh)

echo "'${version_cur}' '${version_sub}'"

if [[ "${version_cur}" != "${version_sub}" ]]; then
    exit 1
fi
