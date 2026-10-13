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

Risk-based test plan تبدأ من تهديدات التغيير: token storage migration، key invalidation، backup restore، logout race، tampered amount، logs فيها بيانات حساسة، وminified build. رتّب likelihood × impact وحدد owner وrelease gate لكل خطر. JVM tests لسياسة auth والredaction، Android tests لـKeystore/backup/lifecycle على API matrix، backend tests ترفض تعديل amount أو reuse غير مصرح، وpenetration/manual review للحدود الحساسة.

## Practical walkthrough

لا تجعل SDK أو local flag سلطة على payment؛ server هو authority. قبل release جرّب بيانات من الإصدار القديم، وتأكد من reauthentication عند فقد key بدل decrypt fallback غير آمن. السجل يذكر ما تم اختباره فعلاً وما بقي جهاز/مزود-dependent.

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

“For a security release I rank risks such as credential leakage, insecure backup, exported components, TLS misconfiguration and payment replay. I map each to a test: static artifact/manifest inspection, dynamic device tests, backend authorization and idempotency tests, and provider sandbox flows. I run the actual minified variant and record evidence and unresolved limitations. Rollout gates monitor both attacks and legitimate-user failures. I keep a rollback trigger for any unresolved high-impact risk.”

## Interview answer — deep senior

“I begin with a threat and change inventory, then assign evidence to each release risk. If the release changes token storage, I test migration from old encrypted data, missing or invalidated Keystore keys, backup restore to another device, logout and refresh races, and log redaction. A JVM suite covers policy and state transitions; Android instrumentation covers platform key and lifecycle behavior on supported API levels; a minified release-like build catches R8 or manifest differences. Backend tests prove it rejects a tampered amount, replayed or unauthorized request even if the client UI is modified. I prioritize by impact and likelihood, not by which test is easiest to automate, and give each blocking case an owner. A security SDK verdict is only a signal; it cannot replace server authorization. I also define what happens when a key is unrecoverable: clear a replaceable token and require sign-in rather than manufacturing a plaintext default. The release report states exact device, provider and environment coverage. I do not claim one emulator or a passing fake proves all hardware and threat-model behavior.”

## How to answer in the interview

- **Why:** security-sensitive changes need risk-weighted evidence.
- **How:** map token migration, key loss, backup, tampering and logs to test layers.
- **Trade-off:** release cost versus exposure and impact.
- **Failure case:** client SDK verdict is treated as authorization.
- **Production solution:** backend checks, device matrix and exact coverage report.

## Deep-dive talking points

Prompt for threat-to-test matrix, real boundary, release variant, residual risk and rollout gate.

## Follow-up questions

- [SEC-25](../sec-25/): How use MASVS? **Answer:** map controls to MASTG evidence, not checkboxes.
- [CIC-14](../cic-14/): Why staged rollout? **Answer:** constrain blast radius and observe real cohorts.

## Self-check rubric

Rank token migration, key invalidation, backup restore, tampered requests and log leakage by likelihood and impact. Assign each a test layer and release gate, including a minified build and backend authorization check.

## References and reviewed-on date

- [OWASP MASVS](https://mas.owasp.org/MASVS/) — mobile security controls.
- [OWASP MASTG](https://mas.owasp.org/MASTG/) — test methods.

Technically reviewed against the cited primary documentation on 2026-10-12; automated technical review only, not human review.
