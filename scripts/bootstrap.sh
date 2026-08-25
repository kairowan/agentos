#!/usr/bin/env bash
set -euo pipefail

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
workspace="${1:-${project_root}/workspace}"
sync_jobs="${AGENTOS_SYNC_JOBS:-$(getconf _NPROCESSORS_ONLN)}"

command -v repo >/dev/null || {
  echo "repo is required: https://source.android.com/docs/setup/download"
  exit 1
}

mkdir -p "${workspace}/.repo/local_manifests"
cd "${workspace}"
repo init -u https://android.googlesource.com/platform/manifest -b android17-release
cp "${project_root}/local_manifests/agentos.xml" .repo/local_manifests/agentos.xml
repo sync -c --no-tags --fail-fast -j"${sync_jobs}"

echo "Source tree ready at ${workspace}"
echo "AgentOS platform: ${workspace}/vendor/agentos"
echo "Next: ${project_root}/scripts/build.sh ${workspace}"
