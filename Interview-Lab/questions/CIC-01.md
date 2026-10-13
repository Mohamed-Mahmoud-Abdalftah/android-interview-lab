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

### Practical walkthrough in Egyptian Arabic

في فريق Android، أول PR لازم يطلع منه compile وlint وunit tests ونتيجة واضحة قبل الدمج؛ ده CI. بعد الدمج، pipeline تنتج AAB موقّع ومربوط بالـcommit وتجهزه لاختبار داخلي؛ ده Continuous Delivery حتى لو شخص يضغط زر النشر. لو نفس الـpipeline ترفعه تلقائيًا للمستخدمين بعد بوابات الجودة، ده Continuous Deployment. الفرّق هنا قرار الإفراج، مش مجرد وجود GitHub Actions. فشل اختبار في CI لازم يمنع دمج النسخة، وفشل بوابة crash بعد النشر يوقف زيادة rollout.

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

“For Android, I use CI to compile and test every PR, delivery to produce a signed, traceable AAB and deploy it to internal testing, and deployment when production rollout itself is automated after gates. Delivery can still include a human approval. The decision depends on test confidence, Play rollout controls, crash/fraud monitoring and ability to halt or recover.”

## Interview answer — deep senior

“I separate the three by when software becomes releasable and who decides release. Continuous Integration means small changes are integrated frequently with automated compile, lint and tests, so the main branch remains trustworthy. Continuous Delivery takes a passing commit through repeatable packaging, signing and verification to a release-ready artifact; a human or policy can still choose when to expose it to users. Continuous Deployment goes further and releases every eligible change automatically through policy gates. In an Android app I would pin the source commit and build variant to the AAB, run a signed release-like smoke test, then publish to an internal track before staged production rollout. I would not call an untested debug APK ‘delivered’. More automation shortens feedback but raises the cost of a weak gate, so I protect secrets, use approval boundaries for high-risk changes and monitor crashes and payment failures after rollout. The decisive question is which verified artifact crosses which trust boundary.”

## How to answer in the interview

- **Why:** CI exposes integration failures early.
- **How:** build and test each PR, then produce a traceable release artifact.
- **Trade-off:** faster release versus cost of stronger gates.
- **Failure case:** a green debug build hides a release-only crash.
- **Production solution:** gate signed release candidates and monitor staged rollout.

## Deep-dive talking points

Prompt for distinction between ready-to-release and automatic release, artifact provenance, Play rollout.

## Follow-up questions

- [CIC-10](../cic-10/): What does delivery produce? **Answer:** traceable artifact ready for internal/production track promotion.
- [CIC-14](../cic-14/): What protects deployment? **Answer:** staged rollout metrics and halt/recovery plan.

## Self-check rubric

Define CI, Continuous Delivery and Continuous Deployment with the exact boundary where a human approves release; give one Android AAB path through build, test, internal track and production.

## References and reviewed-on date

- [Android app publishing](https://developer.android.com/studio/publish) — release process.
- [Gradle build lifecycle](https://docs.gradle.org/current/userguide/build_lifecycle.html) — reproducible build tasks.

Technically reviewed against the cited primary documentation on 2026-10-13; automated technical review only, not human review.
