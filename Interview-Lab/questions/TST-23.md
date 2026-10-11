---
id: "TST-23"
question: "How would you create a risk-based test plan for a security-sensitive release?"
topic: "Testing, Quality & Reliability"
code: "TST"
group: "C"
phase: 4
priority: "P1"
order: 418
editorial_status: "reviewed"
---

# TST-23

## Original interview question

How would you create a risk-based test plan for a security-sensitive release?

## What the interviewer evaluates

- Threat-driven release test scope and evidence.
- Highest-risk trust boundaries, regression and rollout monitoring.

## Explanation in Arabic

Security-sensitive release ما ينفعش تتقاس بعدد tests فقط. نحدد assets وattack paths: token leak، backup، exported component، TLS، tampered client، payment duplicate. نربط كل risk بـunit/integration/device/backend test ودليل، ونشغّل release variant على أجهزة ممثلة. High-risk unresolved finding يمنع release أو يحتاج قرار موثق من أصحاب الصلاحية.

## Why it matters and how it works

A risk-based plan ranks likelihood and impact, then assigns verification at the boundary that can actually prove a control. Static scanning catches configuration errors; dynamic tests catch runtime behavior; backend tests verify financial authority. Staged rollout watches residual risks.

## Worked example

For a banking update that changes token storage, test migration from old encrypted data, key invalidation, backup restore, logout, refresh races and log redaction. Add a tampered-client request test to prove server rejects changed amounts. Run minified APK smoke on supported API levels.

## Trade-offs and decision criteria

Broad exhaustive device coverage is costly; choose representative API/ABI/OEM cohorts based on exposure and incident history. Automated scans help prioritize but do not replace manual threat review or provider certification.

## Failure modes

Team runs only unit tests and claims security complete while a new exported Activity accepts forged extras. Inspect merged manifest and execute hostile intents. A passing client test cannot prove backend authorization.

## Production perspective

Record risk owner, test evidence, residual limitation and release gate. Roll out gradually with anomaly dashboards, rollback plan and incident escalation; monitor both security and legitimate-user false positives.

## Interview answer — short

“I start from assets and threats, then choose tests that prove each control at its real boundary. I include release APK/device checks, backend tamper tests, and monitored staged rollout.”

## Interview answer — structured

“For a security release I rank risks such as credential leakage, insecure backup, exported components, TLS misconfiguration and payment replay. I map each to a test: static artifact/manifest inspection, dynamic device tests, backend authorization and idempotency tests, and provider sandbox flows. I run the actual minified variant and record evidence and unresolved limitations. Rollout gates monitor both attacks and legitimate-user failures. Staged rollout watches residual risks. ”

## Interview answer — deep senior

“My plan has a traceability matrix from threat to invariant to evidence. A client storage migration is tested across old data, key loss, process death and backup restore; a backend payment rule is attacked with a modified APK/request; observability is scanned for canary secrets. I select devices by API, ABI and incident exposure, then use staged rollout with crash, fraud and false-positive signals. If a critical control fails, I halt or scope the release and document an explicit risk decision rather than silently reducing tests.”

## Deep-dive talking points

Prompt for threat-to-test matrix, real boundary, release variant, residual risk and rollout gate.

## Follow-up questions

- [SEC-25](../sec-25/): How use MASVS? **Answer:** map controls to MASTG evidence, not checkboxes.
- [CIC-14](../cic-14/): Why staged rollout? **Answer:** constrain blast radius and observe real cohorts.

## Self-check rubric

Can you explain the mechanism, reproduce the example, justify the trade-off, identify the failure case, and answer both follow-ups for this question?

## References and reviewed-on date

- [OWASP MASVS](https://mas.owasp.org/MASVS/) — mobile security controls.
- [OWASP MASTG](https://mas.owasp.org/MASTG/) — test methods.

Technically reviewed against the cited primary documentation on 2026-10-11; automated technical review only, not human review.
