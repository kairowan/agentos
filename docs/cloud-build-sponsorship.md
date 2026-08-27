# Open-source cloud build sponsorship brief

## Project

AgentOS is an Apache-2.0 experiment targeting AOSP 17 and agent-native computing. Users
express goals; an unprivileged planner proposes a typed operation; a trusted Broker
applies policy and confirmation; and a bounded runtime renders task-specific UI.

Public repositories:

- https://github.com/kairowan/agentos
- https://github.com/kairowan/agentos-platform

## Current status — 2026-08-27

The downloadable baseline is the
[v0.4.0 Android-component pre-release](https://github.com/kairowan/agentos-platform/releases/tag/v0.4.0).
It contains the Shell and Capability Service APKs, not an AOSP system image.
Current `main` also builds a Media Service APK. System-only voice and SELinux
integration still require a full AOSP build. There is one maintainer; independent
community use and several months of maintenance have not yet been demonstrated.

Hosting is not approved or guaranteed. The long-term objective remains donated
build infrastructure for at least 12 months; the immediate milestone is a single
reproducible validation build on donated or borrowed hardware. That one-time run
does not replace the need for a sustainable development environment.

## Existing component evidence

- Public Kotlin and Jetpack Compose implementation
- Typed AIDL boundary between separate Shell and Capability Service APKs
- Signature permission, Binder caller identity checks, and draft SELinux domains
- Repeatable Gradle unit tests and three-APK builds on current `main` in GitHub Actions
- Real-emulator Binder integration check and checksum-published pre-release APKs
- Commit-pinned AgentOS local manifest and an unvalidated Cuttlefish product definition
- Apache-2.0 license, security policy, contribution guide, roadmap, and public issues
- Fail-closed capability, endpoint, generated-UI, and offline-fallback tests

## Validation evidence still needed

| Evidence | Current state | Acceptance/public record |
| --- | --- | --- |
| Independent participation | Not yet demonstrated | Substantive merged external contributions **or** external user issues with follow-up; no star quota |
| Sustained maintenance | Project began in August 2026 | Several months of meaningful commits, issue handling, and milestone releases; not a burst of tags |
| Full AOSP 17 image | Not built/validated | Resolved source manifest, complete build log, machine specification, elapsed time, image checksums |
| Matching Cuttlefish boot | Not validated | Matching fingerprint, system-installed AgentOS packages, screenshot and boot logs; a supplement to build evidence |
| Measured resource model | Estimates only | Separate persistent storage, burst compute, cache/output footprint and retention, based on the first measured build |

The [build runbook](aosp-build.md) describes how to collect these records. A green
script self-check or stock Android emulator with installed APKs is not evidence
of a full AgentOS image. Do not mark a milestone complete without a public result.

## Requested infrastructure — provisional, subject to measurements

For an initial measured run and, if later approved, recurring integration builds:

- 16–32 x86-64 vCPUs and 64–128 GiB RAM while building
- Approximately 800 GiB SSD provisioned initially, including the OS and headroom;
  confirm capacity with the sponsor and adjust after measurement
- KVM support for Cuttlefish integration tests
- object storage for checksums, build logs, test reports, and release images

Initial target usage is up to four full builds per month plus incremental builds
while resolving integration failures. This is a burst compute workload, **not**
zero persistent storage. Required compute hours are unknown until the first build;
we are not requesting or promising 24/7 exclusive use of a machine.

| Resource | Between builds | Proposed retention |
| --- | --- | --- |
| Source checkout and `.repo` objects | Persistent | Keep one active pinned checkout during approved hosting |
| CPU/RAM worker allocation | Releasable | Release after build, verification, and evidence capture if the provider supports it |
| `out/` and optional ccache | Disposable but useful for incremental builds | Keep one active output tree/cache initially; measure before agreeing a size cap or eviction policy |
| Public images | Separate artifact storage; size not measured yet | Propose latest two successful milestone images, subject to sponsor capacity |
| Logs, manifests, checksums, summaries | Persist independently of worker | Propose retention throughout the sponsorship; review sensitive content before publication |

These are proposed policies, not implemented automatic deletions. Stopping a VM
does not release its disk allocation. Deleting a checkout saves storage but forces
a full resync and loses incremental-build savings. Do not promise both persistent
caches and zero idle storage. No resource is provisioned, billed, or removed by the
repository scripts.

## Public outcomes

The next component milestone is an independently installable preview, not more
concept modules: one versioned three-APK bundle, an actual offline
goal → deny/confirm → system action → persisted-history recording, and small
contribution tasks with runnable checks. The platform's
[preview runbook](https://github.com/kairowan/agentos-platform/blob/main/docs/developer-preview.md)
separates those checks from full-image, DSP and real-carrier evidence. Local
artifacts or unexecuted workflows must not be reported as published validation.

Prospective support can be earmarked for one measured full build, recurring build
allocation, artifact storage, or a dedicated test device. Report the resulting
logs, measurements and compatibility work against that contribution. The long-term
12-month infrastructure objective remains unchanged; no donation or hosting
approval is promised and no billing or donor account is configured by these scripts.

1. First reproducible `agentos_cf_x86_64` AOSP 17 image.
2. Published machine shape, elapsed time, commit IDs, logs, and artifact checksums.
3. Cuttlefish boot and interaction recording.
4. Capability Broker AIDL and SELinux isolation validation.
5. Monthly integration image and public compatibility results.

## Current blocker

The application and architecture layers build successfully on free CI. A complete
AOSP checkout and image build requires substantially more disk and memory than the
standard public runner provides. No complete AgentOS system image is claimed yet.

## Resource stewardship

Use a dedicated worker to make whole-host resource samples meaningful. Publish
sync time separately from build time, distinguish a fresh output tree from an
incremental run, and report source/output/cache sizes without double-counting nested
directories. Revise the request with observed peaks and headroom rather than
presenting 800 GiB as a verified sufficient capacity.

When genuine participation, maintenance history, and a full-build result exist,
follow up in the existing hosting ticket. Additional documentation or rapid tags
alone do not satisfy those criteria, and reconsideration does not guarantee approval.
