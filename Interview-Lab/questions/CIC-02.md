---
id: "CIC-02"
question: "What are typical stages in an Android CI pipeline?"
topic: "CI/CD, Git & Team Delivery"
code: "CIC"
group: "A"
phase: 4
priority: "P2"
order: 421
editorial_status: "reviewed"
---

# CIC-02

## Original interview question

What are typical stages in an Android CI pipeline?

## What the interviewer evaluates

- Dependency order of Android pipeline stages.
- Fast feedback, release variant fidelity and protected signing.

## Explanation in Arabic

Android CI المعتاد: checkout مضبوط، dependency resolution، format/lint/static checks، compile، JVM tests، instrumentation/device tests حسب risk، build AAB/APK، security/artifact checks، signing محمي، internal track، ثم staged production ومراقبة. لازم نختبر release-like variant لأن R8/flavor/ABI ممكن يغير السلوك.

## Why it matters and how it works

The pipeline is a graph, not necessarily one serial list. Independent lint and unit jobs run in parallel; artifacts are built once and promoted. Untrusted PR jobs must not receive signing secrets. Test reports and artifact hashes link back to source commit.

## Worked example

A payment app PR gates Kotlin compile, lint, JVM transaction-state tests and API contracts. Release candidate adds minified build, Room migration tests, emulator matrix and terminal hardware checks, then uploads the same AAB to internal testing.

## Trade-offs and decision criteria

Every PR running full hardware E2E is slow; sampling/affected-area selection improves speed but needs a broad release gate. Cache Gradle dependencies safely and invalidate on lockfile/toolchain changes.

## Failure modes

Debug tests pass while release R8 strips an SDK callback. A stage that rebuilds after tests may upload a different artifact. Test/publish the intended variant and record SHA and mapping.

## Production perspective

CI dashboard tracks stage duration, flake rate, artifact provenance and rollout health. A failed security/payment gate blocks promotion with an owner and diagnostic artifacts.

## Interview answer — short

“An Android CI pipeline checks source, builds and tests fast, validates release variants and devices, packages/signs a traceable artifact, then promotes through testing and staged rollout.”

## Interview answer — structured

“I place cheap high-signal checks early and parallelize independent jobs. JVM tests and static checks run on PRs; instrumented, migration and hardware flows run by risk before release. I build the actual minified flavor, protect signing secrets from PR code, and promote the same AAB through Play tracks. Reports, mapping files and hashes tie the release to the source commit.”

## Interview answer — deep senior

“I view CI as a supply chain. The source revision, Gradle/JDK/toolchain, dependencies and build variant are pinned or recorded; untrusted code runs without release credentials. Unit, contract, device and security checks each claim a specific boundary. The signed AAB is immutable across internal and production promotion, so we never retest one binary and ship another. I measure queue and critical-path time, shard slow tests and use staged rollout gates for crash, ANR and payment unknown-rate anomalies.”

## Deep-dive talking points

Prompt for pipeline graph, release variant, secret boundary, immutable artifact and rollout telemetry.

## Follow-up questions

- [CIC-09](../cic-09/): Where do signing keys run? **Answer:** protected release jobs, not untrusted PRs.
- [CIC-20](../cic-20/): What to optimize? **Answer:** measured critical path and high-cost stages.

## Self-check rubric

Can you explain this decision, apply the example, name a trade-off and failure, and answer both follow-ups without relying on a memorized slogan?

## References and reviewed-on date

- [Android build command line](https://developer.android.com/studio/build/building-cmdline) — build tasks.
- [Play release tracks](https://developer.android.com/studio/publish) — publishing workflow.

Technically reviewed against the cited primary documentation on 2026-10-11; automated technical review only, not human review.
