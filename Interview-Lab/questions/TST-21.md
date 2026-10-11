---
id: "TST-21"
question: "A flaky test passes locally but fails on CI. Explain triage and mitigation."
topic: "Testing, Quality & Reliability"
code: "TST"
group: "C"
phase: 4
priority: "P1"
order: 416
editorial_status: "reviewed"
---

# TST-21

## Original interview question

A flaky test passes locally but fails on CI. Explain triage and mitigation.

## What the interviewer evaluates

- CI-only flake diagnosis with evidence before mitigation.
- Test order, sharding, emulator/resource and race hypotheses.

## Explanation in Arabic

اختبار ينجح محليًا ويفشل CI مش معناه “CI بطّيء” فقط. نجمع first failure artifacts، seed، device/API، shard، test order وtiming. نعيد على نفس image وبـstress loop، ونشوف shared state، Main dispatcher cleanup، network، animation أو race في app. Retry مؤقت ممكن يساعد التشخيص بس ما نخفيش فشل أصلي.

## Why it matters and how it works

CI differs in CPU contention, scheduling, filesystem, locale and emulator version. A deterministic test should synchronize on observable conditions, isolate fixtures and clean up global state. If repeated runs expose an app race, fix production code and add a lower-level regression test.

## Worked example

A Compose test fails only when run after logout tests. Rerun the pair in the same shard; discover a singleton fake retained session state. Reset DI/test DB per case and assert teardown. If the flake instead tracks low CPU, replace a fixed sleep with semantics wait or fake-clock control.

## Trade-offs and decision criteria

Retrying can keep a pipeline usable temporarily but increases cost and hides risk; quarantine needs owner, expiry and equivalent release coverage for high-risk flows. Longer timeouts may help legitimate slow operations but are not a race fix.

## Failure modes

Blindly increasing sleep from 1 to 5 seconds reduces one symptom while preserving an app concurrency bug. Preserve first-failure logs/screenshot and test ordering evidence; do not delete a payment gate.

## Production perspective

Track flake rate, affected branches/devices and time-to-fix. CI publishes first-attempt failure even when retry passes, enabling prioritization.

## Interview answer — short

“I reproduce the CI environment, capture first-failure evidence, and isolate timing, shared state or app races. Retries are temporary diagnostics; I fix synchronization or production behavior and retain critical gates.”

## Interview answer — structured

“I compare the failing CI shard, emulator image, API level, test order and resource load with local runs. I loop the focused test and adjacent tests, inspect screenshots/logs and replace sleeps with explicit synchronization. If shared fakes or database rows leak, I reset them; if the app has a race, I fix it and add a regression. A bounded retry or quarantine is visible and owned, not silently green. ”

## Interview answer — deep senior

“I use a hypothesis table: environment mismatch, test harness synchronization, cross-test contamination or real app concurrency bug. I preserve artifacts from attempt one, run the same container/device and shard order repeatedly, and instrument state transitions. If a critical checkout test is flaky, I cannot simply quarantine it without another gate; I may move the invariant to a deterministic domain/backend test while repairing UI coverage. I measure flake rate and CI cost, set owner/deadline, and close only after repeated clean runs on the original environment.”

## Deep-dive talking points

Prompt for first-failure artifact, same shard/order reproduction, race versus harness, owned quarantine.

## Follow-up questions

- [TST-15](../tst-15/): What replaces sleep? **Answer:** test clock, idling or observable-condition waits.
- [CIC-13](../cic-13/): How should pipeline treat flakes? **Answer:** visible bounded retry/quarantine policy.

## Self-check rubric

Can you explain the mechanism, reproduce the example, justify the trade-off, identify the failure case, and answer both follow-ups for this question?

## References and reviewed-on date

- [Android testing guidance](https://developer.android.com/training/testing) — test environment and reliability.
- [Compose testing](https://developer.android.com/develop/ui/compose/testing) — synchronization APIs.

Technically reviewed against the cited primary documentation on 2026-10-11; automated technical review only, not human review.
