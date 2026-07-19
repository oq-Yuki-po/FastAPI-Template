#!/usr/bin/env bash
set -euo pipefail

uv sync --locked
uv run pre-commit install
