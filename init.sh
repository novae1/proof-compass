#!/bin/bash

# Print each command before executing it
set -x

# Exit on any error
set -e

# Configure git
git config --global user.name "novae1"
git config --global user.email "ndasilva@protonmail.com"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="${SCRIPT_DIR}"

PYTHON_BIN="python3.12"
VENV_PATH="${REPO_ROOT}/.venv"
REQUIREMENTS_FILE="${REPO_ROOT}/requirements.txt"

if ! command -v "${PYTHON_BIN}" >/dev/null 2>&1; then
    echo "Error: ${PYTHON_BIN} not found. Please install Python 3.12 before running this script." >&2
    exit 1
fi

if [ ! -d "${VENV_PATH}" ]; then
    "${PYTHON_BIN}" -m venv "${VENV_PATH}"
else
    echo "Virtual environment already exists at ${VENV_PATH}; skipping creation."
fi

# shellcheck disable=SC1090
source "${VENV_PATH}/bin/activate"

python -m pip install --upgrade pip
python -m pip install -r "${REQUIREMENTS_FILE}"
