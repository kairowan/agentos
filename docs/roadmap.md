# Roadmap

The downloadable baseline is **v0.4.0, an APK pre-release**. Checked implementation
items below describe component-level work, not a verified AOSP system image or
production-ready hardware support. No complete AOSP 17 image has been validated.

## M0 — Build foundation

- [x] Buildable standalone primary HOME and capability-service APKs
- [x] AgentOS Cuttlefish product definition and pinned platform source revision
- [x] Local sync/build evidence collector and offline failure-path self-checks
- [ ] Complete AOSP 17 checkout and successful full product image build
- [ ] Publish resolved manifest, build log, machine shape, duration, and image checksums
- [ ] Boot the matching image in Cuttlefish and verify system-installed AgentOS packages
- [ ] Measure persistent storage, cache/output usage and burst compute requirements
- [ ] Demonstrate independent contributions or external user feedback with follow-up
- [ ] Accumulate several months of substantive maintenance before hosting reconsideration

See [the build runbook](aosp-build.md) and [hosting evidence checklist](cloud-build-sponsorship.md).
Offline self-checks do not count as a successful AOSP build; real DSP, camera HAL,
CTS/VTS, and SELinux integration remain separate acceptance work.

## M1 — Trusted shell

- [x] Deterministic offline shell path
- [x] Validated declarative UI schema and renderer
- [x] Voice-first input and spoken response provider boundaries
- [x] System VoiceInteractionService and isolated hotword-service boundary
- [x] Silence-ended, one-turn on-device command recognition
- [x] Hotword barge-in for active planning and spoken responses
- [x] Complete Room/SQLite conversation history and virtualized full-history view
- [x] Automatic semantic graph extraction with evidence and confidence
- [x] Full interactive graph canvas with pan, 0.35x-4x zoom, and entity/relation editing
- [x] Persistent node layout, full-graph search, match navigation, and viewport culling
- [x] Native Camera2, photo/video, recorder, and MediaStore workspace vertical slice
- [ ] Target-device Camera HAL, stabilization, stream-combination, and OEM extension calibration
- [ ] Per-relation confirmation, correction, merge, and selective forgetting
- [ ] Enroll and calibrate the `Hey AgentOS` DSP model on target hardware
- [ ] Recovery integration and complete accessibility verification

## M2 — Capability platform

- [x] Typed capability registry and in-process policy broker
- [x] Trusted confirmation UI and bounded audit log
- [x] Initial read-only device capabilities
- [x] AIDL process boundary, signature permission, and caller identity checks
- [x] Broker-filtered incoming message events over one-way AIDL
- [x] Installed-app registry, confirmed launch, and bounded accessibility-semantic bridge
- [x] Multi-domain provider catalog with capabilities and generic fallback
- [x] Unified native Compose visual system and task-first Shell navigation
- [ ] App-specific adapters using deep links, MediaSession, share targets, or semantic fallback
- [ ] Compile and validate SELinux domains in a complete AOSP image
- [ ] Confirmed notification replies and lock-screen privacy policy
- [ ] Scoped grants, quotas, and revocation

## M3 — Agent runtime

- [x] Deterministic local planner and optional OpenAI-compatible provider
- [x] Cancellation and fail-safe offline fallback
- [ ] Resumable workflows and user-visible execution trace
- [ ] Adversarial prompt-injection test corpus

## M4 — Generated experiences

- Persistent workflows as user-owned software
- Sandboxed extension runtime
- Import, export, provenance, signing, and rollback

## M5 — Device product

- SoundTrigger HAL, DSP hotword power/accuracy calibration, and audio policy
- Physical-device TTS barge-in echo/false-wake acceptance matrix
- Physical-device bring-up, verified boot, OTA, rollback, CTS, and VTS
