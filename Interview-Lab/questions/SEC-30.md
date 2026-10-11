---
id: "SEC-30"
question: "A payment app must mask PAN and avoid sensitive logs. Design a logging/observability policy."
topic: "Android Security, Crypto & Fintech Threat Modeling"
code: "SEC"
group: "C"
phase: 3
priority: "P1"
order: 327
editorial_status: "reviewed"
---

# SEC-30

## Original interview question

A payment app must mask PAN and avoid sensitive logs. Design a logging/observability policy.

## What the interviewer evaluates

- PAN masking, PIN/CVV exclusion and correlation without sensitive payloads.
- Redaction before third-party SDK boundaries and retention.

## Explanation in Arabic

Payment observability لازم تشرح الحالة من غير PAN/PIN/CVV أو tokens. نخزن operation ID عشوائي، transition، error code، latency وSDK/device version. لو نعرض card، نستخدم masked PAN وفق قواعد provider/PCI المطبقة ونمنع full PAN في logs، screenshots، crash attachments وanalytics. PIN ما يدخلش app logs إطلاقًا.

## Why it matters and how it works

Use an allowlist schema and redact at event creation, before crash/analytics upload. Correlation IDs are opaque, non-reversible and separate from card identifiers. Data retention/access controls apply to telemetry too. Card-data handling requirements depend on the certified payment flow and applicable PCI program; do not infer compliance from masking alone.

## Worked example

Event `payment_reversal_pending {operationId: opaque UUID, reasonCode: TIMEOUT, sdkVersion: X, attempt: 2}` is useful. Event `charge_failed {pan: 4111..., pin: ..., requestBody: ...}` is forbidden. The client and backend share the opaque ID for trace correlation.

## Trade-offs and decision criteria

Redaction reduces debugging detail, so use precise state codes and provider references that are safe under contract. More detailed data may require a controlled, short-lived diagnostic process with security approval, never blanket raw logging.

## Failure modes

An HTTP interceptor enabled in release logs ISO 8583/card payloads before the app logger redacts them. Audit every sink, including vendor SDKs, and use synthetic canaries in release-like tests. Rotate any exposed credentials and contain logs after incidents.

## Production perspective

Build a telemetry dictionary with prohibited fields, safe event types, retention, role access and automated leak tests. The backend reconciles transaction outcomes using IDs and provider records rather than card values in app logs.

## Interview answer — short

“I log opaque operation IDs, states and error codes, never PAN/PIN/CVV or tokens. Redaction happens before any logger or third-party SDK, with retention and access controls.”

## Interview answer — structured

“A payment log must answer what happened without exposing cardholder data. I define allowlisted events for transaction state, timing, SDK version and opaque correlation IDs. Full PAN, PIN, CVV, bearer tokens and raw request bodies are excluded from app and backend telemetry. I test release logging and vendor SDK behavior with canary values, and set retention and access limits. Masked display data is handled under the relevant payment-provider and PCI obligations, not assumed compliant just because it is partially hidden.”

## Interview answer — deep senior

“I design observability around the state machine and transaction identity: intent recorded, sent, unknown, reconciled, reversed, with stable opaque IDs and safe provider status codes. Every sink is reviewed—Logcat, network interceptor, crash attachments, analytics, support export and SDK diagnostics—and schema validation rejects prohibited fields before upload. I avoid PAN-derived correlation IDs because they can become linkable sensitive data. Access to production telemetry is audited and time-limited. I run synthetic secret-canary tests on release builds and coordinate incident response if any sink captured card or token data.”

## Deep-dive talking points

Prompt for allowlist, every telemetry sink, opaque IDs, canary tests, retention and payment-program review.

## Follow-up questions

- [PAY-10](../pay-10/): How do IDs aid observability? **Answer:** join state transitions without logging card fields.
- [SEC-15](../sec-15/): Why redact before SDK upload? **Answer:** downstream deletion cannot reliably undo disclosure.

## Self-check rubric

Can I specify safe fields, forbidden fields, test a release logger and state residual compliance scope?

## References and reviewed-on date

- [OWASP MASVS storage](https://mas.owasp.org/MASVS/controls/MASVS-STORAGE-1/) — sensitive data minimization.
- [Android security best practices](https://developer.android.com/privacy-and-security/security-best-practices) — logging and data handling.

Technically reviewed against the cited primary documentation on 2026-10-11; this is an automated editorial and technical review, not a human review.
