#!/bin/bash
# Copyright (C) 2025 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

# Make IWYU tools matching the LLVM version used by Bazel available in ~/.local/bin

set -e -o pipefail

# Change to the directory where this script resides, it makes many things easier
# and we can call this script from everywhere.
cd -- "${BASH_SOURCE%/*}"

failure() {
    test ${#@} -eq 0 || echo "$(basename "$0"):" "$@" >&2
    exit 1
}

# figure out Clang version to use ##############################################

if [[ $# -eq 0 ]]; then
    CLANG_VERSION=$(
        bazel mod graph --output=json |
            jq --raw-output '.dependencies | map(select(.name == "llvm_linux_x86_64") | .version) | first // "21" | split(".") | first'
    )
elif [[ $# -eq 1 ]]; then
    CLANG_VERSION=$1
else
    shift
    failure "superfluous arguments:" "$@"
fi

# The tag/version numbering scheme is a big mess...
case $CLANG_VERSION in
    7) TAG_NAME="7.0" LIB_VERSION="7" ;;
    8) TAG_NAME="8.0" LIB_VERSION="8" ;;
    9) TAG_NAME="9.0" LIB_VERSION="9" ;;
    *) TAG_NAME="${CLANG_VERSION}" LIB_VERSION="${CLANG_VERSION}" ;;
esac

CLANG_LIB_PATH=/usr/lib/llvm-${LIB_VERSION}
if [[ ! -d ${CLANG_LIB_PATH} ]]; then
    failure "Clang ${CLANG_VERSION} is not installed."
fi

# temporary directory handling #################################################

WORK_DIR=$(mktemp --directory)
if [[ -z ${WORK_DIR} || ! -d ${WORK_DIR} ]]; then
    failure "could not create temporary working directory"
fi

cleanup() {
    rm -rf "${WORK_DIR}"
    echo "deleted temporary working directory ${WORK_DIR}"
}
trap cleanup EXIT

# build/install ################################################################

cd "${WORK_DIR}"
git clone \
    --depth 1 \
    --branch "clang_${TAG_NAME}" \
    https://github.com/include-what-you-use/include-what-you-use

IWYU_VERSION=$(
    grep --word-regexp IWYU_VERSION_STRING include-what-you-use/iwyu_version.h |
        sed 's/^.*"\(.*\)"$/\1/'
)
HOME_LOCAL="${HOME}/.local"
RELATIVE_PREFIX="opt/iwyu-${IWYU_VERSION}"
INSTALL_PREFIX="${HOME_LOCAL}/${RELATIVE_PREFIX}"

mkdir -p include-what-you-use-build
cd include-what-you-use-build
cmake -Wno-dev \
    -G "Unix Makefiles" \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_PREFIX_PATH="${CLANG_LIB_PATH}" \
    -DCMAKE_INSTALL_PREFIX="${INSTALL_PREFIX}" \
    ../include-what-you-use
make -j8 install

# setup convenience symlinks ###################################################

cd "${INSTALL_PREFIX}/bin"
ln --symbolic --force include-what-you-use iwyu
ln --symbolic --force iwyu_tool.py iwyu_tool

mkdir -p "${HOME_LOCAL}/bin"
cd "${HOME_LOCAL}/bin"
ln --symbolic --force "../${RELATIVE_PREFIX}/bin/"* .
