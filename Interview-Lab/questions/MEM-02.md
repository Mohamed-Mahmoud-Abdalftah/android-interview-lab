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

`GC roots` هي نقاط يبدأ منها الـcollector تتبع الـobject graph، زي references من thread stacks وstatic fields وبعض VM/JNI roots. أي object له strong-reference path من root يظل reachable، حتى لو الشاشة المقابلة اتقفلت. لو `singleton` ماسك listener والـlistener ماسك Activity، الـActivity وكل شجرتها ممكن تفضل في الذاكرة. بالمقابل دائرتين ماسكين بعض لكن مفيش طريق من root ليهم يمكن جمعهم؛ مجرد circular reference مش leak وحده. في heap dump ندور على retaining path للـActivity أو bitmap ونصلح المالك اللي طول عمره أكبر من اللازم.

## Practical walkthrough

لو heap dump بيقول خمس نسخ من `ProfileActivity` بعد خمس rotations، امشِ من كل نسخة لحد root: static manager، callback، وبعدين Activity. المشكلة مش إن GC تأخر ثانية؛ المشكلة إن manager لسه محتفظ بالـcallback. شيل التسجيل من نفس lifecycle boundary ورجّع السيناريو. لو الدائرة الداخلية منفصلة عن كل roots فدي مش leak في tracing GC حتى لو objects ماسكة بعض.

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

“GC roots are starting references such as thread stacks and static fields. The collector traces strong-reference paths from them; an object with no reachable path can be reclaimed, even if it participates in a cycle.”

## Interview answer — structured

“I model memory as an object graph. The collector starts at runtime roots and follows references. A destroyed Activity can still be reachable through a singleton callback, so GC cannot reclaim it. Two objects referring only to each other are collectable if the pair has no root path. In a heap dump I look for a retained object's path to a root, identify which owner lived too long, and fix registration, cancellation, or reference ownership rather than adding a random weak reference.”

## Interview answer — deep senior

“Reachability gives a concrete way to investigate leaks. Roots include live thread stack references, static state, and runtime or JNI-held references. The collector walks the strong-reference graph; lifecycle callbacks do not change this graph unless my code releases references. If a Fragment view is retained by an observer in a longer-lived scope, the view tree remains reachable even after `onDestroyView`. I capture a heap dump after a repeatable screen-close cycle and inspect the shortest retaining path to a root. Then I decide which edge violates intended ownership—perhaps a singleton listener, an unbounded coroutine, or a native global—and remove it at the right boundary. I verify retained instance counts after the fix. Weak references can be useful in specific cache designs, but they do not replace explicit lifecycle cleanup. For five rotations, I expect at most the current screen to remain once old work settles. A static registry-to-listener-to-Activity path names the edge to remove; a large object without such a path is not enough. I also check JNI globals when managed code cannot explain the root.”

## How to answer in the interview

- **Why:** Define roots and strong reachability.
- **How:** Trace the destroyed screen back to its owning registry.
- **Trade-off:** Weak references reduce retention but weaken delivery guarantees.
- **Failure case:** An uncleared static listener keeps an obsolete view tree alive.
- **Production solution:** Unregister at the matching lifecycle event and compare dumps.

## Deep-dive talking points

Discuss thread/static/JNI roots, strong paths, cycles, shortest retaining path, Fragment view lifetime, and weak-reference limits.

## Follow-up questions

- Does a reference cycle always leak? **Answer:** no; a tracing collector can reclaim the whole cycle if nothing from a root reaches it.
- Can a destroyed Activity remain alive? **Answer:** yes, if a reachable listener, coroutine, or static field retains it.
- What does a heap retaining path tell you? **Answer:** the chain of references to a root that explains why the object has not been collected.

## Self-check rubric

Name roots, trace a listener-to-Activity path, explain cycle collection, and identify the ownership edge to remove.

## References and reviewed-on date

- [Overview of memory management](https://developer.android.com/topic/performance/memory-overview) — managed heap reachability.
- [JVMTI reachable objects](https://docs.oracle.com/en/java/javase/18/docs/specs/jvmti.html#iterate-over-reachable-objects) — root categories and graph traversal model.

Technically reviewed against these primary sources on 2026-10-13 by automated editorial review. The heap path is illustrative.
