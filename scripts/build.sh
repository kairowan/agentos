#!/usr/bin/env bash
set -euo pipefail

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
workspace="${1:-${project_root}/workspace}"
mode="${2:-build}"

minimum_memory_kib=$((64 * 1024 * 1024))
minimum_disk_kib=$((400 * 1024 * 1024))
memory_kib="${AGENTOS_TOTAL_MEMORY_KIB:-$(awk '/MemTotal/ { print $2 }' /proc/meminfo)}"
disk_kib="${AGENTOS_FREE_DISK_KIB:-$(df -Pk "$(dirname "${workspace}")" | awk 'NR == 2 { print $4 }')}"

if (( memory_kib < minimum_memory_kib )); then
  echo "AgentOS requires at least 64 GiB RAM; detected $((memory_kib / 1024 / 1024)) GiB"
  exit 1
fi
if (( disk_kib < minimum_disk_kib )); then
  echo "AgentOS requires at least 400 GiB free disk; detected $((disk_kib / 1024 / 1024)) GiB"
  exit 1
fi
if [[ "${mode}" == "--check-only" ]]; then
  echo "AgentOS AOSP resource checks passed"
  exit 0
fi

[[ -f "${workspace}/build/envsetup.sh" ]] || {
  echo "AOSP source tree not found at ${workspace}; run scripts/bootstrap.sh first"
  exit 1
}

build_jobs="${AGENTOS_BUILD_JOBS:-$(getconf _NPROCESSORS_ONLN)}"
cd "${workspace}"
source build/envsetup.sh
lunch agentos_cf_x86_64-aosp_current-userdebug

mkdir -p out/agentos-metadata
repo manifest -r -o out/agentos-metadata/source-manifest.xml
{
  echo "built_at_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "target=agentos_cf_x86_64-aosp_current-userdebug"
  echo "jobs=${build_jobs}"
  echo "agentos_platform_commit=$(git -C vendor/agentos rev-parse HEAD)"
} >out/agentos-metadata/build.txt

m -j"${build_jobs}" 2>&1 | tee out/agentos-metadata/build.log
find out/target/product/vsoc_x86_64 -maxdepth 1 -type f -name '*.img' -print0 \
  | sort -z \
  | xargs -0 sha256sum >out/agentos-metadata/images.sha256

echo "AgentOS image build completed"
echo "Metadata: ${workspace}/out/agentos-metadata"
