#!/bin/bash
set -e

echo "Running mypy..."
mypy

echo "Running bandit..."
bandit -c pyproject.toml -r pyrogram_async_redis_storage

echo "Running semgrep..."
semgrep scan --config auto --error
