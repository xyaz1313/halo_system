#!/usr/bin/env bash
# One-command Docker dev launcher. Equivalent to running
# `docker compose up --build` from the repo root, but locked to the
# repo root so it works from any cwd.
#
# `--build` is deliberate: it's cheap when the Dockerfile layers are
# cached and it avoids the classic "I edited pyproject.toml but the
# image still has the old deps" footgun.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

exec docker compose up --build
