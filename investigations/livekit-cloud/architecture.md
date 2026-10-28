# Architecture hypotheses and proposed implementation

## Verified boundaries
**DOCUMENTED:** LiveKit SDK handles realtime rooms, audio, SIP legs, explicit dispatch, session observability and data hooks.
**UNKNOWN:** Technical configuration and enabled features of the supplied authenticated Cloud project.
**PROPOSED:** Persistent agent orchestration, users, permissions and business records belong outside LiveKit (Hermes + application services).

## Reference flow
Phone call -> number/SIP trunk -> LiveKit room/dispatch -> thin voice adapter -> Hermes agent session -> policy + context + tools -> speech/TTS -> LiveKit audio.
On completed call -> signed session result + transcript/events -> event bus -> DB/object storage -> inbox, leads, calendar actions, analytics, audit.

## Services / ownership
- Identity/auth: platform account and agent profiles; optional World ID unique human proof; role/team permissions.
- Hermes: stateful sessions, memory retrieval, skills, model routing, tool/action execution, delegated tasks.
- Voice adapter: LiveKit token issuance, participant context, interruption handling, SIP routing and TTS/STT connector.
- Scheduling: first-party resource/appointment model; external Google/Microsoft calendars with OAuth; slot holds, conflict checks, time zone and idempotency.
- Contacts/CRM: person vs business contact, relationship tags, lead stages, ticket/quote/order service types.
- Rule engine: 'WHEN event / IF context / THEN notification / ELSE queue', human-approval gates, throttling and consent.
- Network: public business profile, handles, business claim status, agent inbox, discoverable capabilities, A2A-compatible gateway.
- Maps: own licensable POI dataset and MapLibre/other renderer with permitted source licenses; verified claimed profiles augment the directory.
- Data: Postgres (+ PostGIS for geospatial), row-level tenant separation, object storage for consented recordings, vector or search index for memory retrieval; background workers for retries/webhooks/scheduled tasks.

## Minimal canonical entities
Account, Organization, Membership, Agent, AgentPolicy, Skill, ConnectorGrant, Contact, Relationship, Conversation, CallSession, TranscriptTurn, ActionRequest, Approval, Task, TaskDependency, Event, Calendar, AvailabilityRule, Appointment, Lead, NotificationRule, BusinessListing, BusinessClaim, VerificationEvidence, AgentMessage, AuditEvent.

## Security invariants
- Each tool call has a tenant, agent, user/delegation principal, scope, purpose, approval rule and audit event.
- Do not use caller ID or voice mimicry alone to authorize disclosure or sensitive actions.
- Public business discovery != authorized business owner/agent.
- World ID uniqueness proof != business control, property ownership, or right to act for a company.
- GPS proximity != identity, ownership, or authority; spoofable and optional supporting evidence only.
- Sensitive transactions and outbound marketing need explicit scoped authorization, rate limits, consent checks and human review.
- Personal memory never becomes publicly accessible through agent search/MCP or business cross-tenant tooling.
- MCP exposes tools to properly scoped callers; A2A handles independently run agent discovery/tasks/messages; never treat either as security by itself.

## Build-test gates
- Inbound and outbound test calls; handle barge-in, failure, dropped calls, retries, no double booking.
- One client/person -> personal and business agents with demonstrably isolated data.
- Approved schedule creation, conflict check, reschedule, cancel and no accidental side effects.
- Idempotent webhooks and call outcomes; signed audit path for each external action.
- Prompt injection in websites, call transcripts and MCP responses cannot authorize external data release.
