---
id: "MEM-17"
question: "What is UI jank? Explain frame timing, recompositions, and excessive work on Main."
topic: "Memory Management, ANR & Performance"
code: "MEM"
group: "B"
phase: 1
priority: "P1"
order: 72
editorial_status: "reviewed"
---

# MEM-17

## Original interview question

What is UI jank? Explain frame timing, recompositions, and excessive work on Main.

## What the interviewer evaluates

- Define jank as missed frame deadlines and avoid a universal 16 ms assumption for all refresh rates.
- Distinguish recomposition count from actual costly composition, layout, draw, and main-thread blocking.
- Use traces and frame metrics to find a specific bottleneck before optimizing.

## Explanation in Arabic

الـjank يظهر لما frame يتأخر عن deadline المناسب لتردد الشاشة، فيحس المستخدم بتقطيع. عند 60Hz الميزانية حوالي 16.7ms، وعند 120Hz حوالي 8.3ms، لكن الـpipeline فيها عمل UI وRenderThread/GPU، فلا تختزل المشكلة في رقم واحد لكل جهاز. في Compose، تغيير state قد يسبب recomposition لأجزاء محتاجة التحديث؛ مش كل composable بالضرورة تعاد، والعدد وحده لا يساوي بطء. المشكلة لما عمل ثقيل، query، decode، list sorting أو layout متكرر يحصل على Main أو في مسار frame. خذ trace لسيناريو محدد وشوف أي phase تأخر.

## Practical walkthrough

على 120Hz الـframe interval حوالي 8.3ms، لكن في UI pipeline شغل Main وRenderThread وGPU، فمتقولش إن كل composable لازم يخلص في 8.3ms لوحده. في cart screen، sorting آلاف المنتجات داخل composition بعد كل حرف يعمل long Main slices. خذ Frame Timeline، شوف أي frames اتأخرت وليه، وانقل الحساب لطبقة state أو cache محسوب. بعد التعديل قارن tail frame time على نفس الجهاز والرحلة.

## Why it matters and how it works

The display refresh cadence sets frame deadlines. Main-thread event handling, composition or View traversal, layout, draw, RenderThread, and GPU work all contribute to what appears on screen. Compose can skip unaffected groups during recomposition; unstable inputs or expensive calculations inside composables may increase work. A background coroutine does not guarantee main safety if heavy code before suspension still runs on Main. Frame timing and system traces identify where the actual delay occurs.

## Worked example

A cart total recalculates by sorting thousands of items inside a composable whenever a text field changes. Frame trace shows long Main slices during typing. Move the computation into a ViewModel on an appropriate dispatcher, expose a stable UI state, and avoid invalidating unrelated rows. Compare frame percentiles and recomposition traces before and after on the same device. This is an illustrative diagnosis, not a measured benchmark.

## Trade-offs and decision criteria

Memoization can avoid repeated pure computation but adds invalidation complexity; first measure if it is costly. `derivedStateOf` is useful for specific rapidly changing derived UI state, not a blanket fix. Moving work off Main improves responsiveness but needs cancellation and thread-safe state updates. GPU-heavy effects require different profiling than a main-thread database call. Optimize user-visible frame tails rather than only average time.

## Failure modes

An image decode on Main blocks input and drawing. A shared mutable model emits whole-list changes that trigger excessive layout. A blocking binder call or lock wait stalls Main despite low CPU usage. Treating every recomposition as a bug drives unnecessary complexity; use Compose tracing and frame metrics to identify expensive work. Test with production-sized lists and high-refresh devices.

## Production perspective

Define scroll and interaction journeys, measure slow/frozen frame metrics by device class, capture Perfetto on a representative device, and mark app operations. Fix the dominant phase, replay identical data, and monitor staged rollout rendering metrics. Keep correctness: a faster screen that shows stale totals or misses state updates is not a successful optimization.

## Interview answer — short

“Jank is visible frame delay when rendering misses a display deadline. I inspect frame traces to find whether Main work, recomposition/layout, RenderThread, or GPU is responsible, then fix the measured bottleneck.”

## Interview answer — structured

“A frame must be ready for the display's refresh cadence, so the time budget varies by device. Main-thread blocking, repeated expensive composition or layout, and GPU work can all produce jank. In Compose, a state change may recompose affected groups, but that does not mean every composable re-executes or that each recomposition is bad. I capture a trace and frame metrics for a repeatable interaction, inspect which phase misses the deadline, and move heavy calculations or I/O out of the frame path. I compare tail frame times after the change and check UI correctness.”

## Interview answer — deep senior

“I define jank as a missed frame deadline perceived during a real interaction, not as an arbitrary count of recompositions. At 60 Hz the interval is about 16.7 ms and at 120 Hz about 8.3 ms, but work crosses Main, RenderThread, and GPU, so the trace matters. For a slow list I capture a representative scroll with production-sized data, inspect frame timeline and Main slices, and use Compose tracing to see whether invalidation caused expensive composition, layout, or draw. Compose can skip unaffected work; I would not rewrite the state graph solely because a counter increased. I look for image decode, sorting, database I/O, binder waits, and lock contention on Main. A coroutine launch without dispatcher change may still execute CPU work there. Once I isolate the expensive phase, I move or reduce that work, preserve cancellation and state consistency, and compare slow-frame percentiles and correctness before rolling out. For a cart search that sorts thousands of items on each keystroke, I compare frame-tail timing while typing and inspect whether the sort runs during composition. Memoization can lower CPU cost but retain another large list, so I check memory too. Stable state boundaries should reduce the affected UI work without changing product ordering.”

## How to answer in the interview

- **Why:** Define jank by missed presentation deadlines.
- **How:** Trace frame timeline and Main computation.
- **Trade-off:** Memoization trades CPU for retained memory.
- **Failure case:** Counting recompositions alone misdiagnoses jank.
- **Production solution:** Move heavy transforms and compare frame-tail distribution.

## Deep-dive talking points

Discuss refresh-rate-dependent deadlines, Main versus RenderThread/GPU, Compose skipping, expensive state derivation, and tail frame metrics.

## Follow-up questions

- Does every recomposition mean a whole Compose screen reruns? **Answer:** no; Compose can skip unaffected groups based on state reads and stability.
- Can jank occur with low Main CPU? **Answer:** yes; Main may be waiting on a lock, binder call, or I/O, or GPU/RenderThread may be the bottleneck.
- Why isn't 16 ms a universal frame budget? **Answer:** displays have different refresh rates and the frame pipeline consumes time in multiple phases.

## Self-check rubric

Define a missed frame, describe two pipeline causes, explain Compose recomposition limits, and plan a traced before/after test.

## References and reviewed-on date

- [Measure app performance](https://developer.android.com/topic/performance/measuring-performance) — frame timing and Compose tracing.
- [System tracing overview](https://developer.android.com/topic/performance/tracing) — device-wide timing.
- [Compose performance](https://developer.android.com/develop/ui/compose/performance) — recomposition and UI optimization.

Technically reviewed against these primary sources on 2026-10-13 by automated editorial review. The cart example was not device-benchmarked.
