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

GC Roots are objects always deemed alive (active threads, local stack variables, static fields, JNI global handles). The GC traverses outgoing strong references forming a directed graph; objects reachable from any GC Root are retained, while unreachable objects are reclaimed.

## Interview answer — structured

Garbage collection in Android determines an object's liveness through **Reachability Analysis** originating from **GC Roots**:

A **GC Root** is an anchor object that is fundamentally alive and cannot be collected:

1. **Active Threads**: The Main UI thread and any running worker thread or coroutine thread pool.
2. **Thread Stack Frames**: Local variables and parameters currently residing on active function call stacks.
3. **Static Fields**: Variables owned by loaded classes or Kotlin companion objects/singletons.
4. **JNI References**: Global C/C++ native pointers created via `NewGlobalRef`.

During a collection cycle, the GC traces outward from all GC Roots across object reference pointers in a directed graph. If an object has a valid path of strong references connecting it to at least one GC Root, it is **Reachable** and preserved. If no path exists, it is **Unreachable** and its memory is reclaimed.

## Interview answer — deep senior

A vital senior distinction is understanding how tracing garbage collection handles **Cyclic References** compared to naive reference counting:

If Object A references Object B, and Object B references Object A, but neither A nor B is reachable from any GC Root, ART's reachability graph correctly identifies both as unreachable garbage and collects both simultaneously. Cycles of unreachable objects do not cause memory leaks in Android.

The type of reference pointer also modifies reachability:

- **Strong Reference**: Default reference. Prevents collection completely as long as reachable from a GC Root.
- **Soft Reference (`SoftReference`)**: Retained until memory pressure becomes critical before throwing an OOM. (Discouraged for caches in modern Android in favor of explicit `LruCache`).
- **Weak Reference (`WeakReference`)**: Does not protect the target from collection. Reclaimed immediately in the next GC cycle if no strong references exist.

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
