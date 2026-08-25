# Architecture

AgentOS keeps its trusted computing base small and preserves AOSP's kernel,
HAL, Binder, media, connectivity, keystore, update, and recovery foundations.

## System layers

1. **AgentShell** is the primary HOME experience and renders trusted fallback UI.
2. **Agent Runtime** interprets goals, plans work, and manages resumable workflows.
3. **Capability Broker** runs in a separate package, process, UID, and SELinux domain;
   typed AIDL is the only route from model decisions to capability implementations.
4. **Generative UI Runtime** renders validated declarative screens and workflows.
5. **Model Router** selects local or remote models without granting either system access.
6. **Memory Service** separates ephemeral context, preferences, credentials, and audit data.

Voice is the primary intent path: a replaceable speech recognizer feeds the same
Agent Runtime used by text fallback, and text-to-speech reads only responses to
voice-originated requests. Incoming notification events travel in the opposite
direction—from Android into the Broker, through a bounded local filter, then over a
one-way AIDL callback to the Shell.

## Process boundary

Models and generated code never run in `system_server` or the capability-service
process. The service requires a signature permission and verifies the Binder calling
UID, exact package identity, and matching signing certificate before parsing a
request. Generated code, when introduced, runs in a sandbox without direct Binder,
filesystem, network, camera, microphone, or location access.

## Failure contract

Boot, lock screen, networking, permissions, updates, recovery, accessibility, and
emergency functions retain deterministic interfaces. A model or network failure
must not make the device unusable.

## Integration strategy

Custom code lives under `vendor/agentos` and is installed through the product
partition. Changes to upstream AOSP and hardware interfaces are deferred until a
stable platform API cannot provide the required behavior.
