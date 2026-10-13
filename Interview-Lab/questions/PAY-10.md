---
id: "PAY-10"
question: "How do you make a payment workflow observable without logging PAN/PIN or secrets?"
topic: "Bonus: Payment/POS & Security Scenarios"
code: "PAY"
group: "B"
phase: 5
priority: "P2"
order: 480
editorial_status: "reviewed"
---

# PAY-10

## Original interview question

How do you make a payment workflow observable without logging PAN/PIN or secrets?

## What the interviewer evaluates

- Observability of state transitions without PAN/PIN or secret leakage.
- Correlation IDs, redaction and unresolved-operation alerts.

## Explanation in Arabic

نعمل telemetry للـpayment workflow باستخدام opaque operation ID، state transition، timestamp، duration، SDK version وsafe error code. ممنوع PAN/PIN/CVV، raw ISO message، token أو request body. هدف logs يعرفنا العملية واقفة فين وهل reversal اتبعت، من غير ما يحول monitoring system لمخزن card data.

## Practical walkthrough

سجل `intent_persisted → sent → unknown → lookup → confirmed` مع operation ID ومدة ونسخة SDK، من غير request body أو raw ISO message. حتى exception من SDK ممكن تحتوي card data؛ اعمل redaction قبل Crashlytics/monitoring. خليك واضح إن PAN نفسها تخضع لمتطلبات حماية لو اتعاملت معاها، وPIN/CVV لا تتخزن بعد authorization وفق PCI DSS.

## Why it matters and how it works

Instrument the state machine at its durable transition boundary so events reflect committed state, not only UI clicks. Correlate terminal, backend and provider with a stable ID and map provider references in restricted storage. Redact before third-party crash/analytics SDKs receive data.

## Worked example

For `operationId=6f…`, safe events are `intent_persisted`, `authorization_sent`, `outcome_unknown`, `status_lookup_succeeded`, and `reversal_confirmed`, with latency and SDK build. A dashboard flags unknown older than the expected provider SLA.

## Trade-offs and decision criteria

Fine-grained events improve incident diagnosis but add volume and privacy risk. Use short retention and access controls. Do not use a PAN-derived hash as a “safe” correlation ID; it can still be linkable.

## Failure modes

Logging a vendor callback object via `toString()` may include track/card fields. Review SDK payloads and use an explicit allowlist DTO; inject canary PAN/PIN values in tests and assert they never appear in collected telemetry.

## Production perspective

Operations dashboards show pending age, retry count and divergence between ledgers. Alerts route unresolved payments to reconciliation staff with an opaque ID and controlled lookup access.

## Interview answer — short

“I log safe state transitions and timing under an opaque operation ID, not card payloads. I redact SDK errors before third-party telemetry and correlate only through restricted references.”

## Interview answer — structured

“Observability should let us answer whether an intent was persisted, sent, approved, unknown or reversed. I emit events at durable state changes with an opaque operation ID, safe status code, timing and app/SDK version. I never log PAN, PIN, CVV, raw payloads or bearer tokens; third-party SDK capture is audited. Dashboards alert on old unknowns and reversal queue backlog, and reconciliation links to provider references in restricted records. Use short retention and access controls. I allowlist fields before an event reaches crash or analytics tooling.”

## Interview answer — deep senior

“I define an event schema from the payment state machine and validate it at compile/test and ingestion boundaries. An operation ID connects terminal and backend; a separate attempt count shows retries without new business identity. Events come after DB commits so they reflect durable facts, and at-least-once telemetry is deduplicated in analysis. I test every error path with synthetic sensitive canaries, including vendor callback `toString()`, network interceptors and crash attachments. Access and retention are limited, and on-call views show opaque IDs with a controlled path to authoritative provider status rather than raw financial payloads.  I would inspect SDK exception messages and raw request logging paths because redaction at one logger is insufficient. I instrument the durable transition boundary rather than just button taps: intent committed, authorization sent, response unknown, status resolved, and reversal confirmed. Each event has an opaque ID, monotonic duration, timestamp, terminal model, SDK version, and allowlisted error code. I do not log raw request or ISO messages, PAN, PIN block, CVV, access tokens, or unrestricted exception text. PCI SSC explicitly prohibits retaining sensitive authentication data such as PIN blocks and card verification codes after authorization; PAN also requires controlled handling. I audit crash SDK breadcrumbs, HTTP interceptors, and support exports because a single redaction function is not enough. Dashboards alert on old Unknown and reversal-pending records, with restricted drill-down.”

## How to answer in the interview

- **Why:** responders need state evidence without making logs a card-data store.
- **How:** emit structured events at committed transitions with opaque IDs.
- **Trade-off:** redaction reduces raw detail but preserves safe diagnosis.
- **Failure case:** SDK exception or payload logs leak PAN, PIN block, or CVV.
- **Production solution:** allowlisted fields, retention controls, access review, and alerting on unknown age.

## Deep-dive talking points

Prompt for event-on-commit, operation versus attempt IDs, canary leak tests, backlog alerts and restricted provider mapping.

## Follow-up questions

- [PAY-05](../pay-05/): Why stable correlation? **Answer:** it joins terminal/backend/provider records.
- [SEC-30](../sec-30/): What data is forbidden? **Answer:** PAN/PIN/CVV, secrets and raw payloads.

## Self-check rubric

Can I specify an allowlisted event schema and operational alert without card data?

## References and reviewed-on date

- [OWASP MASVS storage](https://mas.owasp.org/MASVS/controls/MASVS-STORAGE-1/) — sensitive-data minimization.
- [Android app architecture data layer](https://developer.android.com/topic/architecture/data-layer) — durable data ownership.
- [PCI SSC FAQ on sensitive authentication data](https://www.pcisecuritystandards.org/faqs/1533/) — PIN block and card verification data must not be retained after authorization.

Technically reviewed against the cited primary documentation on 2026-10-11; this is an automated editorial and technical review, not a human review.
