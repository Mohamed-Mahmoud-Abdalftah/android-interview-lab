---
id: "CIC-01"
question: "What are CI, Continuous Delivery, and Continuous Deployment?"
topic: "CI/CD, Git & Team Delivery"
code: "CIC"
group: "A"
phase: 4
priority: "P2"
order: 420
editorial_status: "reviewed"
---

# CIC-01

## Original interview question

What are CI, Continuous Delivery, and Continuous Deployment?

## What the interviewer evaluates

- Integration, delivery and deployment as different release automation levels.
- Human approval versus automatic production release.

## Explanation in Arabic

CI معناها كل change يتبني ويتفحص باختبارات متكررة بعد دمجه أو على PR. Continuous Delivery يخلي artifact صالح للنشر في أي وقت لكن ممكن خطوة production تبقى بموافقة. Continuous Deployment ينشر production تلقائيًا بعد gates. المصطلحات مش مجرد GitHub Actions؛ لازم pipeline موثوق، tests، signing، rollout ومراقبة.

## Why it matters and how it works

CI shortens integration feedback; delivery keeps a release candidate reproducible; deployment automates the production transition. A pipeline can be CI even if release is manual. A green build only proves its configured checks, not absence of defects.

## Worked example

Android PR runs compile/lint/JVM tests; merge produces signed AAB and uploads to internal testing; release manager approves a staged Play rollout after device and payment checks. That is continuous delivery, not automatic production deployment.

## Trade-offs and decision criteria

Automatic deployment reduces lead time but needs strong gates and rollback; manual approval can help high-risk releases but may add delay. Choose based on risk, telemetry and organizational controls.

## Failure modes

Calling a nightly build “continuous deployment” while production publishing is manual confuses accountability. Shipping directly from a developer laptop breaks reproducibility. Keep artifact provenance and immutable versioning.

## Production perspective

Production pipeline records source commit, build toolchain, test evidence, signed artifact hash, track promotion and rollout metrics. Security/payment critical changes get explicit release criteria.

## Interview answer — short

“CI continuously validates integrated changes; continuous delivery keeps a releasable artifact ready; continuous deployment automatically promotes passing changes to production.”

## Interview answer — structured

“For Android, I use CI to compile and test every PR, delivery to produce a signed, traceable AAB and deploy it to internal testing, and deployment when production rollout itself is automated after gates. Delivery can still include a human approval. The decision depends on test confidence, Play rollout controls, crash/fraud monitoring and ability to halt or recover. The mechanics matter. CI shortens integration feedback; delivery keeps a release candidate reproducible; deployment automates the production transition. A pipeline can be CI even if release is manual. A green build only proves its configured checks, not absence of defects. The choice has a trade-off. Automatic deployment reduces lead time but needs strong gates and rollback; manual approval can help high-risk releases but may add delay. Choose based on risk, telemetry and organizational controls.”

## Interview answer — deep senior

“I design the pipeline around artifact provenance and risk. A single immutable artifact is built from a known commit, validated at multiple layers, signed with protected credentials and promoted through tracks. If production rollout is automatic, crash and business metrics must stop expansion quickly; high-risk migrations or payment SDK changes may need human approval. CI does not claim every security or hardware risk has been tested. I measure lead time and change failure rate while retaining the ability to identify and roll back a bad release. Consider a concrete case. Android PR runs compile/lint/JVM tests; merge produces signed AAB and uploads to internal testing; release manager approves a staged Play rollout after device and payment checks. That is continuous delivery, not automatic production deployment. A failure case illustrates the risk. Calling a nightly build “continuous deployment” while production publishing is manual confuses accountability. Shipping directly from a developer laptop breaks reproducibility. Keep artifact provenance and immutable versioning. In production, the response is concrete. Production pipeline records source commit, build toolchain, test evidence, signed artifact hash, track promotion and rollout metrics. Security/payment critical changes get explicit release criteria. The decision has a trade-off. Automatic deployment reduces lead time but needs strong gates and rollback; manual approval can help high-risk releases but may add delay. Choose based on risk, telemetry and organizational controls.”

## Deep-dive talking points

Prompt for distinction between ready-to-release and automatic release, artifact provenance, Play rollout.

## Follow-up questions

- [CIC-10](../cic-10/): What does delivery produce? **Answer:** traceable artifact ready for internal/production track promotion.
- [CIC-14](../cic-14/): What protects deployment? **Answer:** staged rollout metrics and halt/recovery plan.

## Self-check rubric

Can you explain this decision, apply the example, name a trade-off and failure, and answer both follow-ups without relying on a memorized slogan?

## References and reviewed-on date

- [Android app publishing](https://developer.android.com/studio/publish) — release process.
- [Gradle build lifecycle](https://docs.gradle.org/current/userguide/build_lifecycle.html) — reproducible build tasks.

Technically reviewed against the cited primary documentation on 2026-10-11; automated technical review only, not human review.
