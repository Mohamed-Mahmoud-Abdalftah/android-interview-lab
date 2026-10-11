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

PR gate لازم يدي feedback سريع على أخطاء شائعة: format/lint، compile، JVM tests، contract tests وaffected modules. Device UI، benchmark، hardware وfull E2E أبطأ فتشتغل parallel أو على merge/nightly/release حسب risk. بس payment/security invariants الخطيرة لازم تفضل gate قبل shipping حتى لو مش على كل PR.

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

“My PR gate usually compiles affected code, runs lint/static analysis, JVM unit tests and contracts in parallel. Slower emulator or E2E suites run by affected area, nightly or before release. I measure queue and execution time, cache deterministic dependencies, and shard device tests. A risk exception is explicit: payment idempotency or security boundary changes may require a slower required check immediately. The mechanics matter. A pipeline is a dependency graph with cost and detection value. Run cheap high-signal checks early, parallelize independent jobs, cache safely, and avoid repeating identical builds. Separate PR merge gate from release gate with explicit required status checks. The choice has a trade-off. Selective tests reduce PR time but can miss hidden dependencies. Use module graph plus a broad scheduled suite and monitor escape rate. Caches speed builds but must not reuse signing secrets or invalid artifacts.”

## Interview answer — deep senior

“I optimize for time-to-reliable-signal, not simply shortest pipeline. I classify checks by cost, flake rate and historical defect catch, then put quick deterministic failures first and parallelize independent jobs. A changed-module graph can select tests, but broad scheduled/release suites catch dependency mistakes. Quarantine has ownership and expiry, and first-failure artifacts remain visible. I profile the critical path, not just total CPU time, and require release gates for migrations, signing, security and provider/hardware flows that PR sampling cannot prove. Consider a concrete case. PR changing ViewModel runs module JVM tests, static checks and compile; nightly runs emulator matrix; release candidate runs migration, POS hardware and payment-lost-response tests. If PR touches transaction code, trigger targeted backend idempotency contract gate immediately. A failure case illustrates the risk. Making flaky UI tests optional forever erodes trust; quarantined tests need owner/deadline. Conversely, serializing all device tests blocks every small docs PR for 40 minutes. Profile and shard intelligently. In production, the response is concrete. Publish per-stage duration, queue time, flaky rate and defect escapes. Review gates after incidents, and prevent merge when critical source/contract tests fail. The decision has a trade-off. Selective tests reduce PR time but can miss hidden dependencies. Use module graph plus a broad scheduled suite and monitor escape rate. Caches speed builds but must not reuse signing secrets or invalid artifacts.”

## Deep-dive talking points

Prompt for critical path, risk-triggered checks, cache correctness, flake governance and release gates.

## Follow-up questions

- [CIC-20](../cic-20/): How optimize a 40-minute CI? **Answer:** profile queue/build/test critical path first.
- [TST-23](../tst-23/): Which tests cannot be skipped? **Answer:** those proving high-impact release risks.

## Self-check rubric

Can you explain the mechanism, reproduce the example, justify the trade-off, identify the failure case, and answer both follow-ups for this question?

## References and reviewed-on date

- [Android CI guidance](https://developer.android.com/studio/build/building-cmdline) — command-line builds.
- [Gradle performance](https://docs.gradle.org/current/userguide/performance.html) — build optimization.

Technically reviewed against the cited primary documentation on 2026-10-11; automated technical review only, not human review.
