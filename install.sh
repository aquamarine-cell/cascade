#!/usr/bin/env bash
set -euo pipefail

REPO_URL="${CASCADE_REPO_URL:-https://github.com/Evangeline-Development-Company/cascade.git}"
REF="${CASCADE_REF:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

if ! command -v "${PYTHON_BIN}" >/dev/null 2>&1; then
  echo "Error: ${PYTHON_BIN} is required but was not found." >&2
  exit 1
fi

PACKAGE_SPEC="git+${REPO_URL}"
if [[ -n "${REF}" ]]; then
  PACKAGE_SPEC="${PACKAGE_SPEC}@${REF}"
fi

echo "Installing Cascade from ${PACKAGE_SPEC}"

install_with_pipx() {
  pipx install --force "${PACKAGE_SPEC}"
}

install_with_pip_user() {
  "${PYTHON_BIN}" -m pip install --user --upgrade "${PACKAGE_SPEC}"
}

if command -v pipx >/dev/null 2>&1; then
  echo "Using pipx (recommended)..."
  install_with_pipx
else
  echo "pipx not found; falling back to pip --user."
  install_with_pip_user
fi

USER_BIN="$("${PYTHON_BIN}" -m site --user-base)/bin"
if [[ ":${PATH}:" != *":${USER_BIN}:"* ]]; then
  cat <<EOF
Install complete, but ${USER_BIN} is not on your PATH.
Add this line to your shell profile:
  export PATH="${USER_BIN}:\$PATH"
EOF
fi

echo "Done. Run: cascade --help"
