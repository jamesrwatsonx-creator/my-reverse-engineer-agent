# Feature inventory

## First-party LiveKit surfaces

| Capability | Status | Evidence | Product use |
|---|---|---|---|
| Realtime agent audio and web/mobile clients | DOCUMENTED | https://docs.livekit.io/agents/integrations/openai/ | browser/mobile user-agent sessions |
| Inbound SIP routing via trunks/dispatch rules | DOCUMENTED | https://docs.livekit.io/telephony/accepting-calls/inbound-trunk/ | business/personal receptionist |
| Outbound calls via SIP participants | DOCUMENTED | https://docs.livekit.io/telephony/making-calls/outbound-calls/ | approved reminder and delegated calls |
| Explicit dispatch and per-job metadata | DOCUMENTED | https://docs.livekit.io/agents/server/agent-dispatch/ | route correct agent/profile/tenant |
| Agent observability: transcripts, audio, traces, metrics | DOCUMENTED | https://docs.livekit.io/testing/observability/insights/ | call review, debugging, QA |
| Data hooks and session reports | DOCUMENTED | https://docs.livekit.io/testing/observability/data/ | persistent product-owned records |

## User-proposed product capabilities — NOT observed LiveKit features

### Onboarding and voice
- Human account / handle and personal + business agent profiles.
- Spoken welcome -> transcription/edit/clean-up -> synthetic voice preview -> explicit approval.
- Voice catalog, consent-verified own voice, licensed voice-actor options.
- Calendar connection or internal appointment management.

### Reception and relationships
- Inbound call inbox with transcript, summary, audio retention choice, actions, searchable history.
- Family/friends group with contact-sensitive greetings; caller ID is not strong authentication.
- Business outcomes: appointment, lead, quote request, customer support, order inquiry, dispatch, escalation.
- 'Text me if' rule builder by contact/group/business event; test before enabling.

### Task and preparation layer
- Conversational tomorrow plan; multi-calendar conflict resolution, time zones and reminder rules.
- Scheduled opt-in morning brief; per-task 'Prep me for' contextual agent call.
- Delegated outreach with approval, consent, bounded retries and recorded outcomes.

### Discovery and network
- Gods Eye View business pins, handles, unclaimed neutral listings, claim workflows.
- Public business Agent Card; private personal discoverability only with opt-in.
- Inbox and permissions for agent-to-agent requests, eventually standards-based A2A.
- Skills library and enterprise connectors; marketplace and wallet/token concepts deferred.

## Unknowns to inspect in LiveKit console
Plan/quotas, phone numbers, trunks, registered agents, region, deployment model, observability settings, data residency, usage, webhooks and authorization policy.
