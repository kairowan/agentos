#!/usr/bin/env bash
set -euo pipefail

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
manifest="${project_root}/local_manifests/agentos.xml"

grep -q 'name="agentos-platform"' "${manifest}"
grep -q 'path="vendor/agentos"' "${manifest}"
grep -q -- '-b android17-release' "${project_root}/scripts/bootstrap.sh"
grep -q -- '--fail-fast' "${project_root}/scripts/bootstrap.sh"
grep -q 'lunch agentos_cf_x86_64-aosp_current-userdebug' "${project_root}/scripts/build.sh"
grep -q 'repo manifest -r' "${project_root}/scripts/build.sh"

bash -n "${project_root}/scripts/bootstrap.sh"
bash -n "${project_root}/scripts/build.sh"

AGENTOS_TOTAL_MEMORY_KIB=$((64 * 1024 * 1024)) \
AGENTOS_FREE_DISK_KIB=$((400 * 1024 * 1024)) \
  "${project_root}/scripts/build.sh" /tmp --check-only >/dev/null

if AGENTOS_TOTAL_MEMORY_KIB=1024 AGENTOS_FREE_DISK_KIB=$((400 * 1024 * 1024)) \
  "${project_root}/scripts/build.sh" /tmp --check-only >/dev/null 2>&1; then
  echo "AgentOS build preflight accepted insufficient memory"
  exit 1
fi

echo "AgentOS manifest checks passed"
