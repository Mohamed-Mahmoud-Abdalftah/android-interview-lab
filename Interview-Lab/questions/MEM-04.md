---
id: "MEM-04"
question: "What is a memory leak, and how is it different from a large memory allocation?"
topic: "Memory Management, ANR & Performance"
code: "MEM"
group: "A"
phase: 1
priority: "P1"
order: 59
editorial_status: "reviewed"
---

# MEM-04

## Original interview question

What is a memory leak, and how is it different from a large memory allocation?

## What the interviewer evaluates

- Define a leak as unintended retention, not simply high memory or an OOM.
- Compare retained baseline after cleanup with bounded, intentionally large working sets.
- Describe a heap-dump experiment and corrective owner change.

## Explanation in Arabic

الـmemory leak يحصل لما object ما بقاش مطلوب لكن لسه reachable بسبب reference عمره أطول، مثل singleton ماسك Activity قديمة. الـlarge allocation ممكن تكون مقصودة ومؤقتة، زي decode لصورة كبيرة، وبرضه تسبب `OutOfMemoryError` لو تخطت الحدود، لكنها مش leak بالضرورة. الفرق يظهر بعد انتهاء العملية وتكرارها: هل baseline يرجع ولا retained objects تزيد؟ استخدم heap dump وretaining path لتعرف مين ماسك الحاجة. خفض حجم الصورة يحل allocation؛ إزالة listener أو تصحيح scope يحل leak.

## Why it matters and how it works

GC reclaims unreachable objects. A leaked object remains reachable through an unintended path, so repeated screen visits can accumulate old views and context references. A single oversized allocation may fail immediately despite no retained growth. Both affect memory pressure, and a large cache can be either legitimate or effectively unbounded retention depending on policy. Analyze retained size, peak allocation, and process memory categories separately.

## Worked example

A gallery opens a 40-megapixel image at full resolution and crashes once: sample down to the display target and inspect bitmap memory. A separate gallery keeps each closed Activity through a singleton callback and memory grows after every open/close: unregister the callback. Repeat identical navigation and compare retained Activity counts. These are illustrative cases, not measured app results.

## Trade-offs and decision criteria

Reducing peak image size can improve both memory and performance but may lower zoom quality; use tiled or sampled decoding for high-resolution zoom. A cache speeds repeat access but needs size bounds and trim policy. Weak references can avoid retention in limited cases, yet explicit lifecycle ownership is easier to reason about. Do not call every high heap snapshot a leak.

## Failure modes

One heap dump taken at peak load mislabels expected working memory as a leak. Ignoring native/graphics memory misses bitmap pressure. Conversely, relying only on OOM reports misses a growing Activity leak that causes slow GC and jank first. Compare snapshots after the same workload and cleanup boundary, and inspect paths to roots.

## Production perspective

Define a deterministic user journey and a baseline after quiescence. Measure peak and post-close retained memory over repeated cycles, correlate with low-memory device crashes, and isolate Java versus graphics/native categories. Fix the specific allocation or owner and repeat the same profile. Add a regression test or LeakCanary watch for a previously leaked screen where feasible.

## Interview answer — short

“A leak is an object retained after it should be released; a large allocation is memory intentionally requested for work. Either can cause pressure, but I diagnose them by retained growth versus peak usage.”

## Interview answer — structured

“An Activity kept alive by a singleton listener is a leak because GC still sees a root path. A full-resolution image decoded once is a large allocation; it may OOM even if it becomes unreachable afterward. I run a repeatable open/close loop and compare post-close retained instances and heap paths. For an allocation spike I size the work or stream it; for a leak I correct lifecycle ownership. Cache bounds and native bitmap memory must also be considered.”

## Interview answer — deep senior

“I use retention over time to distinguish the two. A leak is an unintended strong path from a GC root to data whose logical lifetime ended. Repeated navigation raises the retained baseline; a heap dump shows the owner, perhaps an observer in a singleton retaining a destroyed Activity. A large allocation can be valid yet exceed a device's available heap or graphics memory; its signature is a peak tied to one operation, possibly with a stable baseline afterward. I profile the same workload several times, inspect managed and native categories, and avoid interpreting a single high-memory sample as proof of a leak. The fix follows the cause: release the listener at the right lifecycle boundary, bound a cache, sample a bitmap, or use tiles for zoom. Then I reproduce on constrained devices and watch OOM and frame metrics.”

## Deep-dive talking points

Discuss retained baseline, peak allocation, GC root path, bitmap sampling, cache budget, and repeatable profiling.

## Follow-up questions

- Can a large allocation OOM without a leak? **Answer:** yes; one request can exceed available memory even if the result would later be collected.
- Why doesn't GC fix an Activity listener leak? **Answer:** the listener remains reachable and retains the Activity, so the collector cannot reclaim it.
- What measurement differentiates them? **Answer:** compare retained objects and post-cleanup baseline across repeated runs, alongside peak allocation and native memory.

## Self-check rubric

Define leak and peak allocation, give one example each, propose a measurement, and choose a cause-specific fix.

## References and reviewed-on date

- [Manage your app's memory](https://developer.android.com/topic/performance/memory) — memory pressure and investigation.
- [Overview of memory management](https://developer.android.com/topic/performance/memory-overview) — GC reachability.

Technically reviewed against these primary sources on 2026-10-11 by automated editorial review. The gallery cases are illustrative.
