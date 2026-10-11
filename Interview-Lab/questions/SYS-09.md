---
id: "SYS-09"
question: "Design analytics, logs, metrics, and crash reporting."
topic: "Android System Design & Architecture Decisions"
code: "SYS"
group: "A"
phase: 4
priority: "P1"
order: 338
editorial_status: "reviewed"
---

# SYS-09

## Original interview question

Design analytics, logs, metrics, and crash reporting.

## What the interviewer evaluates

Design privacy-aware analytics, structured logs, metrics and crash reporting.

## Explanation in Arabic

نفصل analytics للأفعال، logs للتشخيص، metrics للاتجاهات وcrash/ANR reporting للأعطال. كل event له schema, version, correlation ID وprivacy classification؛ ما نرسلش tokens, card data أو PII بدون حاجة وموافقة/سياسة مناسبة. نقيس startup, ANR, crash-free sessions, sync pending age وpayment unknowns، ونربط client/server IDs من غير كشف أسرار.

## Why it matters and how it works

Use structured events with sampling and retention limits. Offline telemetry can queue with bounded storage and WorkManager, respecting consent and network constraints. A server correlation ID helps trace one operation across retries. Crash reports need deobfuscation mapping for release and redaction of sensitive breadcrumbs.

## Worked example

Conceptual event contract; sink must enforce schema/redaction and consent.

```kotlin
data class OperationEvent(
    val name: String,
    val operationId: String,
    val stage: String,
    val durationMs: Long,
)
interface TelemetrySink { fun record(event: OperationEvent) }
// Never put access tokens, payment payloads or raw PII in event fields.
```

## Trade-offs and decision criteria

Detailed logs aid debugging but increase privacy/storage cost. Sampling reduces volume but can hide rare incidents; retain unsampled critical counters without sensitive payload. Client-only metrics miss server commit after lost response, so correlate both sides.

## Failure modes

Logging Authorization header leaks credentials. Treating a timed-out payment as failure metric hides Unknown outcomes. Analytics events with unstable names break dashboards. Storing endless offline telemetry can fill disk.

## Production perspective

A commerce app emits payment operation state transitions by opaque ID, records app crash/ANR vitals and sync backlog, and uses backend reconciliation metrics. Dashboards alert on increased Unknown age after staged rollout.

## Interview answer — short

“I define structured, versioned events for analytics and diagnosis, collect crash/ANR and performance metrics, and correlate client/server operations by opaque ID. I redact secrets and monitor business unknown states, not just HTTP errors.”

## Interview answer — structured

“I separate user analytics from operational telemetry. Logs explain individual failures, metrics show rates and latency, crash/ANR tools capture platform failures, and business events track durable state transitions. I define schemas and stable correlation IDs, redact tokens and personal data, and honor consent/retention policy. For offline uploads of telemetry I bound the queue. A payment timeout is measured as Unknown until reconciliation, so dashboards do not misclassify it as failure. Release mapping files make obfuscated traces actionable.”

## Interview answer — deep senior

“Observability should test the architecture’s promises. I instrument cold-start time, ANR/crash rate, API latency by endpoint, cache stale age, outbox pending age, token refresh failures and payment reconciliation delay. Every business operation has an opaque correlation ID shared with backend logs, but no credentials or full payment payload enter telemetry. Events are typed/versioned with ownership and retention; sampling controls high-volume traces while aggregate counters preserve trends. Offline telemetry uses bounded storage and consent-aware upload. I compare client and server views because a lost response can produce client timeout and server success. During staged rollout, alert thresholds and kill-switch criteria are defined before deployment. Logging Authorization header leaks credentials.”

## Deep-dive talking points

Choose SLOs and show how one opaque ID traces an ambiguous operation.

## Follow-up questions

- [SYS-17](../sys-17/): How use kill switch? **Answer:** tie it to measured guardrails and server enforcement.
- [DAT-20](../dat-20/): How observe lost response? **Answer:** correlate client Pending ID with server ledger status.

## Self-check rubric

Can I classify signals, redact data, bound offline storage and measure unknown outcomes?

## References and reviewed-on date

- [Android vitals](https://developer.android.com/google/play/vitals) — crash/ANR signals.
- [Android architecture guide](https://developer.android.com/topic/architecture) — data ownership.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-11; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
