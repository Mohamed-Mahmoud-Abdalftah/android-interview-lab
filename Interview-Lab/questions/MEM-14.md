---
id: "MEM-14"
question: "How do you analyze a heap dump and use LeakCanary?"
topic: "Memory Management, ANR & Performance"
code: "MEM"
group: "B"
phase: 1
priority: "P1"
order: 69
editorial_status: "reviewed"
---

# MEM-14

## Original interview question

How do you analyze a heap dump and use LeakCanary?

## What the interviewer evaluates

- Reproduce a logical lifetime ending before capturing a heap dump.
- Interpret retained objects and paths to GC roots, not just shallow size.
- Understand LeakCanary's automated watch/dump/report flow and verify a fix.

## Explanation in Arabic

ابدأ بسيناريو يمكن تكراره: افتح الشاشة، اقفلها، وكرر. لو Activity أو Fragment view المفروض انتهت لكن لسه retained، خذ heap dump وافحص الـreference path من GC root إليها. المهم تعرف أي reference مخالف لعمر المالك، مش تختار أكبر object في القائمة عشوائيًا. `LeakCanary` يراقب objects اتدمرت باستخدام weak references، وبعد فترة لو لم تُجمع يحلل heap ويعرض leak trace. التقرير دليل تحقيق، مش إثبات قاطع وحده؛ ممكن يكون فيه مؤقتات أو references من أدوات debug. أصلح edge المحدد، أعد نفس السيناريو، وتأكد إن retention اختفت.

## Practical walkthrough

LeakCanary قال إن `ProfileActivity` اتدمرت لكنها لسه reachable من `AppEventBus.listeners`. متقفلش التقرير بالـignore: افتح leak trace، حدد أول edge مخالف للعمر، وشوف هل التسجيل بيتكرر من غير removal. بعد الإصلاح كرر rotation بنفس العدد واستنى إن held instances تختفي. heap dump لحظة واحدة ممكن يمسك object مؤقت؛ قارن بعد استقرار الشغل وما تعتمدش على أكبر retained size وحده.

## Why it matters and how it works

A heap dump captures managed object graph at a point in time. Retained size estimates the graph kept alive through an object; shallow size is only the object itself. A shortest strong-reference path to a root explains why an instance survives GC. LeakCanary watches destroyed Android owners, checks whether they remain retained, dumps and analyzes heap when warranted, then groups leak traces. Native memory growth may need other tools; a Java heap dump alone cannot explain every process-memory problem.

## Worked example

After three rotations, LeakCanary reports destroyed `ProfileActivity` retained through `AppEventBus.listeners -> ProfileActivity$callback`. Inspect the exact callback registration, remove the same instance at the intended lifecycle boundary, then repeat rotation and check retained count and heap path. Do not simply suppress LeakCanary's report. This path is an illustrative diagnostic example, not a finding in this repository.

## Trade-offs and decision criteria

LeakCanary is effective during development for owner leaks, while Android Studio Memory Profiler supports broader allocation and snapshot comparison. Heap dumping can pause an app and dumps may contain sensitive data; use appropriate debug/test handling. A one-time retained object may be legitimately pending cleanup, so repeat the scenario and examine its expected lifetime. If native bitmap memory dominates, use process and native profiling alongside the Java heap.

## Failure modes

Treating shallow size as total impact misses a small callback that retains a large view tree. Treating any reachable object as a leak ignores caches and active tasks. Assuming `onDestroy` immediately means GC must already have run causes false alarms. Editing the nearest line in a leak trace without understanding the owner can break legitimate event delivery. Verify both correctness and memory after the fix.

## Production perspective

Reproduce a field report on a representative device, capture a heap only in an authorized debug environment, identify the ownership edge, and add a regression path. Compare post-navigation retained objects and process memory before/after. For release telemetry, monitor OOM and memory symptoms without uploading raw heap dumps containing user data by default.

## Interview answer — short

“I reproduce a screen's expected destruction, inspect retained instances and their path to a GC root, fix the owner holding the reference, and repeat the same flow. LeakCanary automates watching and reporting likely leaks.”

## Interview answer — structured

“A heap dump is a snapshot of the managed object graph. I first reproduce a case where an Activity or Fragment view should be gone, then inspect retained instances and the strong-reference path from a GC root. A small listener object may retain a large view tree, so shallow size alone is misleading. LeakCanary watches destroyed owners with weak references, checks for retention, and analyzes a dump to show likely leak traces. I confirm the owner and lifetime before changing code, then repeat the same navigation and compare retention. Native memory issues need additional profiling.”

## Interview answer — deep senior

“The investigation begins with a repeatable lifetime boundary, for example close and reopen a screen several times. I capture a heap dump after the UI should be collectable, compare retained instance counts, and follow the shortest strong path to a GC root. I ask which reference edge violates ownership: a singleton listener, a Fragment holding an old view binding, a Handler Runnable, or a coroutine continuation. LeakCanary helps by automatically watching destroyed Android objects, checking whether weak references clear, and producing grouped leak traces. I do not treat one report as unquestionable; active operations, delayed cleanup, or instrumentation may explain temporary retention. Once I remove or rescope the offending reference, I rerun the identical flow, verify rendering and callbacks still work, and compare retained memory. I also inspect native and graphics categories if process memory rises but the Java heap is stable, and keep heap dumps private because they can contain user data. I would not suppress a leak trace merely because a collector has not run immediately; I check repeated counts after operations settle and whether the strong path remains. The report can include user data, so heap dumps stay in controlled storage. A regression check must confirm the listener still delivers after being resubscribed.”

## How to answer in the interview

- **Why:** Begin with a repeatable destroyed-object boundary.
- **How:** Read the strong path from root to retained instance.
- **Trade-off:** Weak or suppressed reports can conceal real lifetime bugs.
- **Failure case:** Temporary retention may look suspicious in one dump.
- **Production solution:** Fix the first invalid owner edge and rerun rotation checks.

## Deep-dive talking points

Discuss repeatable owner destruction, shallow versus retained size, root path, LeakCanary watch flow, false positives, and heap-data privacy.

## Follow-up questions

- What is a retaining path? **Answer:** the strong-reference chain from a GC root that keeps the target object reachable.
- Why isn't the largest shallow object necessarily the leak cause? **Answer:** a tiny callback can retain a much larger object graph through references.
- Can a Java heap dump diagnose every memory problem? **Answer:** no; native and graphics allocations may require additional process-level tools.

## Self-check rubric

Reproduce a lifetime boundary, inspect a root path, explain LeakCanary's flow, distinguish retained and shallow size, and verify the fix.

## References and reviewed-on date

- [Android Studio Memory Profiler](https://developer.android.com/studio/profile/memory-profiler) — heap inspection.
- [How LeakCanary works](https://square.github.io/leakcanary/fundamentals-how-leakcanary-works/) — watch, dump, and trace process.
- [Manage app memory](https://developer.android.com/topic/performance/memory/manage-app-memory) — broader memory categories.

Technically reviewed against these primary sources on 2026-10-13 by automated editorial review. No heap dump was captured for the illustrative case.
