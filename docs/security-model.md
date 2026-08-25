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

## Required invariant

No model-controlled value becomes a Binder call, Intent, filesystem path, network
destination, shell command, or privileged argument without typed validation and
policy evaluation.

## Deterministic fallback

Boot, lock screen, connectivity, permissions, accessibility, emergency functions,
updates, and recovery remain usable when every model and network provider fails.
