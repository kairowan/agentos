# First full AOSP 17 build: execution and evidence

**Status: not yet completed.** `v0.4.0` is an APK pre-release. This runbook and its
offline self-checks prepare the first real build; they do not prove the product,
system-only voice service, or SELinux policy compiles. No host has been provisioned.

## Before accepting donated build access

- Agree on a dedicated x86-64 Linux VM/workstation, 16–32 logical CPUs, 64–128 GiB
  RAM, and approximately 800 GiB SSD initially. This is a provisional allocation;
  the first run must measure whether it is sufficient. Cloud decimal GB differs
  from binary GiB. Do not silently convert the sponsor's capacity offer.
- Confirm KVM and the necessary host setup if the donation includes a Cuttlefish
  boot, not just compilation. KVM is not required to compile the image itself.
- Agree which disk persists, an access window, ownership of artifacts, and how
  to export results. CPU/RAM can be burst resources while source/cache disks persist.
- Install the [official AOSP prerequisites](https://source.android.com/docs/setup/start/requirements),
  Python 3, `repo`, and standard Linux utilities. Check network access to both
  `android.googlesource.com` and GitHub before starting a large sync.
- Keep the `agentos` entry repository outside the AOSP checkout. Evidence is saved
  beside the entry scripts, not inside the AOSP source tree, which can be mounted
  read-only by modern builds. Do not run two builds or a sync against the same tree
  concurrently. Do not use a shared/limited container for sponsor sizing: the
  current sampler measures whole-host memory and filesystems, not cgroup limits.

## 1. Check tooling and synchronize

From a checkout of the `agentos` entry repository:

```bash
./scripts/check.sh
AGENTOS_SYNC_JOBS=16 ./scripts/bootstrap.sh /srv/agentos-aosp
```

The first command is an **offline simulated self-check**, requiring no AOSP source
or Linux build host. The second downloads real source and must only run on a host
with agreed storage and network capacity. Each sync creates `evidence/sync-*/`
with `sync.log`, `sync.txt` (timestamps, elapsed seconds, exit code), and, if sync
completes, a commit-resolved `source-manifest.xml`. Failed syncs keep their logs.

The upstream selection is `android17-release`. The local AgentOS revision is
`37ae1804a9ff3914812deacc9f0728bd3bd787bb`; it is newer than the downloadable
`v0.4.0` tag. Uncommitted UI changes on a developer's computer are **not** part of
that pin. A later integration fix needs a committed, accessible revision and a
reviewed manifest update, not an invisible modification to the build host.

## 2. Preflight and build

Use the same explicit output directory for checks and the real build:

```bash
OUT_DIR=/srv/agentos-out ./scripts/build.sh /srv/agentos-aosp --check-only
OUT_DIR=/srv/agentos-out AGENTOS_BUILD_JOBS=16 ./scripts/build.sh /srv/agentos-aosp
```

Without arguments, the workspace defaults to `agentos/workspace` and output to
`workspace/out`. Relative `OUT_DIR` paths are resolved against the workspace.
`OUT_DIR_COMMON_BASE` is deliberately rejected to avoid measuring the wrong disk.
The gate requires a 64 GiB-class host (at least 60 GiB visible RAM to allow for
reserved memory) and **400 GiB free on the actual output filesystem after sync**.
That conservative build gate is not the total storage requirement and is not
claimed to be an experimentally established minimum.

For the first measurement use a new output directory. An existing directory is
allowed for incremental development but `output_preexisting=true` is recorded;
do not report that run as a clean build. No script deletes output or cache files.

The collector exports all source commits, rejects dirty tracked/untracked project
files, runs `source build/envsetup.sh`, selects
`agentos_cf_x86_64-aosp_current-userdebug`, and calls **`m -jN` without module-only
targets**. It then checks for source changes, Android version 17, a build
fingerprint, and nonempty `boot.img`, `super.img`, and `userdata.img` before hashing
all product `.img` files. It does not use `set -u` inside AOSP's environment script.

The terminal prints the unique evidence directory. Follow its `build.log` with
`tail -f` in another terminal if desired. Ctrl-C/SIGTERM during compilation stops
the build process group and retains partial evidence. A forced SIGKILL, host crash,
or full evidence disk may leave an `in_progress` record; this is not success.

Resource overrides `AGENTOS_TOTAL_MEMORY_KIB` and `AGENTOS_FREE_DISK_KIB` are only
accepted together with `--check-only`, explicitly labeled `SIMULATED`, and rejected
for an actual build. They cannot make a small machine eligible for an evidence run.

## 3. Understand the evidence bundle

| File | Meaning |
| --- | --- |
| `summary.json` | Stage/status, source IDs, output reuse, start/end times, build and total elapsed time, sampled peaks, directory sizes, errors |
| `machine.json` | CPU count, memory, OS/kernel, output-filesystem capacity, KVM accessibility |
| `build.log` | Source checks/tool information and complete envsetup/lunch/compiler output; retained on failure |
| `source-manifest.xml`, `source-manifest-after.xml` | Commit-resolved project composition, checked for changes during compilation |
| `commands.sh`, `build_evidence.py` | Exact command and collector used; driver hash and entry-repository dirty state are recorded |
| `resources.csv` | Samples before, during and after compilation, approximately every five seconds |
| `product-out.txt`, `host-out.txt` | Paths reported by this product configuration, not a hard-coded image directory |
| `images.sha256` | SHA-256 of product images, relative to `product-out.txt`; only complete after artifact validation |
| `build-fingerprint.txt`, `platform-version.txt` | Build identity for the later boot comparison |

Sampling reports **whole-host** RAM in use (`MemTotal - MemAvailable`), swap,
1-minute load, and source/output filesystem usage. It includes other processes,
caches, and unrelated disk contents; short spikes between samples can be missed.
It is not a per-process maximum or aggregate compiler RSS. A dedicated worker
makes this a useful first sizing estimate, not an exact future resource guarantee.

Before/after `du` measurements include the workspace, `.repo`, output, and an
explicit `CCACHE_DIR` if present. Nested values overlap: **do not sum them**.
Setting `CCACHE_DIR` alone does not enable compiler caching. Record whether the
build actually uses ccache or remote execution when publishing measurements.
`build_elapsed_seconds` includes environment setup and compilation; total elapsed
also includes snapshots, hashing and directory measurements. Sync time is separate.

Successful compilation is labeled `build_succeeded_boot_unverified`. Exit zero
does not mean the image boots, passes CTS/VTS, or works on physical hardware.
Failed attempts return nonzero and keep their logs. Nothing uploads automatically.

## 4. Boot and capture the matching image

Prepare host packages, KVM permissions and networking using the
[official Cuttlefish setup](https://source.android.com/docs/devices/cuttlefish/get-started).
Do not substitute a downloaded stock image or sideload APKs as system-build proof.
Use the host tools and images from the **same build**. In a fresh terminal:

```bash
cd /srv/agentos-aosp
export OUT_DIR=/srv/agentos-out
source build/envsetup.sh
lunch agentos_cf_x86_64-aosp_current-userdebug
"$(get_abs_build_var HOST_OUT)/bin/launch_cvd" --daemon
adb devices
```

Host setup, machine access and launching the VM are intentionally manual. Select
the Cuttlefish serial printed by `adb devices` (do not assume the example below
matches your instance). Back in the entry repository, substitute the exact build
directory printed by the collector:

```bash
./scripts/build.sh --capture-boot /path/to/agentos/evidence/build-RUN --serial localhost:6520
```

This read-only check requires `sys.boot_completed=1`, the AgentOS product name,
the recorded fingerprint and Android version, and Shell/Capability/Media/Voice
packages installed on system partitions rather than `/data`. It stores a new
`boot-*/summary.json`, PNG and logcat under that build's evidence directory.
It never selects HOME, installs APKs, enables permissions or changes accounts.

A `boot_smoke_passed` record is only an identity/boot/package smoke check. The build
summary remains immutable with `boot_verified=false`; use the separate boot record
for this later result. Record Shell interaction and test capability denials
separately. Checking `getenforce` is not a complete SELinux audit; Cuttlefish cannot
validate DSP wake-word accuracy, acoustic echo cancellation, or camera HAL quality.

## 5. Reproduce the pinned source

For a replay use a **fresh checkout**, not `bootstrap.sh` against an existing
validation tree (bootstrap selects the moving upstream branch again). First
initialize the same upstream manifest repository, then copy the exported complete
manifest into its manifest checkout and select it:

```bash
mkdir /srv/agentos-replay
cd /srv/agentos-replay
repo init -u https://android.googlesource.com/platform/manifest -b android17-release
cp /path/to/evidence/source-manifest.xml .repo/manifests/agentos-pinned.xml
repo init -m agentos-pinned.xml
repo sync -c --no-tags --fail-fast -j16
```

Do **not** add the original local manifest again: the export already includes
`vendor/agentos`. Preserve the entry-script revision/driver as well. The collector
will export a second manifest for comparison. Pinning source enables a repeatable
input set; bit-identical images are not promised without controlling timestamps,
build numbers, toolchain environment and signing inputs too.

## 6. Review and publish manually

- Review logs, paths, screenshots and manifests for secrets, account information,
  private notifications and internal URLs. Do not test publication with real accounts.
- Keep an unchanged private original. If publishing a redacted copy, label the
  redactions and do not claim its hash matches the original.
- Publish the build summary, source manifest, log, machine details, metrics, image
  checksums and separate boot result alongside the exact source revision. A failure
  report is useful but must not be labeled a completed build.
- Upload large images to agreed artifact storage, not Git source history. Decide
  retention with the sponsor; the proposed policy is in the
  [sponsorship brief](cloud-build-sponsorship.md). These scripts never upload or delete.
- Replace provisional disk/compute estimates with measured values plus headroom.
  Follow up on the existing hosting ticket once real build evidence, external
  participation and several months of maintenance are available.
