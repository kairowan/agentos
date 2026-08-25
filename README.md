# AgentOS

AgentOS is an experimental agent-native operating system based on AOSP 17.
Users express goals instead of opening traditional applications; trusted system
services execute approved capabilities and render task-specific interfaces.

AgentOS 是一个基于 AOSP 17 的智能体原生操作系统实验项目。用户表达目标，
系统通过受控能力执行任务，并为当前任务即时生成交互界面，而不是要求用户
在一组传统应用之间切换。

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

The v0.1 platform baseline now includes a Kotlin/Jetpack Compose HOME shell,
declarative generated-interface model, three read-only capabilities, deterministic
local agent routing, JVM tests, and automatic APK builds. It is an architecture
validation release, not a daily-driver operating system.

See the [platform repository](https://github.com/kairowan/agentos-platform) for
source, CI artifacts, and implementation issues.

## Development without a full AOSP workstation

Daily Android work is built independently in `agentos-platform` with Gradle and
GitHub Actions. The complete AOSP checkout is only required for product images,
SELinux, privileged-service integration, Cuttlefish, CTS, and VTS.

## Project documents

- [Architecture](docs/architecture.md)
- [Security model](docs/security-model.md)
- [Roadmap](docs/roadmap.md)
- [Contributing](CONTRIBUTING.md)

## License

Apache License 2.0.

