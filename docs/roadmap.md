# Roadmap

## M0 — Build foundation

- Reproducible AOSP 17 synchronization
- AgentOS Cuttlefish product target
- Buildable primary HOME package

## M1 — Trusted shell

- [x] Deterministic offline shell path
- [x] Validated declarative UI schema and renderer
- [ ] Recovery integration and complete accessibility verification

## M2 — Capability platform

- [x] Typed capability registry and in-process policy broker
- [x] Trusted confirmation UI and bounded audit log
- [x] Initial read-only device capabilities
- [x] AIDL process boundary, signature permission, and caller identity checks
- [ ] Compile and validate SELinux domains in a complete AOSP image
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

- Physical-device bring-up, verified boot, OTA, rollback, CTS, and VTS
