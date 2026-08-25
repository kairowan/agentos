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

By contributing, you agree that your contribution is licensed under Apache-2.0.

