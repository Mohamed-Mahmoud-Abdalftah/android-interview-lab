---
id: "TST-24"
question: "How do you gate PRs without creating an unreasonably slow pipeline?"
topic: "Testing, Quality & Reliability"
code: "TST"
group: "C"
phase: 4
priority: "P1"
order: 419
editorial_status: "reviewed"
---

# TST-24

## Original interview question

How do you gate PRs without creating an unreasonably slow pipeline?

## What the interviewer evaluates

- Fast PR gates versus slower risk-specific release checks.
- Parallelism, caching, ownership and signal quality.

## Explanation in Arabic

PR gate هدفها feedback سريع على أخطاء التغيير، لكن السرعة لا تبرر إسقاط invariant مالي أو أمني. شغّل formatting/lint/static checks، compilation وtargeted JVM tests على كل PR؛ استخدم changed-module scope بحذر لأن shared module تؤثر على غيرها. شغّل emulator suites الأصغر على المخاطر أو merge queue، وnightly matrix للأجهزة والmigrations، مع release candidate gate لـPOS hardware/provider sandbox.

## Practical walkthrough

لو PR لمس transaction، شغّل backend idempotency contract فورًا حتى لو أبطأ. قِس median وp95 feedback time وأسباب failures، وقلّل setup/cache misses قبل حذف coverage. أي quarantine لها owner وexpiry؛ release لا يمر إذا اختبار حرج flaky بلا بديل.

## Why it matters and how it works

A pipeline is a dependency graph with cost and detection value. Run cheap high-signal checks early, parallelize independent jobs, cache safely, and avoid repeating identical builds. Separate PR merge gate from release gate with explicit required status checks.

## Worked example

PR changing ViewModel runs module JVM tests, static checks and compile; nightly runs emulator matrix; release candidate runs migration, POS hardware and payment-lost-response tests. If PR touches transaction code, trigger targeted backend idempotency contract gate immediately.

## Trade-offs and decision criteria

Selective tests reduce PR time but can miss hidden dependencies. Use module graph plus a broad scheduled suite and monitor escape rate. Caches speed builds but must not reuse signing secrets or invalid artifacts.

## Failure modes

Making flaky UI tests optional forever erodes trust; quarantined tests need owner/deadline. Conversely, serializing all device tests blocks every small docs PR for 40 minutes. Profile and shard intelligently.

## Production perspective

Publish per-stage duration, queue time, flaky rate and defect escapes. Review gates after incidents, and prevent merge when critical source/contract tests fail.

## Interview answer — short

“I run fast, high-signal checks early and parallelize them, then schedule slower device and E2E checks according to risk. Critical security/payment checks remain mandatory before release.”

## Interview answer — structured

“My PR gate usually compiles affected code, runs lint/static analysis, JVM unit tests and contracts in parallel. Slower emulator or E2E suites run by affected area, nightly or before release. I measure queue and execution time, cache deterministic dependencies, and shard device tests. A risk exception is explicit: payment idempotency or security boundary changes may require a slower required check immediately. ”

## Interview answer — deep senior

“I design the pipeline around both feedback latency and risk. Every PR gets fast compile, lint/static checks and focused JVM tests so developers learn quickly. A module-aware selection can help, but a shared API or build-logic change must trigger dependents; otherwise the fast path gives false confidence. I run targeted emulator tests on risky UI, database or platform changes, and a broader API/device matrix nightly or in a merge queue. A release candidate must pass migrations from supported schemas, minified startup, payment lost-response cases and any required terminal or provider sandbox verification. Some invariants are too important to defer: if a PR changes transaction identity or authorization, the backend idempotency contract gate should run immediately. I profile the critical path—dependency downloads, Gradle configuration, compilation, emulator boot and test runtime—before removing checks. I publish median and p95 feedback time alongside escape rate, because faster green builds that miss incidents are not a win. Flaky critical tests get an owner and replacement gate, not a permanent silent retry.”

## How to answer in the interview

- **Why:** slow PR checks delay feedback, but missing gates leak serious defects.
- **How:** keep fast compile/static/JVM checks, trigger targeted device/backend gates by risk.
- **Trade-off:** feedback latency versus coverage and CI cost.
- **Failure case:** changed-module selection misses a shared API dependent.
- **Production solution:** profile pipeline and require critical release invariants.

## Deep-dive talking points

Prompt for critical path, risk-triggered checks, cache correctness, flake governance and release gates.

## Follow-up questions

- [CIC-20](../cic-20/): How optimize a 40-minute CI? **Answer:** profile queue/build/test critical path first.
- [TST-23](../tst-23/): Which tests cannot be skipped? **Answer:** those proving high-impact release risks.

## Self-check rubric

Name a fast PR gate for compilation, focused JVM tests and static checks; place device/hardware suites on risk triggers or later stages; define a hard release gate for payment invariants and measure feedback time.

## References and reviewed-on date

- [Android CI guidance](https://developer.android.com/studio/build/building-cmdline) — command-line builds.
- [Gradle performance](https://docs.gradle.org/current/userguide/performance.html) — build optimization.

Technically reviewed against the cited primary documentation on 2026-10-12; automated technical review only, not human review.
