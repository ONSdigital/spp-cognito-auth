#!/bin/sh

set -eu

pip install poetry

cd spp-cognito-auth-git

poetry install

poetry run python -m pytest -p no:warnings
