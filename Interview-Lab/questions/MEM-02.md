---
id: "MEM-02"
question: "What are GC roots, and how does the GC determine reachability?"
topic: "Memory Management, ANR & Performance"
code: "MEM"
group: "A"
phase: 1
priority: "P1"
order: 57
editorial_status: "reviewed"
---

# MEM-02

## Original interview question

What are GC roots, and how does the GC determine reachability?

## What the interviewer evaluates

- Define roots and a path of strong references rather than saying “unused” means visually off screen.
- Explain why cycles can be collected but a retained Activity cannot.
- Use a heap dump's shortest path to a root to identify ownership mistakes.

## Concept and technical explanation

GC roots define the anchor nodes of the live object graph in tracing garbage collectors. In ART, an object is reachable if a direct or indirect chain of strong references connects it to at least one active GC Root. The runtime defines specific categories of GC roots: active thread stacks (local variables and method execution frames), static class fields, JNI global and local references, synchronized monitor locks, and system boot classes. ART evaluates reachability by traversing this directed reference graph. Objects that are part of isolated cyclic dependency islands but lack a path to any root are recognized as dead and eligible for reclamation.

## Practical walkthrough (English)

Tracing a reference chain from an active thread to a leaked Activity:
```text
[GC Root: Active Main Thread Looper]
       |
       v
[MessageQueue -> Pending Message (target: Handler, delay: 10s)]
       |
       v
[Anonymous Runnable instance]
       |
       v (implicit outer reference: this$0)
[Destroyed ProfileActivity instance]
```
Even if ProfileActivity.finish() has been executed and the window is removed from the screen, the active thread's Looper message queue retains the pending message, which holds the Runnable, which holds this$0. Because a path from a live GC Root exists, the GC cannot collect the activity or its associated view tree.

## Explanation in Arabic

ما هي الـ GC Roots وكيف يحدد مجمع النفايات إمكانية الوصول للكائنات (Reachability Analysis)؟

1. ما هو جذر تتبع القمامة (GC Root)؟
   - الـ GC Root هو كائن في الذاكرة يُعتبر **حياً بطبيعته ونقطة بداية موثوقة (Anchor of Liveness)** لا يمكن للـ GC حذفها.
   - أمثلة على الـ GC Roots:
     * **خيوط المعالجة النشطة (Active Threads):** أي كائن `Thread` يعمل حالياً في النظام، بما في ذلك الـ Main Thread وخيوط Coroutines.
     * **المتغيرات المحلية على الـ Stack (Stack Frames):** المتغيرات والمعاملات الموجودة داخل الدوال الجاري تنفيذها حالياً في أي Thread.
     * **المتغيرات الثابتة للكلاسات (Static Fields):** أي متغير `static` أو كائن `companion object` في كلاس محمل في الذاكرة.
     * **مراجع الـ JNI العامة (JNI Global References):** كائنات Java الممسوكة من كود C++ عبر `NewGlobalRef`.

2. كيف يحدد الـ GC إمكانية الوصول (Reachability)؟
   - يقوم الـ GC بعمل خوارزمية **Mark-and-Sweep**:
     * يبدأ من جميع الـ GC Roots ويتتبع كل المراجع (References) الخارجة منها كشجرة علاقات (Directed Graph).
     * أي كائن متصل بـ GC Root عبر سلسلة مراجع قوية (Strong Reference Chain) يُعتبر **Reachable (حي)** ويُترك في الذاكرة.
     * أي كائن غير متصل بأي GC Root يُعتبر **Unreachable (ميت)** ويتم مسحه وتحرير مساحته، حتى لو كانت هناك كائنات ميتة أخرى تشير إليه (Cyclic References)!

## Practical walkthrough

توضيح عملي للـ Reference Chains وكيف يحدث الـ Leak:
```text
[GC Root: Active Main Thread]
       |
       v
[Looper Message Queue]
       |
       v
[Pending Message: 10-second delay]
       |
       v (target)
[Anonymous Handler Runnable]
       |
       v (implicit outer reference)
[Old Destroyed MainActivity]  <--- LEAKED! لانها متصلة بـ GC Root!
```
طالما أن الـ Message معلقة في الـ MessageQueue، فالـ MainActivity تعتبر Reachable بالنسبة للـ GC ولن يستطيع مسحها من الذاكرة حتى ينتهي الـ 10 ثوانٍ.

## Why it matters and how it works

Tracing collectors start from runtime-defined roots and walk references. Reachability is about graph connectivity, not developer intent. Strong references keep targets alive; weak references can be cleared and are not a substitute for correct lifecycle ownership. The exact root set and GC algorithm vary by runtime, but the diagnostic model is stable: find why an object remains reachable from a long-lived owner.

## Worked example

After five profile-screen rotations, a heap dump contains five destroyed Activities. A path reads `static AnalyticsManager.instance -> callbacks -> ProfileActivity`. The callback was registered in `onStart()` without removal in `onStop()`. Unregister it symmetrically, repeat the rotation test, and compare retained Activities. This is an illustrative diagnostic path rather than a measured repository leak.

## Trade-offs and decision criteria

A weak reference may prevent one retention path but can hide an ownership problem or make callbacks disappear unpredictably. Explicit registration/unregistration is clearer for lifecycle-bound listeners. A process-wide cache can hold application-scope immutable data, but must not capture Activity or View references. Heap analysis identifies the actual path before changing cache design.

## Failure modes

Developers assume `onDestroy()` frees memory or that a reference cycle itself leaks. A coroutine launched in a long-lived scope captures a view binding. JNI global references can retain managed objects unexpectedly. Finalization is unreliable for timely resource release. Use a heap dump and retained-object detector, then reproduce to verify the path is gone.

## Production perspective

For a suspected screen leak, record a deterministic navigation loop, force a diagnostic GC only as part of profiling, capture a heap dump, and inspect retained instances and root paths. Fix the owner with a precise lifecycle boundary, then compare before and after on the same device profile. Monitor memory and OOM clusters after rollout.

## Interview answer — short

GC Roots are the foundational live anchors from which the garbage collector begins reachability tracing. They include active thread stacks, static variables, JNI global references, and system monitors. An object is considered reachable and kept alive only if a chain of strong references links it back to a GC Root. Isolated circular references disconnected from any root are automatically reclaimed.

## Interview answer — structured

Garbage collection in Android relies on tracing reachability rather than naive reference counting. GC Roots are the fundamental anchors that the runtime considers permanently alive during a collection pass.

These roots include local variables and parameters on active thread call stacks, static fields of loaded classes, JNI native references, and active thread objects themselves. The garbage collector traverses the object graph by following strong reference edges outward from these roots. If an object cannot be reached through any directed path, it is designated as eligible for reclamation.

In production, this graph-based approach easily handles cyclic references; two dead objects pointing to each other are collected without difficulty because neither connects back to a root.

Memory leaks occur when a short-lived component, such as an Activity, becomes unintentionally linked into a long-lived reference chain held by a persistent GC root like a background thread or a static manager.


## Interview answer — deep senior

When investigating memory leaks at an enterprise scale, staff engineers rely on graph theory algorithms embedded in heap dump parsers like LeakCanary's Shark engine and Eclipse Memory Analyzer Tool. During an HPROF heap dump analysis, the memory profiler constructs a dominator tree from the object reference graph. In this tree, node A dominates node B if every path from any GC Root to B must pass through A. This distinction between Shallow Heap—the memory consumed by the object itself—and Retained Heap—the memory that would be freed if that object were garbage collected—is crucial for identifying true leak root causes.

In Android, the most common retaining GC Roots are persistent thread workers like ThreadPoolExecutor workers or the Main Thread Looper. For example, an active thread stack frame executing a long network request keeps the executing Runnable alive as a GC Root. If that Runnable captures a lambda or inner class instance that references an Activity context, the entire retained dominator tree of that activity remains uncollected. To isolate the exact defect, profilers compute the Shortest Path to GC Roots excluding weak, soft, and phantom references. By identifying the specific field edge where ownership violated lifecycle boundaries, engineers can sever the link by clearing listeners in lifecycle callbacks or scoping workers to structured coroutine scopes.

## How to answer in the interview

- **Why:** Define roots and strong reachability.
- **How:** Trace the destroyed screen back to its owning registry.
- **Trade-off:** Weak references reduce retention but weaken delivery guarantees.
- **Failure case:** An uncleared static listener keeps an obsolete view tree alive.
- **Production solution:** Unregister at the matching lifecycle event and compare dumps.

## Deep-dive talking points

Discuss thread/static/JNI roots, strong paths, cycles, shortest retaining path, Fragment view lifetime, and weak-reference limits.

## Follow-up questions

- **Interviewer:** "Why are `SoftReference`s discouraged for image caching in Android?"
  **Answer:** "Because the runtime GC doesn't have sufficient heuristics on bitmap memory size vs overall system pressure, often evicting soft references either too aggressively or too late. An explicit `LruCache` with a fixed byte-budget in RAM is far more predictable."

- **Interviewer:** "What is a `PhantomReference`?"
  **Answer:** "A `PhantomReference` is enqueued after an object has been finalized and its memory is scheduled for reclamation, used primarily for low-level resource cleanup tracking."

- **Interviewer:** "Can an active coroutine be a GC Root?"
  **Answer:** "Yes. An active coroutine running on a dispatcher thread keeps its Continuation state machine reachable. If the coroutine captures an Activity reference in its closure and runs an infinite loop, that Activity is reachable from a GC Root and leaks indefinitely."

## Self-check rubric

Name roots, trace a listener-to-Activity path, explain cycle collection, and identify the ownership edge to remove.

## References and reviewed-on date

- [Overview of memory management](https://developer.android.com/topic/performance/memory-overview) — managed heap reachability.
- [JVMTI reachable objects](https://docs.oracle.com/en/java/javase/18/docs/specs/jvmti.html#iterate-over-reachable-objects) — root categories and graph traversal model.

Technically reviewed against primary documentation on 2026-10-13.
