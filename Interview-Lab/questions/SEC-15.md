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

## Practical walkthrough

ممكن network interceptor يطبع `Authorization` header في debug ثم نفس logger يتفعل في release بالغلط. اعمل allowlist للأحداث بدل redact بعد ما السر انتشر: `operationId`, status, latency كفاية للتشخيص. راجع crash attachments وanalytics وscreenshots كأنها مخازن بيانات. للواجهات الحساسة استخدم سياسة screen capture مناسبة واختبر إنها ما تكسرش الدعم أو accessibility.

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

“I define an allowlist of safe telemetry fields such as opaque operation ID, status, error code, latency and app version. Tokens, passwords, PAN, PIN, CVV, raw request bodies and headers never reach the logging API. I audit Logcat, network interceptors, crash attachments, analytics and screenshots on a release build, because redacting one logger is insufficient. Screen-capture controls may help on sensitive views, subject to product and accessibility needs, and telemetry itself needs retention and access limits.”

## Interview answer — deep senior

“My logging policy starts with an allowlist of fields, not a redaction pass over a raw request. For sign-in or payment failures I need an opaque operation ID, state, safe reason code, latency and app version. I do not pass Authorization headers, PAN, PIN, CVV or request bodies into Logcat, crash SDKs or analytics. I would audit every sink on a release build, including network interceptors and screenshots, then test with canary secret values to catch leaks. Screen capture controls may be appropriate for sensitive views, but their usability effect must be considered. Retention and access controls limit exposure if telemetry itself is compromised. I would create a canary token in a test environment, exercise login, refresh, failure and crash paths, then search release Logcat, telemetry payloads and support attachments for that token. No arbitrary string field should accept card or credential data. If support needs a screenshot, provide a safe diagnostic view instead of capturing a payment screen. Auditing includes third-party SDK defaults because a logger outside our wrapper can still leak data.”

## How to answer in the interview

- **Why:** telemetry sinks create durable copies of secrets.
- **How:** allowlist safe fields before logging, disable body/header capture, and review crash/analytics sinks.
- **Trade-off:** less raw telemetry requires better correlation IDs.
- **Failure case:** a token enters a third-party SDK before redaction.
- **Production solution:** release-build leak tests and restricted access/retention.

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

Technically reviewed against the cited primary documentation on 2026-10-13; this is an automated editorial and technical review, not a human review.
