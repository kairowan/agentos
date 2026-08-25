# Architecture

AgentOS keeps its trusted computing base small and preserves AOSP's kernel,
HAL, Binder, media, connectivity, keystore, update, and recovery foundations.

## System layers

1. **AgentShell** is the primary HOME experience and renders trusted fallback UI.
2. **Agent Runtime** interprets goals, plans work, and manages resumable workflows.
3. **Capability Broker** is the only route from model decisions to privileged APIs.
4. **Generative UI Runtime** renders validated declarative screens and workflows.
5. **Model Router** selects local or remote models without granting either system access.
6. **Memory Service** separates ephemeral context, preferences, credentials, and audit data.

## Process boundary

Models and generated code never run in `system_server`. Privileged operations use
typed AIDL contracts, scoped grants, timeouts, audit records, and deterministic
system-owned confirmation UI. Generated code, when introduced, runs in a sandbox
without direct Binder, filesystem, network, camera, microphone, or location access.

## Failure contract

Boot, lock screen, networking, permissions, updates, recovery, accessibility, and
emergency functions retain deterministic interfaces. A model or network failure
must not make the device unusable.

## Integration strategy

Custom code lives under `vendor/agentos` and is installed through the product
partition. Changes to upstream AOSP and hardware interfaces are deferred until a
stable platform API cannot provide the required behavior.

