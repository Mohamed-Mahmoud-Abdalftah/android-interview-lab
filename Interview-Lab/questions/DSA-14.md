---
id: "DSA-14"
question: "A product list freezes on low-end devices. How do you distinguish rendering bottlenecks from algorithmic complexity?"
topic: "Data Structures, Algorithms & Big O"
code: "DSA"
group: "C"
phase: 5
priority: "P2"
order: 453
editorial_status: "reviewed"
---

# DSA-14

## Original interview question

A product list freezes on low-end devices. How do you distinguish rendering bottlenecks from algorithmic complexity?

## What the interviewer evaluates

- Separating CPU algorithm, composition/binding, image, GC and GPU bottlenecks.
- Low-end-device evidence and scaling tests.

## Explanation in Arabic

Product list بتجمد على جهاز ضعيف؟ نجيب trace/frame metrics ونشوف: CPU في data transform أو `find` متكرر؟ Compose recomposition/bind؟ bitmap decode كبيرة؟ GC بسبب allocations؟ GPU overdraw؟ نجرب input sizes مختلفة: لو الوقت يقفز مع n² فغالبًا algorithm، لو مرتبط بصور/رسم فمسار rendering. ما نغيّرش architecture بالتخمين.

## Why it matters and how it works

Profilers and frame traces attribute main-thread work, rendering and allocations. Algorithmic complexity shows growth with input size and often CPU stacks in collection operations. Rendering bottlenecks can persist even when data preparation is precomputed.

## Worked example

Benchmark 100, 1k, 5k products with placeholders (no images) then real thumbnails. If placeholder run is fast but images freeze, inspect decode/caching; if both scale quadratically, inspect per-row joins and DiffUtil/Compose keys.

## Trade-offs and decision criteria

Paging limits visible data and memory but may mask an inefficient transform on each page. Moving work off main helps responsiveness but not total CPU/battery. Optimize the proven stage first.

## Failure modes

A profiler shows `prices.find` per row, but team blames Compose and rewrites UI. Or a HashMap refactor changes nothing because image decoding dominates. Require before/after metrics for the actual hypothesis.

## Production perspective

Production test uses representative low-end hardware, thermal state and real catalog shapes. Track frame time, dropped frames, allocations and memory, plus correctness of list ordering/data.

## Interview answer — short

“I profile the frame pipeline, vary input size and disable images temporarily to separate algorithmic work from rendering. Then I fix the measured bottleneck and verify on low-end devices.”

## Interview answer — structured

“I capture traces and frame metrics while scrolling a realistic list. I split time between data transforms, binding/recomposition, image decode, GC and GPU. Scaling input from hundreds to thousands can reveal an accidental quadratic join, while a constant freeze with heavy images points elsewhere. I use controlled experiments, then benchmark before/after rather than assume Compose itself is slow. Optimize the proven stage first.”

## Interview answer — deep senior

“My investigation has hypotheses and controls. I reproduce on a representative low-end device, record frame time distribution and CPU/allocation traces, and vary list size, image loading and update frequency independently. If transform cost grows superlinearly, I inspect hidden list scans and preindex once per snapshot. If rendering dominates, I inspect image size, keys, invalidations and layout work. Paging and background dispatch can reduce UI pressure, but I still fix pathological complexity and verify data correctness. I monitor production jank after rollout. Optimize the proven stage first.”

## Deep-dive talking points

Prompt for controlled experiments, scaling signature, profiler attribution, correctness after optimization.

## Follow-up questions

- [DSA-12](../dsa-12/): What code yields O(n²)? **Answer:** per-item linear lookup.
- [TST-17](../tst-17/): What measures frames? **Answer:** Macrobenchmark on release-like device setup.

## Self-check rubric

Can you derive the bound, explain the Android example, identify a trade-off/failure, and answer both follow-ups?

## References and reviewed-on date

- [Android rendering performance](https://developer.android.com/topic/performance/rendering) — frame pipeline.
- [Macrobenchmark overview](https://developer.android.com/topic/performance/benchmarking/macrobenchmark-overview) — device measurement.

Technically reviewed against the cited primary documentation on 2026-10-11; automated technical review only, not human review.
