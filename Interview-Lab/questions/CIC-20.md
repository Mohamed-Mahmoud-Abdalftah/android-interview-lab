---
id: "CIC-20"
question: "The CI pipeline takes 40 minutes. How would you profile and prioritize optimizations?"
topic: "CI/CD, Git & Team Delivery"
code: "CIC"
group: "C"
phase: 4
priority: "P2"
order: 439
editorial_status: "reviewed"
---

# CIC-20

## Original interview question

The CI pipeline takes 40 minutes. How would you profile and prioritize optimizations?

## What the interviewer evaluates

- Critical-path profiling rather than random optimization.
- Queue, Gradle, tests and device farm time separated.

## Explanation in Arabic

Pipeline 40 دقيقة؟ نقيس أولًا queue time، dependency download، Gradle configuration/tasks، JVM tests، emulator startup، instrumentation shards، upload. نطلع critical path لأن tasks parallel، مش نجمع كل CPU minutes. بعدين نصلح أكبر bottleneck: cache compatible، shard tests، reuse emulator، affected-module selection، أو تقليل flaky retries. نقارن p50/p95 بعد كل خطوة.

### Practical walkthrough in Egyptian Arabic

لو arm64 شغّال وABI تاني بيفشل، حدد الجهاز و`Build.SUPPORTED_ABIS` والstack/native load error، وافحص الـAAB/APK splits هل `.so` المطلوبة موجودة بنفس الاسم والـABI. راجع dependencies transitive والـvendor SDK support؛ ممكن ABI مدعومة في Gradle لكن مكتبة vendor نفسها مش متوفرة. اختبر install من Play-generated split أو bundletool، مش debug universal APK فقط. لا تضف `abiFilters` عشوائيًا فتخفي أجهزة من التوزيع.

## Why it matters and how it works

Build scans and CI traces show task duration/invalidation; Gradle configuration/build caches target distinct phases. Parallelism helps only if memory and shared devices permit it. CI queueing may dominate even when build tasks are fast.

## Worked example

If 40 minutes = 5 queue + 8 Gradle + 24 serial emulator tests + 3 publish, splitting device tests into four balanced shards may reduce wall time more than changing compiler flags. Verify each shard isolated and measure flake rate.

## Trade-offs and decision criteria

Caching can give fast warm runs but hide cold-start cost and stale-output risk. More shards use more infrastructure and may increase resource contention. Select changes based on measured savings and quality impact.

## Failure modes

Blindly enable Gradle parallel and double workers on memory-limited CI, causing OOM/retries and worse p95. Test with real CI constraints and preserve correctness/no-cache control runs.

## Production perspective

Dashboard tracks p50/p95 queue and each stage, cache hit rate, flake/retry minutes and defect escapes. A speed improvement that removes critical coverage is not accepted.

## Interview answer — short

“I profile the 40-minute critical path, separate queue/build/test time, then optimize the measured bottleneck and compare p50/p95 without weakening release coverage.”

## Interview answer — structured

“I collect CI timeline and Gradle build scans before changing settings. If emulator tests dominate, I shard or reduce setup; if configuration dominates, I evaluate configuration cache; if compilation dominates, I inspect processors and dependency invalidation. I include queue time and retry overhead. Each change is measured on cold and warm runs, and I keep security/payment gates even if they are slow.”

## Interview answer — deep senior

“I start with the exact release artifact, device ABI list and failure signature. A `UnsatisfiedLinkError` may indicate a missing `.so`, an ABI mismatch, a wrong JNI symbol or a transitive native dependency that was packaged only for arm64. I inspect the AAB and generated device splits, compare the vendor SDK’s supported ABIs, and reproduce on the affected hardware with the minified production variant. A debug universal APK can pass while a Play-delivered split lacks a dependency, so I test the distribution path. I check `abiFilters`, packaging exclusions and dependency versions, then confirm the native symbols and mapping needed to decode crashes. If the vendor does not support the ABI, I change device eligibility or feature availability deliberately rather than shipping a build that installs and crashes. The trade-off is package size and supported-device reach versus actual SDK compatibility. A staged rollout segmented by ABI gives the fix a safer exposure path.”

## How to answer in the interview

- **Why:** native support differs by device and artifact.
- **How:** inspect AAB splits, JNI symbols and vendor matrix.
- **Trade-off:** device reach versus reliable packaging.
- **Failure case:** debug universal APK hides missing split library.
- **Production solution:** test release delivery on affected ABI.

## Deep-dive talking points

Prompt for critical path, queue versus execution, p95, memory contention and correctness.

## Follow-up questions

- [CIC-12](../cic-12/): When use configuration cache? **Answer:** after scans show configuration cost and plugins are compatible.
- [TST-24](../tst-24/): How keep gates fast? **Answer:** prioritize signal and parallelize slow independent checks.

## Self-check rubric

Break the 40-minute run into setup, Gradle configuration, compilation, JVM, emulator and upload times; prioritize a measured critical-path change and retain release-risk coverage.

## References and reviewed-on date

- [Gradle performance guide](https://docs.gradle.org/current/userguide/performance.html) — profiling and caches.
- [Gradle build scans](https://docs.gradle.org/current/userguide/inspect.html) — build inspection.

Technically reviewed against the cited primary documentation on 2026-10-13; automated technical review only, not human review.
