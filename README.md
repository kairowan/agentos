# AgentOS

AgentOS is an experimental agent-native operating system based on AOSP 17.
Users express goals instead of opening traditional applications; trusted system
services execute approved capabilities and render task-specific interfaces.

This repository is the project entry point. It pins the AOSP branch, documents
the architecture, and synchronizes the buildable platform code from
[`agentos-platform`](https://github.com/kairowan/agentos-platform).

## Requirements

- 64-bit Linux with KVM for Cuttlefish
- Git and Google's `repo` tool
- Approximately 400 GB free disk and 64 GB RAM for a full AOSP build

## Fetch the complete source tree

```bash
git clone https://github.com/kairowan/agentos.git
cd agentos
./scripts/bootstrap.sh
```

The script initializes `android17-release` in `workspace/` and checks out the
platform repository at `workspace/vendor/agentos`.

## Build

```bash
cd workspace
source build/envsetup.sh
lunch agentos_cf_x86_64-aosp_current-userdebug
m
```

Run `./scripts/check.sh` before syncing AOSP to validate the project linkage.

## Status

The repository currently contains the bootstrapping and architectural baseline.
The first buildable platform component is a minimal HOME activity that establishes
the product integration path; it is not yet the finished agent experience.

