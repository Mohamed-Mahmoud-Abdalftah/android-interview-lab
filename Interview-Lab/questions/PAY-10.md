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

“I log payment state transitions and opaque correlation IDs, not card data or secrets. Redaction happens before telemetry SDKs, and alerts focus on unresolved or aging operations.”

## Interview answer — structured

“Observability should let us answer whether an intent was persisted, sent, approved, unknown or reversed. I emit events at durable state changes with an opaque operation ID, safe status code, timing and app/SDK version. I never log PAN, PIN, CVV, raw payloads or bearer tokens; third-party SDK capture is audited. Dashboards alert on old unknowns and reversal queue backlog, and reconciliation links to provider references in restricted records. Use short retention and access controls.”

## Interview answer — deep senior

“I define an event schema from the payment state machine and validate it at compile/test and ingestion boundaries. An operation ID connects terminal and backend; a separate attempt count shows retries without new business identity. Events come after DB commits so they reflect durable facts, and at-least-once telemetry is deduplicated in analysis. I test every error path with synthetic sensitive canaries, including vendor callback `toString()`, network interceptors and crash attachments. Access and retention are limited, and on-call views show opaque IDs with a controlled path to authoritative provider status rather than raw financial payloads. ”

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

Technically reviewed against the cited primary documentation on 2026-10-11; this is an automated editorial and technical review, not a human review.
