# Roadmap

## M0 — Build foundation

- Reproducible AOSP 17 synchronization
- AgentOS Cuttlefish product target
- Buildable primary HOME package

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
- [ ] Per-relation confirmation, correction, merge, and selective forgetting
- [ ] Enroll and calibrate the `Hey AgentOS` DSP model on target hardware
- [ ] Recovery integration and complete accessibility verification

## M2 — Capability platform

- [x] Typed capability registry and in-process policy broker
- [x] Trusted confirmation UI and bounded audit log
- [x] Initial read-only device capabilities
- [x] AIDL process boundary, signature permission, and caller identity checks
- [x] Broker-filtered incoming message events over one-way AIDL
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
