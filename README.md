# AgentOS

[![Manifest](https://github.com/kairowan/agentos/actions/workflows/manifest.yml/badge.svg)](https://github.com/kairowan/agentos/actions/workflows/manifest.yml)
[![Platform CI](https://github.com/kairowan/agentos-platform/actions/workflows/ci.yml/badge.svg)](https://github.com/kairowan/agentos-platform/actions/workflows/ci.yml)

AgentOS is an experimental agent-native operating system targeting AOSP 17.
Users express goals instead of opening traditional applications; trusted system
services execute approved capabilities and render task-specific interfaces.

AgentOS 是一个基于 AOSP 17 的智能体原生操作系统实验项目。用户表达目标，
系统通过受控能力执行任务，并为当前任务即时生成交互界面，而不是要求用户
在一组传统应用之间切换。

![AgentOS v0.4.0 using voice-first UI and the separate capability service](https://github.com/kairowan/agentos-platform/releases/download/v0.4.0/AgentShell-home.png)

**Build status:** `v0.4.0` is an Android-component APK pre-release, not a complete
AgentOS system image. No full AOSP 17 image or Cuttlefish boot has been validated
yet. Green component CI and Android 35 emulator screenshots do not establish that.

This repository is the project entry point. It selects the AOSP branch, documents
the architecture, and synchronizes the buildable platform code from
[`agentos-platform`](https://github.com/kairowan/agentos-platform).

## Requirements

- x86-64 Linux; working KVM is additionally required to boot Cuttlefish
- Git, Python 3, Google's `repo` tool, and standard Linux utilities (`du`, `lscpu`)
- A 64 GiB-class or larger machine; preflight allows 60 GiB visible RAM for hardware reservations
- Provision approximately **800 GiB SSD initially**, including OS, source, output,
  caches, and headroom. This is a planning estimate, not measured AgentOS usage.
  The build gate conservatively requires **400 GiB still free on the output
  filesystem after source synchronization**, not a 400 GiB total volume.

Install the [upstream AOSP build prerequisites](https://source.android.com/docs/setup/start/requirements)
before synchronizing. Use a dedicated VM/workstation for meaningful measurements;
the collector samples whole-host resources, not container or per-job resource limits.

## Fetch the complete source tree

```bash
git clone https://github.com/kairowan/agentos.git
cd agentos
./scripts/bootstrap.sh
```

The script initializes `android17-release` in `workspace/` and checks out the
platform repository at `workspace/vendor/agentos`. The local manifest pins platform
commit `37ae1804a9ff3914812deacc9f0728bd3bd787bb`, not the moving `main` branch or
uncommitted local edits. That source snapshot is newer than the `v0.4.0` APK tag.
Each sync records its log, exit status, duration, and resolved manifest under
`evidence/sync-*/`. AOSP project revisions are frozen in the exported manifest;
the initial upstream branch selection is not itself an immutable lockfile.

## Build

```bash
./scripts/check.sh
./scripts/build.sh --check-only
./scripts/build.sh
```

Each attempt writes a new local `evidence/build-*/` directory with a pinned source
manifest, machine details, full log, timestamps, resource samples, output-directory
sizes, and (on success) image checksums. Failures retain their logs and return a
nonzero exit code. Nothing is uploaded automatically. `scripts/check.sh` uses fake
AOSP commands to exercise the collector; it does **not** build or boot Android.

See the [first full-build runbook](docs/aosp-build.md) for external output disks,
replaying a source snapshot, Cuttlefish boot verification, and publication checks.

## Status

The `v0.4.0` APK pre-release remains the downloadable baseline. Current platform development
moves microphone access from the HOME app into an AOSP `VoiceInteractionService`,
with DSP hotword detection, an isolated detection service, silence-ended command
capture, hotword interruption, and signature-protected delivery. A bounded local
Room-backed SQLite history shows every completed goal and an automatically extracted,
searchable, zoomable and editable semantic graph with persistent custom node positions.
Relations preserve evidence, confidence, and candidate status so
model inference cannot become capability authority. Locally filtered social-message events
continue through the dedicated capability service over one-way AIDL. It remains an
architecture validation project, not a daily-driver operating system; real hotword
wake-up still needs target-device SoundTrigger hardware and model enrollment.

The platform also contains a native media vertical slice: a separately sandboxed,
signature-protected service owns Camera2 preview, JPEG capture, H.264/AAC video,
pauseable M4A recording, and unified MediaStore queries. AgentShell renders the
camera, gallery, and recorder as Kotlin Compose workspaces around a native Surface;
target-device HAL and vendor-extension calibration remains required for OEM-grade image quality.

An installed-app capability bridge also keeps conventional Android apps available
as compatibility providers behind the Agent interface. It discovers launchable
apps, requires confirmation before leaving AgentOS, caches a bounded accessible
semantic snapshot, and revalidates page nodes before controlled click, scroll, or
text-input actions. It never reads another app's private database or account token.

The native Shell now shares one Compose visual system across home, media, app
providers, confirmations, notifications, and the complete knowledge graph. Voice
state is the home-screen focus, camera/gallery/apps/memory are immediate actions,
and the command composer remains fixed above the keyboard instead of being buried
at the end of a settings feed.

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
