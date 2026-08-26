# AgentOS

[![Manifest](https://github.com/kairowan/agentos/actions/workflows/manifest.yml/badge.svg)](https://github.com/kairowan/agentos/actions/workflows/manifest.yml)
[![Platform CI](https://github.com/kairowan/agentos-platform/actions/workflows/ci.yml/badge.svg)](https://github.com/kairowan/agentos-platform/actions/workflows/ci.yml)

AgentOS is an experimental agent-native operating system based on AOSP 17.
Users express goals instead of opening traditional applications; trusted system
services execute approved capabilities and render task-specific interfaces.

AgentOS 是一个基于 AOSP 17 的智能体原生操作系统实验项目。用户表达目标，
系统通过受控能力执行任务，并为当前任务即时生成交互界面，而不是要求用户
在一组传统应用之间切换。

![AgentOS v0.4.0 using voice-first UI and the separate capability service](https://github.com/kairowan/agentos-platform/releases/download/v0.4.0/AgentShell-home.png)

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
./scripts/build.sh
```

The build script rejects hosts below the documented 64 GiB RAM and 400 GiB free
disk minimum, records a pinned source manifest and build metadata, and publishes
SHA-256 checksums for generated images. Run `./scripts/check.sh` before syncing AOSP
to validate linkage and the preflight behavior.

## Status

The v0.4 release remains the downloadable baseline. Current platform development
moves microphone access from the HOME app into an AOSP `VoiceInteractionService`,
with DSP hotword detection, an isolated detection service, silence-ended command
capture, hotword interruption, and signature-protected delivery. A bounded local
SQLite history view shows every completed goal and an automatically extracted
semantic graph. Relations preserve evidence, confidence, and candidate status so
model inference cannot become capability authority. Locally filtered social-message events
continue through the dedicated capability service over one-way AIDL. It remains an
architecture validation project, not a daily-driver operating system; real hotword
wake-up still needs target-device SoundTrigger hardware and model enrollment.

See the [platform repository](https://github.com/kairowan/agentos-platform) for
source, CI artifacts, and implementation issues.
Download the current runnable APK from the
[`v0.4.0` pre-release](https://github.com/kairowan/agentos-platform/releases/tag/v0.4.0).

## Development without a full AOSP workstation

Daily Android work is built independently in `agentos-platform` with Gradle and
GitHub Actions. The complete AOSP checkout is only required for product images,
SELinux, privileged-service integration, Cuttlefish, CTS, and VTS.

## Project documents

- [Architecture](docs/architecture.md)
- [Security model](docs/security-model.md)
- [Roadmap](docs/roadmap.md)
- [Cloud build sponsorship brief](docs/cloud-build-sponsorship.md)
- [Contributing](CONTRIBUTING.md)

## License

Apache License 2.0.
