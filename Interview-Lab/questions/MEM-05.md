---
id: "MEM-05"
question: "Compare memory leak, OutOfMemoryError, ANR, and StackOverflowError."
topic: "Memory Management, ANR & Performance"
code: "MEM"
group: "A"
phase: 1
priority: "P1"
order: 60
editorial_status: "reviewed"
---

# MEM-05

## Original interview question

Compare memory leak, OutOfMemoryError, ANR, and StackOverflowError.

## What the interviewer evaluates

- Separate reachability, allocation failure, responsiveness, and call-stack exhaustion.
- Pick evidence appropriate to each symptom instead of calling every freeze a leak.
- Explain that one defect can contribute to another without making the failure classes identical.

## Explanation in Arabic

الـmemory leak معناه object مبقاش له استخدام لكنه لسه reachable من GC root، زي singleton ماسك Activity قديمة؛ الاستهلاك يزيد مع الوقت. `OutOfMemoryError` بيحصل لما runtime ما يقدرش يوفّر مساحة لتخصيص جديد، وده ممكن يحصل من leak أو صورة ضخمة واحدة أو cache بلا حد. الـANR معناه التطبيق ما استجابش في المهلة المطلوبة؛ غالبًا Main thread محجوز بـI/O أو lock أو شغل CPU، حتى لو الذاكرة طبيعية. `StackOverflowError` غالبًا من recursion عميق أو غير منتهٍ استهلك stack بتاع thread. الأربعة أعراض مختلفة؛ شخّص بالدليل قبل ما تصلح.

## Why it matters and how it works

Garbage collection reclaims unreachable heap objects. A leak keeps obsolete objects reachable, while an OOM is failure of a new allocation under a memory limit and may have no leak at all. ANR is an app responsiveness timeout; inspect the main thread and blockers, including Binder calls or locks. Stack overflow consumes a thread's call stack, not the Java heap capacity in the same way. A leak may increase GC pressure and contribute to jank/OOM, but an ANR can occur with plenty of free heap.

## Worked example

After every rotation, a process singleton retains the previous Activity through a callback. Heap dumps show multiple destroyed Activities reachable from that singleton: a leak. Separately, decoding a full-resolution camera image may fail allocation immediately: OOM without a leak. A synchronous database migration on Main can produce an ANR. Infinite recursive tree traversal can produce StackOverflowError. Differentiate with heap-retention paths, allocation traces, ANR thread dump/Perfetto, and exception stack respectively.

## Trade-offs and decision criteria

Fix a leak by breaking the unintended reference and matching owner lifetimes; increasing heap size merely postpones failure. Fix a large-allocation OOM by sampling, streaming, or bounding caches, but avoid indiscriminately shrinking images needed for quality. Fix ANR by removing blocking work/lock contention from Main and measuring traces. Fix stack overflow by correcting recursion termination or using an explicit stack when depth is unbounded.

## Failure modes

Seeing high memory and declaring a leak without checking whether objects are still intentionally cached wastes time. Catching `OutOfMemoryError` and continuing may leave the app unstable. Moving a lock holder to another thread does not help if Main still waits on it. Treating StackOverflowError as a heap-size problem misses the recursive call chain. Capture reproducible evidence, not only an aggregate crash count.

## Production perspective

For a media feed with crashes and freezes, segment reports by OOM stack, ANR cluster, and heap growth. Record image dimensions and cache occupancy without private content; inspect heap dumps for retained Activities; inspect main-thread traces for decode or locks. Add a bounded image pipeline and lifecycle cleanup, then measure memory percentiles, ANR rate, and crash rate separately after rollout.

## Interview answer — short

“A leak is unwanted reachable heap memory; OOM is an allocation failure; ANR is a responsiveness timeout; StackOverflowError is call-stack exhaustion. A leak can cause OOM or jank, but these are different diagnoses and need different evidence.”

## Interview answer — structured

“I look at the failing resource. A leak keeps unused objects alive through GC roots, so I inspect a heap dump and reference path. An OOM can come from that leak or one oversized allocation, so I inspect allocation and cache behavior. An ANR means the app missed a responsiveness deadline, often because Main is blocked; I inspect thread traces and Perfetto. A StackOverflowError points to a deep or runaway call chain. I would not label an ANR as a memory leak without evidence.”

## Interview answer — deep senior

“These failures have different causal mechanisms and telemetry. For a leak, I compare retained-object populations over repeated lifecycle transitions and trace GC roots. For OOM, I examine the attempted allocation, heap limit, image size, cache policy, and whether leak pressure contributed. For ANR, I inspect the main-thread state and the thread or Binder target it waits on; the apparent top frame can be misleading if the trace was captured late. For StackOverflowError, I inspect recursion depth and cycle detection. In production I cluster each symptom separately, form a reproducible hypothesis, make a targeted fix, and verify the corresponding memory, crash, or responsiveness metric.”

## Deep-dive talking points

Compare GC reachability and heap limit, large single allocations, thread-stack recursion, lock/Binder waits in ANRs, and evidence from heap dumps versus traces.

## Follow-up questions

- [MEM-04](../mem-04/): Can an OOM happen without a leak? **Answer:** yes; a single bitmap or unbounded but still-used cache can exceed the heap.
- [MEM-10](../mem-10/): Can an ANR happen with free memory? **Answer:** yes; Main can be blocked by I/O, a lock, or a slow Binder call.
- [MEM-14](../mem-14/): What proves an Activity leak? **Answer:** a heap path from a GC root to a destroyed Activity that should no longer be retained.

## Self-check rubric

Define all four failures; give a non-leak OOM example; choose one diagnostic artifact per failure; explain a leak-to-OOM causal path without equating them; and identify a misleading ANR assumption.

## References and reviewed-on date

- [Android memory overview](https://developer.android.com/topic/performance/memory-overview) — heap/GC and OOM behavior.
- [Diagnose and fix ANRs](https://developer.android.com/topic/performance/anrs/diagnose-and-fix-anrs) — responsiveness and trace analysis.

Technically reviewed against these primary sources on 2026-10-11 by automated editorial review. Examples are diagnostic scenarios, not device experiments.
