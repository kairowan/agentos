#!/usr/bin/env bash
set -euo pipefail

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
manifest="${project_root}/local_manifests/agentos.xml"

grep -q 'name="agentos-platform"' "${manifest}"
grep -q 'path="vendor/agentos"' "${manifest}"
grep -q -- '-b android17-release' "${project_root}/scripts/bootstrap.sh"

echo "AgentOS manifest checks passed"

