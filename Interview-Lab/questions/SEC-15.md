---
id: "SEC-15"
question: "How do you prevent token leakage through logs, screenshots, crash reports, and analytics?"
topic: "Android Security, Crypto & Fintech Threat Modeling"
code: "SEC"
group: "B"
phase: 3
priority: "P1"
order: 312
editorial_status: "reviewed"
---

# SEC-15

## Original interview question

How do you prevent token leakage through logs, screenshots, crash reports, and analytics?

## What the interviewer evaluates

- Multiple data-exfiltration channels beyond persistent storage.
- Redaction, screenshot policy and observability without token values.

## Explanation in Arabic

Token ممكن يتسرب من `Authorization` header في HTTP logger، crash breadcrumb، analytics property، notification أو screenshot. تشفير storage مش بيعالج القنوات دي. سياسة logging لازم تكون allowlist: نسجل event type وcorrelation ID وstatus، ونحذف tokens/PAN/PIN وquery params الحساسة قبل ما تصل لأي SDK خارجي.

## Why it matters and how it works

Redaction is applied before data crosses an observability boundary, not only at dashboard display. Android `FLAG_SECURE` can prevent screenshots/recording for selected sensitive screens, but it has usability and platform limitations and cannot prevent all compromised-device capture. Crash SDKs and HTTP interceptors need separate configuration.

## Worked example

For sign-in troubleshooting, record `refresh_failed`, HTTP class, app version and an opaque request ID. Do not record the Authorization header, token prefix, password, raw request body or screenshot of account details. On a payment confirmation screen, evaluate `FLAG_SECURE` against product accessibility and support needs.

## Trade-offs and decision criteria

Allowlist telemetry reduces diagnostic detail, so add safe state transitions and correlation IDs. Screen capture blocking protects against some casual capture but can hinder support and still does not secure an instrumented process.

## Failure modes

Debug logging accidentally enabled in release can upload bearer tokens. A crash reporter may attach screenshots or custom attributes automatically. Audit SDK defaults, scan logs during tests, and revoke any credential found in telemetry.

## Production perspective

Use shared redaction at network and analytics boundaries, restrict dashboard access and retention, and test with synthetic secrets to ensure none reach collected events. Incident response includes secret rotation and affected-session revocation.

## Interview answer — short

“I prevent token leakage at every output boundary: logs, HTTP interceptors, crash reports, analytics, notifications and screenshots. I allowlist safe fields and use correlation IDs; local encryption alone does not solve this.”

## Interview answer — structured

“My logging policy records operational state rather than sensitive payloads. I remove Authorization headers and secret query parameters before network logs, disable body logging in release, and configure crash/analytics SDKs to avoid tokens and screenshots. For sensitive screens I may use FLAG_SECURE, aware of usability and device limitations. Tests inject a fake token and assert it never appears in telemetry. If one leaks, I revoke it rather than simply deleting the log. I test leakage with a synthetic token in a release-like build and inspect every telemetry sink, including network interceptors and crash attachments. An allowlist of event names, status and opaque correlation IDs is safer than trying to redact arbitrary payloads later. A screenshot flag can help on sensitive screens but is not a guarantee against a hostile device.”
## Interview answer — deep senior

“I treat observability as an exfiltration path with multiple sinks. Data classification drives an allowlist at source: event names, statuses, latency buckets and opaque correlation IDs; no PAN, PIN, CVV, bearer credentials, names or raw request bodies. I audit third-party SDK capture settings and retention, inspect release builds with synthetic canaries, and test error paths because exceptions often include headers or URLs. FLAG_SECURE is a screen-level mitigation, not a universal privacy guarantee on rooted devices. When a leak is detected, security response rotates/revokes credentials, limits access to stored telemetry and traces the affected versions. A banking app can encrypt a refresh token at rest and still leak it through a debug HTTP logger or crash breadcrumb. I define prohibited fields at collection time—credentials, PAN, PIN, raw bodies and sensitive query parameters—and allow only safe operational state. Third-party analytics and crash SDK defaults are reviewed before integration, because once data is uploaded, dashboard-side masking may be too late. For a confirmation screen I evaluate `FLAG_SECURE` against accessibility/support needs, while acknowledging that a rooted process can capture content elsewhere. Canary tests verify no synthetic secret reaches logs, screenshots or reports. If a real bearer token appears in telemetry, I contain access and revoke the underlying session rather than only deleting the event.”
## Deep-dive talking points

Audit redaction at HTTP logging, crash capture, analytics properties and screenshots; test release builds for accidental token exposure.

## Follow-up questions

- [SEC-30](../sec-30/): How do payment logs remain useful? **Answer:** correlation and state codes without card data.
- [SEC-14](../sec-14/): What if a token appears in logs? **Answer:** revoke the grant and remove/contain telemetry copies.

## Self-check rubric

Can I enumerate leak channels, design an allowlist, test redaction and state incident response?

## References and reviewed-on date

- [Android sensitive data guidance](https://developer.android.com/privacy-and-security/security-best-practices) — handling sensitive information.
- [OWASP MASTG tests](https://mas.owasp.org/MASTG/tests/) — storage and log verification.

Technically reviewed against the cited primary documentation on 2026-10-11; this is an automated editorial and technical review, not a human review.
