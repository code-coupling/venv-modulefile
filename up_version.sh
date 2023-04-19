#!/usr/bin/env bash

project_root_dir="$( cd "$( dirname "${0}" )" &> /dev/null && pwd )"
version_file=${project_root_dir}/src/venvmod/VERSION

########################
# Cli
########################
if (( $# != 1 )); then
    echo "ERROR: You must provide exactly 1 argument: version number as x.y.z"
    exit 1
fi
version_name=$1

########################
# Main
########################

if ! (python3 -c "if not len('${version_name}'.split('.')) == 3: exit(1)"); then
    echo "ERROR: version format is not correct: '${version_name}', expected 'x.y.z'."
    exit 1
fi

versions_tagged=( $(git tag | grep -e '.') )
for version_tagged in ${versions_tagged[@]}; do
    if ! (python3 -c "from packaging import version; exit( 1 if version.parse('${version_name}') <= version.parse('${version_tagged}') else 0)"); then
        echo "ERROR: version is lower or equal to existing one: '${version_name}' <= ${version_tagged}."
        exit 1
    fi
done

git_status="$(git status --porcelain)"
if [[ -n "${git_status}" ]]; then
    read -p "Current repository is not clean: '${git_status}'. Do you want to continue ? (yes/[no]) " answer
    if [[ -z "${answer}" ]]||[[ "${answer}" == "n"* ]]; then
        exit 0
    fi
fi

echo ${version_name} > ${version_file}
git add ${version_file}
git commit -m "Version ${version_name}"
git tag ${version_name}

read -p "Do you want to push version '${version_name}' ? (yes/[no]) " answer
if [[ "${answer}" == "y"* ]]; then
    git push origin
    git push origin ${version_name}
fi
