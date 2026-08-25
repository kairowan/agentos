# Architecture

AgentOS keeps its trusted computing base small and preserves AOSP's kernel,
HAL, Binder, media, connectivity, keystore, update, and recovery foundations.

## System layers

1. **AgentVoiceService** is the selected Android voice assistant. It owns the DSP
   hotword detector and opens only one on-device speech-recognition turn at a time.
2. **AgentShell** is the primary HOME experience and renders trusted fallback UI.
3. **Agent Runtime** interprets goals, plans work, and manages resumable workflows.
4. **Capability Broker** runs in a separate package, process, UID, and SELinux domain;
   typed AIDL is the only route from model decisions to capability implementations.
5. **Generative UI Runtime** renders validated declarative screens and workflows.
6. **Model Router** selects local or remote models without granting either system access.
7. **Memory Service** separates ephemeral context, preferences, credentials, and audit data.

Voice is the primary intent path: Android's `VoiceInteractionService` and
`AlwaysOnHotwordDetector` receive a low-power SoundTrigger/DSP match, an isolated
`HotwordDetectionService` verifies it, and one on-device recognizer turn feeds the
same Agent Runtime used by text fallback. Silence closes the recognizer; TTS reads
only voice-originated responses and then re-arms detection. Incoming notification
events travel in the opposite direction—from Android into the Broker, through a
bounded local filter, then over a one-way AIDL callback to the Shell.

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
partition. AgentOS first uses AOSP's system APIs and resource overlays; upstream
framework changes are reserved for capabilities that cannot be expressed safely
through those boundaries. Physical-device hotword support still requires the
device's SoundTrigger HAL, DSP model enrollment, and vendor audio policy.
