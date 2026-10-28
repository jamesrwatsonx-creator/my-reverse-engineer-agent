# Evidence log — 2026-10-28

## Authenticated LiveKit project (UNKNOWN)
- URL: https://cloud.livekit.io/projects/p_2dlbc09r83f/overview
- Method: attempted web fetch without user's authenticated LiveKit browser session; denied/disabled.
- REA runtime inspection: NOT EXECUTED. Connected authorized computer was offline; connected browser required originating extension/browser context.
- No LiveKit settings, sessions, credentials, trunk numbers, UI screenshots, billing, plans or calls were observed.
- Never record login secrets, access tokens, phone numbers, caller PII or unredacted customer content in this repository.

## First-party documented product capabilities (DOCUMENTED)
1. https://docs.livekit.io/agents/integrations/openai/ — Web/mobile voice AI integration, telephony and interruption support. Inspected 2026-10-28 via public documentation.
2. https://docs.livekit.io/telephony/accepting-calls/inbound-trunk/ — SIP provider/number and inbound trunk/dispatch requirements. Inspected 2026-10-28.
3. https://docs.livekit.io/telephony/making-calls/outbound-calls/ — agent dispatch + outbound SIP participant. Inspected 2026-10-28.
4. https://docs.livekit.io/agents/server/agent-dispatch/ — explicit dispatch and metadata, inbound SIP routing. Inspected 2026-10-28.
5. https://docs.livekit.io/testing/observability/insights/ — Cloud transcripts/traces/logs/audio, retention and PII redaction. Inspected 2026-10-28.
6. https://docs.livekit.io/testing/observability/data/ — SDK session events and make_session_report. Inspected 2026-10-28.

## Cross-system documented constraints
7. https://world.org/faqs — World ID proves uniqueness of a human through ZK; does not by itself validate business ownership. Inspected 2026-10-28.
8. https://github.com/a2aproject/A2A/blob/main/docs/specification.md — A2A agents, Agent Cards, tasks and messages. Inspected 2026-10-28.
9. https://developer.android.com/reference/android/service/voice/VoiceInteractionService — Android assistant service exists; third-party hotword availability/device support must be tested. Inspected 2026-10-28.
10. https://developer.apple.com/documentation/Intents — Siri/App Intents integration, not arbitrary global Siri replacement. Inspected 2026-10-28.
11. https://developers.google.com/maps/documentation/places/web-service/policies — Places API storage/display restrictions. Inspected 2026-10-28.
12. https://docs.overturemaps.org/guides/places/ — open business POI dataset with publisher-specific source licensing. Inspected 2026-10-28.
13. https://www.priv.gc.ca/en/privacy-topics/surveillance/02_05_d_14/ — Canadian privacy guidance for recorded business calls. Inspected 2026-10-28.
14. https://crtc.gc.ca/eng/phone/telemarketing/tobligations/rules-regles.htm — express-consent restrictions for automated telemarketing. Inspected 2026-10-28.
15. https://elevenlabs.io/docs/eleven-creative/voices/voice-cloning — rights, verification and own-voice cloning constraints. Inspected 2026-10-28.

## User-origin requirements (PROPOSED, not evidence about LiveKit)
Welcome editing/playback; custom/celebrity voices; personal and business agents; friends/family conditional text alerts; morning plan/prep calls; task delegation, contact browser/wake word; skills/marketplace; calendar; business lead workflow; Gods Eye View claimable map; privacy-preserving proof-of-human/business claim; international ambassador acquisition; future wallets/tokens/property.

## Unknowns
Authenticated project state, actual voice stack chosen, model/voice service configuration, call flow, cost per minute, regional data residency, configured integrations, telephony vendor, Android device wake-word restrictions, POI source rights, business-claim jurisdictional registry coverage.
