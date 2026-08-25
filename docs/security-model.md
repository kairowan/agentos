# Security model

## Trust zones

1. Android kernel, verified boot, keystore, update, recovery, and system-owned
   confirmations form the trusted foundation.
2. Capability Broker owns authorization, scoped grants, rate limits, revocation,
   and audit records.
3. Agent Runtime and model providers propose plans but hold no direct system power.
4. Generated UI and workflows are untrusted data rendered by bounded runtimes.
5. Files, webpages, messages, and model responses are hostile input by default.

## Implemented process boundary

`AgentShell` and `AgentCapabilityService` are separate platform packages. The
service is protected by `com.agentos.permission.USE_CAPABILITY_BROKER` at signature
level and also rejects Binder UIDs that do not resolve exclusively to the signed
shell package. Draft product SELinux policy places both packages in distinct domains
and grants only their Binder communication path.

The notification listener is owned by the Broker package and still requires explicit
Android user approval. Only bounded message-category events cross into the Shell;
they are not automatically persisted, spoken, sent to a model, or replied to.

Microphone access belongs to the selected system `VoiceInteractionService`, not the
HOME shell. Always-on detection uses SoundTrigger/DSP and an isolated
`HotwordDetectionService`; unsupported hardware fails closed instead of opening a
continuous software microphone. Recognized text crosses into the Shell through a
signature-protected receiver and a random, one-time in-memory ticket. The ticket
also prevents direct Intent injection into the exported HOME activity.

Conversation history is bounded, stored only in credential-protected application
storage, excluded from model prompts, and removable in the UI. Notification content
and model-inferred facts are not inserted into durable knowledge automatically.

## Required invariant

No model-controlled value becomes a Binder call, Intent, filesystem path, network
destination, shell command, or privileged argument without typed validation and
policy evaluation.

## Deterministic fallback

Boot, lock screen, connectivity, permissions, accessibility, emergency functions,
updates, and recovery remain usable when every model and network provider fails.
