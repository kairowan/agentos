#!/usr/bin/env bash
set -euo pipefail

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
workspace="${1:-${project_root}/workspace}"
sync_jobs="${AGENTOS_SYNC_JOBS:-$(getconf _NPROCESSORS_ONLN)}"

[[ $# -le 1 && "${sync_jobs}" =~ ^[1-9][0-9]{0,3}$ ]] || {
  echo "usage: bootstrap.sh [WORKSPACE]; AGENTOS_SYNC_JOBS must be a positive integer"
  exit 1
}

command -v repo >/dev/null || {
  echo "repo is required: https://source.android.com/docs/setup/download"
  exit 1
}

mkdir -p "${project_root}/evidence" "${workspace}/.repo/local_manifests"
evidence="$(mktemp -d "${project_root}/evidence/sync-$(date -u +%Y%m%dT%H%M%S)-XXXXXX")"
started="$(date +%s)"
finish() {
  result=$?
  {
    printf 'exit_code=%s\n' "${result}"
    printf 'finished_utc=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    printf 'elapsed_seconds=%s\n' "$(($(date +%s) - started))"
  } >>"${evidence}/sync.txt"
  printf 'Sync evidence: %s\n' "${evidence}"
}
trap finish EXIT
{
  printf 'started_utc=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  printf 'aosp_branch=android17-release\njobs=%s\n' "${sync_jobs}"
  printf 'entry_commit=%s\n' "$(git -C "${project_root}" rev-parse HEAD)"
} >"${evidence}/sync.txt"
cd "${workspace}"
{
  repo init -u https://android.googlesource.com/platform/manifest -b android17-release
  cp "${project_root}/local_manifests/agentos.xml" .repo/local_manifests/agentos.xml
  repo sync -c --no-tags --fail-fast -j"${sync_jobs}"
  repo manifest -r -o "${evidence}/source-manifest.xml"
} 2>&1 | tee "${evidence}/sync.log"

echo "Source tree ready at ${workspace}"
echo "AgentOS platform: ${workspace}/vendor/agentos"
echo "Next: ${project_root}/scripts/build.sh ${workspace}"
