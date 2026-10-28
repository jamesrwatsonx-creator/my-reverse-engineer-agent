# UX and experience requirements

**Status: INFERRED/PROPOSED.** The linked authenticated LiveKit console could not be visually inspected. No screen measurements or LiveKit branding claims are asserted.

## Gods Eye View product direction
- Dark, responsive web-first UI with fast mobile layouts, restrained glass/gradient surfaces, accessible contrast and motion-reduction mode.
- Desktop: contextual left rail and command/search bar. Mobile: bottom navigation Home, Inbox, Calendar/Tasks, Explore, Agent.
- A personal/business mode switch in one account, with clear color/text context and separated permissions.
- First session: choose identity -> record welcome -> AI text cleanup -> voice preview -> approve -> connect calendar -> call test. Never present an agent as live before successful test/activation.
- Personal dashboard: calls, friends/family, agent chat, to-dos, tomorrow plan, prep, skills, integrations.
- Business dashboard: calls/leads, customer history, appointments, quote/order/support outcomes, marketing opt-in, agent settings, team/inbox.
- Call review detail: transcript as a navigable document, call summary, tasks created, lead/status, consent/recording state, audio if enabled.
- Rule builder: natural language input -> structured WHEN/IF/THEN card -> simulation -> explicit activate.
- Gods Eye View: a claimable public business directory. 'Unclaimed' listings are clearly labeled and should not pretend an owner authorized an AI.
- Hide marketplace purchasing controls until there are real listings. Keep underlying skill registry present.
- Explicit public/private visibility and exact-location safeguards; never show users' live location by default.

## Testable UI flows
1. User approves polished greeting after hearing the same voice their agent will use.
2. Call triggers a structured outcome (booking / message / request).
3. Owner reviews transcript, corrects summary, sends a follow-up only with permission.
4. User creates 'text me if urgent family call' and tests it without notifying a real contact.
5. Owner finds an unclaimed business, proves control via approved channel, then activates the agent.
6. Personal agent proposes a next-day schedule; nothing is modified before approval.
