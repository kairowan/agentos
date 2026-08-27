#!/usr/bin/env bash
set -euo pipefail

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
manifest="${project_root}/local_manifests/agentos.xml"

grep -q 'name="agentos-platform"' "${manifest}"
grep -q 'path="vendor/agentos"' "${manifest}"
grep -q -- '-b android17-release' "${project_root}/scripts/bootstrap.sh"
grep -q -- '--fail-fast' "${project_root}/scripts/bootstrap.sh"
grep -q 'lunch agentos_cf_x86_64-aosp_current-userdebug' "${project_root}/scripts/build_evidence.py"
python3 -c 'import re,sys,xml.etree.ElementTree as E; p=E.parse(sys.argv[1]).find("project"); assert re.fullmatch("[0-9a-f]{40}", p.get("revision", ""))' "${manifest}"

bash -n "${project_root}/scripts/bootstrap.sh"
bash -n "${project_root}/scripts/build.sh"

AGENTOS_TOTAL_MEMORY_KIB=$((64 * 1024 * 1024)) \
AGENTOS_FREE_DISK_KIB=$((400 * 1024 * 1024)) \
  "${project_root}/scripts/build.sh" /tmp --check-only >/dev/null

python3 "${project_root}/scripts/check_build_evidence.py"

echo "AgentOS manifest checks passed"
