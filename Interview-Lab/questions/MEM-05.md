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

## Concept and technical explanation

Memory Leak, OutOfMemoryError (OOM), Application Not Responding (ANR), and StackOverflowError represent four distinct failure modes in Android, each originating from different architectural subsystems. A memory leak is a logical defect where obsolete objects are kept reachable on the heap, silently driving up memory usage without an immediate crash. An OutOfMemoryError is a runtime error thrown when an allocation request cannot be satisfied after GC and heap compaction because the heap limit or address space is exhausted. An ANR is an operating system watchdog timeout triggered when the Main Thread Looper message queue is blocked for more than 5 seconds during user input dispatch. A StackOverflowError is a JVM/ART error caused by exhausting a thread's fixed execution stack, typically through infinite recursion or cyclic function invocations.

## Practical walkthrough (English)

Summary of failure mechanisms, locations, and triggers:
```text
Failure Type         Location      Underlying Cause                          Manifestation
-----------------------------------------------------------------------------------------------------
Memory Leak          Heap          Retained reference to obsolete object      Monotonically rising RAM
OutOfMemoryError     Heap/Native   Allocation request exceeds heap ceiling    App crash (Fatal Error)
ANR                  Main Thread   Looper message queue blocked (> 5s)        OS dialog / Process kill
StackOverflowError   Thread Stack  Call frame depth exceeds stack quota       App crash (Fatal Error)
```
While distinct, these defects can compound in production: a severe memory leak keeps thousands of objects alive on the heap; this causes ART's concurrent garbage collector to run repeatedly and thrash CPU cores, which delays message processing on the main thread and ultimately triggers a cascading ANR.

## Explanation in Arabic

المقارنة الشاملة بين كوارث أندرويد الأربعة: `Memory Leak` و `OutOfMemoryError` و `ANR` و `StackOverflowError`:

1. الـ Memory Leak (تسريب الذاكرة):
   - **السبب:** كائن لم يعد مطلوباً ولكنه محبوس في الـ Heap بسبب Strong Reference متصل بـ GC Root.
   - **الأثر:** لا يسبب كراش فوري؛ بل تراكم بطيء للذاكرة.

2. الـ OutOfMemoryError - OOM (نفاد الذاكرة):
   - **السبب:** التطبيق طلب حجز ذاكرة على الـ **Heap** (مثل Bitmap ضخم)، ولكن الـ Heap ممتلئ تماماً والـ GC عاجز عن توفير مساحة.
   - **الأثر:** Crash فوري وانهيار للتطبيق.

3. الـ ANR - Application Not Responding (تجميد التطبيق):
   - **السبب:** حظر الـ **Main (UI) Thread** لعدة ثوانٍ (عمليات حسابية ثقيلة، قراءة ديسك، أو Thread.sleep) مما يمنع معالجة أحداث اللمس ورسم الفريمات.
   - **الأثر:** لا يغلق التطبيق فوراً؛ يظهر للمستخدم نافذة من النظام تخبره بأن التطبيق لا يستجيب وتسأله هل يريد إغلاقه.

4. الـ StackOverflowError (فيضان الـ Stack):
   - **السبب:** امتلاء ذاكرة الـ **Stack** الخاصة بالـ Thread بسبب استدعاءات دوال متداخلة لا نهائية (Infinite Recursion).
   - **الأثر:** Crash فوري في كود التنفيذ.

## Practical walkthrough

جدول مقارنة حاسم وسريع:
| الكارثة | مكان الحدوث | السبب الجوهري | النتيجة الظاهرة |
| :--- | :--- | :--- | :--- |
| **Memory Leak** | Heap | كائن ميت ممسوك بـ Reference | استهلاك RAM متزايد تدريجياً |
| **OOM** | Heap | امتلاء الـ Heap وعدم كفاية الرام | Crash فوري بـ OutOfMemoryError |
| **ANR** | Main Thread | حظر الـ UI Thread لأكثر من 5 ثوانٍ | نافذة 'التطبيق لا يستجيب' |
| **StackOverflow** | Call Stack | استدعاء دالة متداخل لا نهائي | Crash فوري بـ StackOverflowError |

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

A memory leak is an uncollected dead object on the heap that raises steady-state memory. An OutOfMemoryError occurs when an allocation fails because the heap or native space is exhausted. An ANR is an OS watchdog timeout when the main thread looper is blocked for over five seconds. A StackOverflowError occurs when method call frames exceed a thread's stack capacity.

## Interview answer — structured

Understanding the boundaries between these four failure modes is essential for accurate production triage. A memory leak occurs on the heap when an object outlives its usefulness because a dangling reference prevents garbage collection, leading to silent memory bloat rather than an immediate crash. OutOfMemoryError is the fatal consequence when an allocation request exceeds the available process heap headroom after full collection attempts fail.

An Application Not Responding condition is not a memory exhaustion failure, but a thread responsiveness failure that occurs when the Main Thread Looper is blocked by heavy computation, disk I/O, or lock contention for more than five seconds.

StackOverflowError operates on thread stack memory, triggered when unbounded recursion exceeds the fixed stack quota allocated to an individual execution thread.

In production, these issues can intertwine; severe memory leaks force continuous garbage collection thrashing that consumes CPU cycles, slowing main thread message dispatch and triggering an indirect ANR.


## Interview answer — deep senior

Diagnosing these four failures requires completely different artifacts and investigative methodologies. For an ANR, the source of truth is the system traces.txt file in data anr or Google Play Console Android Vitals ANR report. We inspect the main thread state: if it is marked as BLOCKED or WAITING, we identify the monitor lock or IPC Binder transaction stalling message queue dispatch. We cross-reference this with CPU usage percentages to distinguish between CPU starvation caused by background worker threads and thread deadlock.

When investigating an OutOfMemoryError, we analyze the allocation stack trace in Crashlytics and examine the accompanying HPROF heap dump. We determine whether the OOM was caused by an acute single allocation, such as decoding an oversized bitmap, or by a chronic memory leak where thousands of leaked views and activities starved the heap over time. For a pure memory leak, LeakCanary provides automated dominator path analysis in debug builds, pointing directly to the leaking field reference. Finally, a StackOverflowError requires immediate inspection of the crashing thread's call frames; because the stack trace repeats a cyclic sequence of method calls, remediation involves refactoring recursive algorithms into iterative models utilizing explicit data structures like ArrayDeque or increasing tailrec recursion optimizations. By establishing strict diagnostic playbooks and correlating stack traces with heap dumps and kernel wait-channels, engineering teams resolve stability bottlenecks before releases reach general availability.

## How to answer in the interview

- **Why:** Name each failure by its direct mechanism.
- **How:** Choose heap, thread dump, or repeated lifecycle evidence.
- **Trade-off:** One regression can trigger several symptoms.
- **Failure case:** Treating an ANR as a heap leak misses a lock holder.
- **Production solution:** Fix the causal edge and watch cohort rates after release.

## Deep-dive talking points

Compare GC reachability and heap limit, large single allocations, thread-stack recursion, lock/Binder waits in ANRs, and evidence from heap dumps versus traces.

## Follow-up questions

- **Interviewer:** "Can a memory leak cause an ANR?"
  **Answer:** "Indirectly, yes! When memory leaks fill the heap near capacity, ART triggers continuous, aggressive garbage collection sweeps in a desperate attempt to free memory. These frequent GC pauses halt the main thread, leading to severe jank and eventually triggering an ANR."

- **Interviewer:** "Can an ANR happen if CPU usage is 0%?"
  **Answer:** "Yes. If the Main thread is blocked waiting on a lock held by a background thread (Deadlock) or waiting on a synchronous IPC call, CPU usage is 0% but the thread is blocked, triggering an ANR."

- **Interviewer:** "Does Kotlin's `tailrec` prevent `StackOverflowError`?"
  **Answer:** "Yes. When a recursive function is marked `tailrec`, the Kotlin compiler transforms the recursion into a standard iterative loop in bytecode, executing within a single stack frame and completely preventing stack overflow."

## Self-check rubric

Define all four failures; give a non-leak OOM example; choose one diagnostic artifact per failure; explain a leak-to-OOM causal path without equating them; and identify a misleading ANR assumption.

## References and reviewed-on date

- [Android memory overview](https://developer.android.com/topic/performance/memory-overview) — heap/GC and OOM behavior.
- [Diagnose and fix ANRs](https://developer.android.com/topic/performance/anrs/diagnose-and-fix-anrs) — responsiveness and trace analysis.

Technically reviewed against primary documentation on 2026-10-13.
