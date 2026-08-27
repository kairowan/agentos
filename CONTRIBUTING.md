# Contributing

Use the platform repository for implementation changes and this repository for
architecture, bootstrap, release planning, and AOSP source composition.

Before submitting a change:

```bash
./scripts/check.sh
```

Architecture proposals must describe the user goal, process boundary, required
Android privilege, failure behavior, and smallest runnable acceptance check.
Implementation changes should remain outside upstream AOSP wherever a product
module or stable platform API can provide the behavior.

## Useful first contributions without a build server

- Test the `v0.4.0` APK pre-release or a specific platform CI artifact and report
  the exact tag/commit, device/API level, steps, expected/actual result, and redacted logs.
- Reproduce an issue and follow up after a fix; incomplete or negative results are useful.
- Add a small denial/error-path test, clarify setup instructions, or improve the
  build evidence self-checks. Describe the acceptance check before starting a large change.

Use platform issues for app/runtime behavior and this repository for AOSP bootstrap,
build measurements, or architecture. A full AOSP host is not required for these
component contributions. Never include account credentials or private conversation
data in logs. Independent participation must be genuine, not manufactured metrics.

Release tags should represent meaningful, documented milestones. Re-running CI or
editing a roadmap alone is not a new OS release. Keep APK, full-image, boot-smoke,
and physical-device validation results explicitly separate.

By contributing, you agree that your contribution is licensed under Apache-2.0.
