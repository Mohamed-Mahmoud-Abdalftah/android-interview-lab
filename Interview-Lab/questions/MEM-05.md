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

A Memory Leak is an unintended object retention in the Heap; an OutOfMemoryError is a Heap exhaustion crash; an ANR is a Main Thread freeze (>5s) blocking user input; and a StackOverflowError is a Thread call stack exhaustion crash caused by infinite recursion.

## Interview answer — structured

These four system failure modes represent fundamentally different failure domains across memory and threading architecture.

First, a Memory Leak is an architectural retention defect where unreachable heap objects are retained by active GC Roots. It does not crash immediately, but progressively inflates the heap baseline. Next, an OutOfMemoryError (OOM) is a runtime fatal error thrown when the application requests heap allocation (e.g. Allocating a bitmap) and the ART garbage collector cannot reclaim sufficient contiguous memory despite garbage collection.
Additionally, an ANR (Application Not Responding) is a threading and responsiveness defect caused by blocking the **Main UI Thread** for longer than 5 seconds (preventing touch input dispatch) or 10-20 seconds in services and broadcast receivers. It prompts a system dialog offering the user to force-close the app. Finally, a StackOverflowError is a thread call stack failure thrown when the LIFO execution stack exceeds its physical frame budget (typically 1MB), almost universally caused by infinite or excessively deep recursive method calls.


## Interview answer — deep senior

In Android production diagnostics, each failure triggers different tracing artifacts.

First, with OOM, captured in Crashlytics with stack traces originating at allocation sites (e.g., `BitmapFactory.nativeDecodeStream` or `ByteArrayOutputStream.toByteArray()`). Resolving it requires analyzing heap dumps (`.hprof`) via LeakCanary or Memory Profiler. Next, with ANR, captured in the Android OS system dump `/data/anr/traces.txt`. The trace reveals what state the Main thread was in (e.g., `BLOCKED` on a database lock or executing a synchronous network read). It is resolved by offloading the blocked work to `withContext(Dispatchers.IO)`.
Finally, with StackOverflowError, manifests with hundreds of repeated lines of the same method in Crashlytics. It is resolved by applying tail recursion (`tailrec`) or converting recursive algorithms into iterative loops with explicit queue/stack data structures.


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
