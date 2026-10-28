# Portable capabilities / buy-integrate-build decisions

| Capability | Input -> Output | Decision | Phase |
|---|---|---|---|
| live-voice-session | mic/audio -> agent speech | INTEGRATE LiveKit; Hermes orchestration | V0 |
| sip-reception | inbound number + caller -> scoped agent call | INTEGRATE LiveKit trunk/dispatch | V1 |
| voice-onboarding | welcome audio -> edited text -> preview -> approved greeting | BUILD UX + integrate STT/TTS | V1 |
| post-call-review | session events -> transcript, summary, outcome, tasks | BUILD app using LiveKit SDK hooks | V1 |
| appointment-scheduler | availability/resources -> hold/confirm/reschedule | BUILD core, CONNECT Google/Microsoft | V1 |
| conditional-notify | event + contact rules -> permitted notification | BUILD deterministic policy engine | V1 |
| personal-daily-plan | tasks/calendars -> reviewed schedule -> opt-in brief call | BUILD on Hermes | V1.5 |
| preflight-prep | task/context -> relevant prep brief + permitted outreach proposal | BUILD | V1.5 |
| agent-network-inbox | agent message -> permissioned request/task state | BUILD tenant-safe inbox | V2 |
| business-claims | POI + registered entity + verified control signals -> claim status | BUILD workflow; INTEGRATE registries | V2 |
| geo-discovery | indexed POI + service capability -> search/pins | INTEGRATE licensed data; BUILD claim augmentation | V2 |
| a2a-gateway | authorized agent card/request -> routed task/result | INTEGRATE A2A spec | V3 |
| skill-library | trusted capability manifest -> enabled scoped tool | BUILD curated catalog and testing | V1 |
| creator-marketplace | rated versioned skills -> paid install/payout | DEFER public monetization | V4 |
| wallet-reputation | signed claim/receipt -> portable attestation | DEFER, optional and chain-agnostic | V5 |
| property-claims | legal owner proof -> separate property entitlement | RESEARCH; do not conflate with business tenancy | V5+ |

## Hard design lines
- Public discoverability is a capability/consent decision, not a consequence of possessing a phone or being onsite.
- Never auto-activate an unclaimed business representative that promises bookings or makes authoritative statements without business opt-in.
- Voice cloning requires authorized use; do not scrape celebrities' YouTube clips for secret cloning.
- No unsolicited automated promotional calls or texts; use explicit opt-in/consent audit for marketing.
