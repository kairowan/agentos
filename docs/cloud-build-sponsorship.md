# Open-source cloud build sponsorship brief

## Project

AgentOS is an Apache-2.0, AOSP 17 based experiment in agent-native computing. Users
express goals; an unprivileged planner proposes a typed operation; a trusted Broker
applies policy and confirmation; and a bounded runtime renders task-specific UI.

Public repositories:

- https://github.com/kairowan/agentos
- https://github.com/kairowan/agentos-platform

## Existing evidence

- Public Kotlin and Jetpack Compose implementation
- Repeatable Gradle unit tests and APK builds on GitHub Actions
- Downloadable, checksum-published pre-release APKs
- AOSP `repo` manifest and Cuttlefish product definition
- Apache-2.0 license, security policy, contribution guide, roadmap, and public issues
- Fail-closed capability, endpoint, generated-UI, and offline-fallback tests

## Requested infrastructure

Credits for an ephemeral Linux AOSP build worker for 12 months:

- 16–32 x86-64 vCPUs
- 64–128 GB RAM
- 600–800 GB SSD while a worker is active
- KVM support for Cuttlefish integration tests
- object storage for checksums, build logs, test reports, and release images

The worker will not run continuously. It will start for scheduled integration builds
and releases, publish public results, then stop. Initial target usage is up to four
full builds per month plus incremental builds while resolving integration failures.

## Public outcomes

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

Build workers are disposable and stopped when idle. The project will use incremental
compilation and caches only when their storage cost is lower than re-synchronization,
publish usage against milestones, and remove resources when credits expire.
