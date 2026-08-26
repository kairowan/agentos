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

Conversation history and its semantic graph are stored through Room in a
credential-protected SQLite database and removable in the UI through confirmed
destructive actions. Old history is excluded from model prompts. When a
remote model is enabled, only the current prompt receives an additional structured
knowledge-extraction request. Model relations require exact source evidence, remain
marked as candidates, and cannot authorize capabilities. Notification content is
not inserted into durable knowledge.

AgentShell does not hold camera or microphone permissions. Native capture is owned
by the separately sandboxed AgentMediaService, which accepts only the single
platform-signed Shell package over a signature permission. Android camera/microphone
AppOps indicators and foreground notifications remain enabled. Failed captures
delete pending MediaStore rows rather than exposing partial files.

The installed-app bridge is signature-protected and does not request visibility of
every installed package. Accessibility access requires explicit user enablement;
snapshots and inputs are bounded. App launch, text input, and transaction-like
clicks use short-lived one-time confirmations. Queued operations revalidate the
target package, node path, class, and text before execution, so a changed page
cannot silently redirect an approved action.

## Required invariant

No model-controlled value becomes a Binder call, Intent, filesystem path, network
destination, shell command, or privileged argument without typed validation and
policy evaluation.

## Deterministic fallback

Boot, lock screen, connectivity, permissions, accessibility, emergency functions,
updates, and recovery remain usable when every model and network provider fails.
