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

Flaky test على CI فقط تحتاج triage مبني على evidence، مش `retry: 3` وخلاص. سجّل test order/shard، seed، API level، CPU pressure، screenshot، logcat وnetwork timing. شغّلها منفردة ثم بعد tests اللي قبلها؛ لو فشلت بعد logout مثلًا، راجع Singleton fake أو DB ما اتصفّرتش.

## Practical walkthrough

لو ترتبط بالضغط، ابحث عن fixed sleeps أو race بين listener والassertion، واستخدم fake gate أو انتظار state/semantics محددة. قارن config المحلية بـCI: locale/timezone، minified variant، parallel workers. Quarantine مؤقتة لها owner وexpiry وتغطية بديلة للflow الحرجة؛ retry يخفي نسبة الفشل ولا يصلح السبب. بعد fix، أعد التشغيل بعدد كاف وفي نفس shard الأصلي.

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

“I compare the failing CI shard, emulator image, API level, test order and resource load with local runs. I loop the focused test and adjacent tests, inspect screenshots/logs and replace sleeps with explicit synchronization. If shared fakes or database rows leak, I reset them; if the app has a race, I fix it and add a regression. A bounded retry or quarantine is visible and owned, not silently green.”

## Interview answer — deep senior

“I preserve the failed run as evidence before changing the test. I record build SHA, device or emulator image, shard, order, seed, logcat, screenshot and timing. Then I rerun the test alone and paired with its predecessor. If a checkout test fails only after logout, I inspect shared DI fakes, database rows and session singletons; if it fails under CPU load, I look for fixed sleeps and unsynchronized callbacks. I change the causal boundary—reset per-test state, inject a controlled fake, or wait for a user-visible semantics condition—and rerun the original CI shard repeatedly. I do not just increase the sleep or add three retries. Retries can be useful diagnostic sampling, but a green retry is still evidence of nondeterminism. If the test must be quarantined to unblock unrelated work, it gets an owner, expiry, incident link and another release gate for the critical behavior. I also check whether the flake reveals a genuine app race, such as a late payment result overwriting a newer screen; in that case the production code needs a fix, not only the test.”

## How to answer in the interview

- **Why:** CI-only flakes may reveal shared state or a real race.
- **How:** capture shard, seed and logs, reproduce in order and fix the causal boundary.
- **Trade-off:** temporary quarantine versus coverage loss.
- **Failure case:** longer sleep only lowers failure frequency.
- **Production solution:** repeated original-shard run with owned quarantine policy.

## Deep-dive talking points

Prompt for first-failure artifact, same shard/order reproduction, race versus harness, owned quarantine.

## Follow-up questions

- [TST-15](../tst-15/): What replaces sleep? **Answer:** test clock, idling or observable-condition waits.
- [CIC-13](../cic-13/): How should pipeline treat flakes? **Answer:** visible bounded retry/quarantine policy.

## Self-check rubric

Reproduce the CI-only failure with its shard/order/environment, preserve logs and seed, isolate shared state or timing, then verify repeated green runs. State when a retry masks rather than fixes the defect.

## References and reviewed-on date

- [Android testing guidance](https://developer.android.com/training/testing) — test environment and reliability.
- [Compose testing](https://developer.android.com/develop/ui/compose/testing) — synchronization APIs.

Technically reviewed against the cited primary documentation on 2026-10-12; automated technical review only, not human review.
