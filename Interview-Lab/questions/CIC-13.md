---
id: "CIC-13"
question: "How do you deal with flaky tests, retries, and quarantine policies?"
topic: "CI/CD, Git & Team Delivery"
code: "CIC"
group: "B"
phase: 4
priority: "P2"
order: 432
editorial_status: "reviewed"
---

# CIC-13

## Original interview question

How do you deal with flaky tests, retries, and quarantine policies?

## What the interviewer evaluates

- Flake classification, visible retries and bounded quarantine.
- Maintaining release coverage for critical flows.

## Explanation in Arabic

Flaky test يفشل أحيانًا بنفس code؛ ممكن يكشف race حقيقي أو test harness timing. نسجل first attempt والenvironment، نعيد للتشخيص، ونصلح السبب. Retries محدودة ومعلنة، quarantine لها owner وdeadline وبديل يغطي risk؛ مش نحول test red إلى green بصمت. Payment/security gate لا يُشال لمجرد إنه مزعج.

## Why it matters and how it works

CI retries can distinguish intermittent from deterministic failure but cannot identify cause alone. Quarantining removes a signal from required checks, so it needs risk assessment. Track flake rate per test, shard and device; preserve first-failure artifacts.

## Worked example

Compose test fails 2% on CI. Keep first screenshot/log, run on same emulator image and shard order, find a fixed sleep around network. Replace with fake response gate and semantics wait; remove retry after repeated clean runs.

## Trade-offs and decision criteria

Immediate quarantine may unblock work but increases escape risk. A small retry budget can reduce random infrastructure noise while adding latency. Critical financial invariants need lower-level deterministic tests during UI repair.

## Failure modes

A race in app code is mislabeled “test flake” and ignored. Analyze state traces and process timing before changing timeouts. Deleting the test without equivalent coverage is an unrecorded release risk.

## Production perspective

Weekly flake dashboard assigns owners; quarantine expiry fails or escalates. CI stores original failure even after retry success and trends test health.

## Interview answer — short

“I preserve first-failure evidence, identify app versus harness versus environment cause, and use retries or quarantine only as visible, time-limited mitigations.”

## Interview answer — structured

“A flaky test is a reliability bug in either the app, test or environment. I reproduce on the same CI image, inspect timing and shared state, then replace sleeps with deterministic synchronization or fix the app race. CI can retry once for diagnosis, but the original failure remains visible. Quarantine has an owner, deadline and alternate coverage, especially for security/payment flows.”

## Interview answer — deep senior

“I govern flakes as production risk. I track rate and cost, group by emulator/device and shard order, preserve logs/screenshots from attempt one and test hypotheses with repeated focused runs. If an app race caused it, I add a lower-level regression and fix state ownership. A quarantined critical test must have a compensating gate before release; otherwise the release is blocked. I avoid blanket retries that hide a rising failure rate and slow every PR. Compose test fails 2% on CI.”

## Deep-dive talking points

Prompt for first failure, same-environment reproduction, app race, quarantine owner.

## Follow-up questions

- [TST-21](../tst-21/): How triage CI-only? **Answer:** compare device image, order and resource load with artifacts.
- [TST-24](../tst-24/): How keep PR fast? **Answer:** improve reliability before adding retries.

## Self-check rubric

Can you explain the mechanism, apply the example, justify a trade-off, identify a failure mode, and answer both follow-ups?

## References and reviewed-on date

- [Android testing guidance](https://developer.android.com/training/testing) — reliable test practice.
- [Gradle test execution](https://docs.gradle.org/current/userguide/java_testing.html) — test reporting.

Technically reviewed against the cited primary documentation on 2026-10-11; automated technical review only, not human review.
