---
id: "MEM-01"
question: "What is memory management in Android? What does garbage collection do?"
topic: "Memory Management, ANR & Performance"
code: "MEM"
group: "A"
phase: 1
priority: "P1"
order: 56
editorial_status: "reviewed"
---

# MEM-01

## Original interview question

What is memory management in Android? What does garbage collection do?

## What the interviewer evaluates

- Distinguish managed heap reclamation from process memory limits, native allocations, and resource cleanup.
- Explain reachability and GC cost without claiming developers can force a perfect collection.
- Connect allocation rate and retained objects to jank, OOM, and production measurement.

## Explanation in Arabic

Android Runtime (`ART`) يدير Java/Kotlin objects داخل managed heap. الـGC يتتبع الأشياء اللي لسه reachable من roots ويستعيد مساحة غير reachable. ده لا يعني إن أي حاجة كبيرة هتختفي فورًا: لو listener أو singleton ماسك Activity، تفضل reachable وده leak. كمان bitmap/native allocations وfile descriptors ومصادر أخرى محتاجة إدارة عمرها؛ GC مش بديل عن `close()` أو lifecycle cleanup. الذاكرة المحدودة وكثرة allocations يزودوا GC pressure ويعملوا jank أو `OutOfMemoryError`، فبنقيس retained heap وallocation rate والـPSS حسب المشكلة.

## Practical walkthrough

في feed صور، افتح واقفل الشاشة عشر مرات على نفس الجهاز وسجّل الـPSS والـJava heap والـnative/graphics قبل وبعد كل مرة. لو الذاكرة ارتفعت أثناء العرض ثم استقرت، ده غير إن كل Activity قديمة تفضل موجودة بعد الإغلاق. الـGC ممكن يشتغل بسبب ضغط التخصيص، لكنه مش تصريح إننا نهمل streams أو caches. دور على مالك الـreference ووقت انتهائه قبل تعديل حجم الـheap.

## Why it matters and how it works

ART allocates managed objects in a process heap and reclaims objects no longer reachable. Android can trim caches and kill less important processes under memory pressure; neither outcome is a contract that the current screen state survives. GC scheduling is runtime-controlled. High allocation rates can increase pauses or CPU work, while long-lived references keep an object graph alive. Native and graphics memory contribute to process footprint even when a Java heap chart looks modest.

## Worked example

A scrolling feed allocates a new full-size bitmap for each bind and retains old views in an observer. A profiler shows a growing retained Activity graph and rising native/graphics footprint. Remove the observer at the view lifecycle boundary, use an image loader with size-aware decoding, and retest memory after repeated navigation. This is a diagnostic example; no benchmark result is asserted.

## Trade-offs and decision criteria

Caching reduces repeated work but holds memory; set a bounded budget and trim on memory pressure. Pooling can reduce allocations in a hot path but adds ownership complexity and is rarely needed without measurement. Manual `System.gc()` is not a memory strategy. Prefer fixing retained references or oversized images over chasing a single GC pause in isolation.

## Failure modes

An Activity leak retains a whole UI tree despite GC. Frequent temporary allocations create GC churn and frame drops. A large bitmap or native buffer can cause OOM even if managed object count looks stable. Failing to close a cursor or stream consumes non-heap resources. Use heap dumps, Memory Profiler, system traces, and repeatable navigation to distinguish causes.

## Production perspective

Set representative low-memory device tests and track crash/OOM and frame metrics by release. Investigate a rising baseline after repeated open/close cycles, not only peak usage. Inspect Java heap, native/graphics categories, and PSS as appropriate. Keep image caches bounded and handle `onTrimMemory` signals without discarding critical unsaved user work.

## Interview answer — short

“ART manages Java/Kotlin heap objects and garbage collection reclaims unreachable ones. GC does not free objects still referenced or replace cleanup of native resources. I watch retention and allocation pressure because both affect memory and responsiveness.”

## Interview answer — structured

“Android processes have limited memory, and ART manages a heap for ordinary Java/Kotlin objects. GC traces reachability and reclaims unreachable objects, but timing is controlled by the runtime. A listener holding an Activity keeps it alive, while frequent allocations can increase GC work and jank. Native buffers, bitmaps, and open resources also matter. In practice I measure retained paths, allocation rate, and process footprint, then fix ownership or image sizing before adding cache or pooling complexity.”

## Interview answer — deep senior

“I separate memory management into reachability, allocation behavior, and total process footprint. ART's collector can reclaim managed objects that are no longer reachable from roots; it cannot reclaim a destroyed Activity still referenced by a singleton or callback. It also cannot substitute for closing files, cursors, or other owned resources. A rising retained baseline suggests a leak; a stable baseline with frequent spikes and collections suggests allocation pressure; native or graphics growth may not appear as a Java heap leak. I reproduce the user flow, inspect heap retaining paths and memory categories, and correlate GC and frame timing before changing code. The fix may be lifecycle cleanup, bounded caching, or correctly sampled image decode. I verify on constrained devices and monitor OOM and jank after release. For a feed regression, I run ten matched open-close cycles and record post-quiescence PSS, managed heap, native or graphics use, and retained screen counts. A rising high-water mark alone is inconclusive; I want a slope tied to a resource class. That experiment separates an intentional warm cache from an old Activity still reachable.”

## How to answer in the interview

- **Why:** Explain ART reachability and total process footprint.
- **How:** Measure a repeated screen journey by memory category and retained count.
- **Trade-off:** A cache may improve latency while raising steady-state memory.
- **Failure case:** GC cannot close owned resources or collect reachable obsolete screens.
- **Production solution:** Fix ownership and size budgets; rerun the same device trace.

## Deep-dive talking points

Discuss reachability, GC scheduling, retained graph, native memory, PSS, allocation churn, and bounded caches.

## Follow-up questions

- Will GC free an Activity after `onDestroy()`? **Answer:** only if no reachable reference still retains it; lifecycle termination alone does not guarantee collection.
- Why can an app OOM with an acceptable Java heap graph? **Answer:** native, graphics, and other process memory can be significant; inspect the full footprint.
- Should code call `System.gc()` to fix jank? **Answer:** no; address the allocation or retention pattern and measure the result.

## Self-check rubric

Explain reachability and collection, name two non-heap resources, distinguish churn from leak, and outline a measured fix.

## References and reviewed-on date

- [Overview of memory management](https://developer.android.com/topic/performance/memory-overview) — ART heap and collection behavior.
- [Manage your app's memory](https://developer.android.com/topic/performance/memory) — practical memory management.

Technically reviewed against these primary sources on 2026-10-13 by automated editorial review. The feed case is illustrative.
