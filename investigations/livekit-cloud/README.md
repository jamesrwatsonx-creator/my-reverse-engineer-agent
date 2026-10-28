# LiveKit Cloud — REA investigation checkpoint

- Target: https://cloud.livekit.io/projects/p_2dlbc09r83f/overview
- Target type: authenticated SaaS console / realtime communications infrastructure
- Reviewed: 2026-10-28
- Status: **BLOCKED** for authenticated inspection; **PARTIAL** documented capability review
- Authorization: project URL supplied by user. No authenticated dashboard access or credentials available in this research session.
- Intended downstream product: Gods Eye View — personal and business agents, inbound/outbound reception, scheduling, local agent discovery and A2A communication.
- Evidence vocabulary: **OBSERVED** directly inspected; **DOCUMENTED** cited first-party source; **INFERRED** plausible architecture/proposed design; **UNKNOWN** inaccessible/not established.

## Executive finding

**DOCUMENTED:** LiveKit offers WebRTC realtime communications, SIP telephony, agent dispatch, SDK session reporting and Cloud agent observability. Use it as the media/telephony substrate, not the platform's master record system.
**PROPOSED:** Hermes owns persistent user/agent identity, sessions, memory, policies, tools, skills, scheduling and event history. Use a thin LiveKit adapter to carry audio and call metadata.
**UNKNOWN:** Configuration, enabled agents, trunks, regions, session activity, deployments, secrets and billing of this specific LiveKit project. Do not imply these are inspected.

## REA next authorized inspection

1. Reconnect authorized desktop and open the supplied project URL while logged in.
2. Run REA browser inspection against Overview, Agents, Sessions, Telephony, Settings, Dispatch, Observability (as present).
3. Collect sanitized page screenshots and network summaries; remove phone numbers, API keys, tokens, caller data, recordings and PII from committed evidence.
4. Compare actual project config with the documented integration surfaces and validate one test inbound/outbound session, if explicitly permitted.
5. Update all target files; replace UNKNOWN with evidence. Set status ACTIVE/PARTIAL/COMPLETE only when warranted, update registry, commit.

This folder is an initial evidence-grounded research dossier, **not** a claim that REA was executed on the private console.
