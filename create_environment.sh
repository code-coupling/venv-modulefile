#!/usr/bin/env bash
# current file can't be sourced
if [[ "$0" != "${BASH_SOURCE[0]}" ]]; then
    echo "Error! You don't initialize the ICoCo environment with:"
    echo "source $0"
    echo "Or:"
    echo ". $0"
    echo
    echo "Please, run:"
    echo "$0"
    return
fi

if [[ -n "${VIRTUAL_ENV}" ]]; then
    echo "VIRTUAL_ENV is already defined: ${VIRTUAL_ENV}"
    echo "Deactivate the virtual environment before running this script."
fi

####################################################################################################
# Functions
####################################################################################################
function usage(){
    cat ${project_root_dir}/README.md
    echo "(content of ${project_root_dir}/README.md) "
}

function help_load(){
    echo "To load the environment, please, run:"
    echo ". ${venv_directory}/bin/activate"
}

function create_venv(){

    if [ -d "${venv_directory}" ]; then
        read -p "Environment already exists, replace it ? ([yes]/no) " answer
        if [[ -z "${answer}" ]]||[[ "${answer}" == "y"* ]]; then
            rm -rf ${venv_directory}
        else
            help_load
            exit 0
        fi
    fi

    python3 -m venv ${venv_directory}
    if [[ "$?" != "0" ]]||[ ! -f "${venv_directory}/bin/activate" ]; then
        echo "venv creation failed in: ${venv_directory}"
        exit 1
    fi
}

function append_env(){
    echo "$1"  >> ${venv_directory}/bin/activate
}

function load_env(){
    if [[ -z "${VIRTUAL_ENV}" ]]; then
        . ${venv_directory}/bin/activate # >> /dev/null 2>&1
    fi
    if [[ ! "$(which python)" == *"${venv_directory}/bin"* ]]; then
        echo "$(which python) does not contanins contains: ${venv_directory}/bin"
        exit 1
    fi
}

function install_prerequisities(){
    load_env
    local python_packages=( pip setuptools ${prerequisities_packages[@]} )
    for package in ${python_packages[@]}; do
        python -m pip install --upgrade --no-cache-dir ${package}
    done
}

function install_dev_package(){
    load_env
    python -m pip -q install --editable ${project_root_dir}
}

####################################################################################################
# Execution
####################################################################################################

# root directory
project_root_dir="$( cd "$( dirname "${0}" )" &> /dev/null && pwd )"
# current directory
current_dir="${PWD}"

#############################
# default variables
#############################
project_name="icoco"

# venv directory
venv_directory=${current_dir}/environment-${project_name}
# add here additional python prerequisities
prerequisities_packages=(
    pylint==2.13.9
    pytest==7.0.1
    pytest-cov==4.0.0
    pytest-html==3.2.0
    pytest-xdist==3.0.2
    psutil==5.9.4
    pytest-sugar==0.9.6
    sphinx-rtd-theme==1.1.1
    myst-parser==0.16.1
    numpydoc==1.1.0
    numpy==1.19.5
    mpi4py==3.1.4
)

#############################
# cli
#############################
if (( $# > 0 )); then
    if [[ "$1" == "-h" ]]||[[ "$1" == "--help" ]]; then
        usage
        exit 0
    fi
fi

#############################
# Execution
#############################
# creates the venv
create_venv

# extend venv
cea_install_prefix='/home/prerequis_codes-public/install/lin-x86-64-cen7/native'
append_env 'export PYTHONPATH="'${cea_install_prefix}'/SALOME-9.8.0/MEDCOUPLING/lib/python3.6/site-packages/:${PYTHONPATH}"'
append_env 'export LD_LIBRARY_PATH="'${cea_install_prefix}'/SALOME-9.8.0/med-4.1.1/lib/:${LD_LIBRARY_PATH}"'
append_env 'export LD_LIBRARY_PATH="'${cea_install_prefix}'/SALOME-9.8.0/MEDCOUPLING/lib/:${LD_LIBRARY_PATH}"'
append_env 'export LD_LIBRARY_PATH="'${cea_install_prefix}'/hdf5-1.10.3/lib/:${LD_LIBRARY_PATH}"'
append_env 'module load mpich/gcc_6.5.0/3.2.1'
append_env 'export PROJECT_NAME="'${project_name}'"'
append_env 'alias '${project_name}'-pytest="cd '${project_root_dir}' && pytest"'
append_env 'alias '${project_name}'-use-cases="cd '${project_root_dir}' && pytest -m use_case"'
append_env 'alias '${project_name}'-pylint="cd '${project_root_dir}' && pylint --rcfile='${project_root_dir}'/.pylintrc '${project_root_dir}'/src '${project_root_dir}'/use_cases '${project_root_dir}'/tests"'
append_env 'alias '${project_name}'-sphinx="'${project_root_dir}'/docs/generate_doc.sh"'
append_env 'alias '${project_name}'-sphinx-build="'${project_root_dir}'/docs/generate_doc.sh --build"'
append_env 'echo "MEDCoupling version is: $(python3 -c '"'import medcoupling; print(medcoupling.MEDCouplingVersionStr())'"')"'

# install prerequisities in venv
install_prerequisities

# install src package in dev mode
install_dev_package

# displays how to load it
help_load

exit 0
