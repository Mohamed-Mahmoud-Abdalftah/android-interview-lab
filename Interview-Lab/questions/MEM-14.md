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

## Concept and technical explanation

Memory leaks occur when an object that is no longer needed by application logic remains reachable through a chain of strong references originating from a Garbage Collection Root (GC Root). In Android, the most damaging memory leaks involve Context, Activity, and View hierarchies because retaining a single Activity retains its entire view hierarchy, loaded bitmaps, and window-bound allocations. A heap dump is a binary snapshot of all objects, reference pointers, and primitive fields residing in the Java/Kotlin runtime heap at an exact moment in time, formatted according to the HPROF specification. Analyzing a heap dump entails reconstructing the directed object graph, distinguishing shallow size (the memory footprint of the instance itself) from retained size (the aggregate memory reclaimed if this instance and its exclusively owned subtree are collected), and computing the dominator tree. LeakCanary is an automated memory leak detection library tailored for Android debug builds. It operates by observing the destruction lifecycle of Activities, Fragments, and ViewModels. When an Android component reaches its terminal lifecycle state (`onDestroy`), LeakCanary wraps the target instance in a `KeyedWeakReference` tied to a `ReferenceQueue`. If the weak reference is not enqueued within a 5-second watch threshold, LeakCanary triggers a GC cycle. If the object remains retained, LeakCanary triggers a background heap dump using `Debug.dumpHprofData()` and parses the snapshot using Shark, its headless Kotlin-based HPROF analyzer, to identify the shortest strongly reachable path from a GC Root to the leaking instance.

## Practical walkthrough (English)

LeakCanary integration and leak trace interpretation:
```kotlin
// 1. Add LeakCanary dependency in build.gradle.kts (runs automatically in debug builds only):
dependencies {
    debugImplementation("com.squareup.leakcanary:leakcanary-android:2.14")
}

// 2. Typical LeakCanary leak trace report:
/*
┬───
│ GC Root: System class / Static field
│
├─ com.example.app.UserManager class
│    Leaking: NO (Static class is never leaking)
│    ↓ static UserManager.currentContext
├─ com.example.app.DetailActivity instance
│    Leaking: YES (Activity has been destroyed: onDestroy() called)
│    Retaining: 24.3 MB across 1,420 objects
╰→ com.example.app.DetailActivity
*/
```
When examining the leak trace, developers look at the boundary where `Leaking: NO` changes to `Leaking: YES`. That exact edge highlights the developer defect: a static field retaining an Activity Context. The remediation requires either clearing the reference inside `onDestroy()`, or decoupling the dependency by passing `applicationContext` instead of the Activity instance.

## Explanation in Arabic

كيفية تحليل الـ Heap Dump واستخدام أداة LeakCanary لاكتشاف تسريبات الذاكرة في بيئة الإنتاج والتطوير:

1. ما هو الـ Heap Dump؟
   - الـ Heap Dump هو لقطة ثنائية (Binary Snapshot بتنسيق HPROF) تحتوي على جميع الكائنات، والمصفوفات، والمراجع، والـ Primitive Fields الحية داخل ذاكرة الـ Heap في لحظة التقاطها.
   - يمكن استخراجه يدوياً عبر Android Studio Profiler (زر Dump Java Heap) أو برمجياً عبر `Debug.dumpHprofData()`.

2. كيف تعمل أداة LeakCanary؟
   - تراقب دورات حياة الـ Activities والـ Fragments والـ ViewModels والـ Root Views تلقائياً عبر `ActivityLifecycleCallbacks` و `FragmentLifecycleCallbacks`.
   - عند تدمير النشاط (`onDestroy()`)، تضع مرجع النشاط داخل `KeyedWeakReference` وتنتظر 5 ثوانٍ.
   - إذا ظل الكائن موجوداً بعد 5 ثوانٍ، تُجبر الـ GC على العمل للتحقق.
   - إذا ظل الكائن حياً، تعلن LeakCanary أن الكائن **مُحتجز (Retained)**، وتقوم بتوليد HPROF dump وتحليله في خلفية التطبيق باستخدام محرك **Shark** (محلل HPROF كوتلن فائق السرعة).

3. قراءة سلسلة التسريب (Leak Trace / Retained Path):
   - يبدأ التقرير من **GC Root** (مثل Thread نشط، أو Static Variable، أو Native Global Ref).
   - يوضح مسار الإشارات (References) وصولاً إلى الـ Leaked Object.
   - يبين الـ Leak Trace بدقة أي مرجع يُشتبه في أنه السبب (مُحدد بـ `Leaking: YES` مقابل `Leaking: NO`).

## Practical walkthrough

تثبيت وقراءة مخرجات LeakCanary وتحليل Heap Dump في Android Studio:
```kotlin
// 1. إضافة LeakCanary في build.gradle.kts (تعمل تلقائياً في debug فقط دون كود إضافي):
dependencies {
    debugImplementation("com.squareup.leakcanary:leakcanary-android:2.14")
}

// 2. نموذج للـ Leak Trace الناتج عن تحليل LeakCanary:
/*
┬───
│ GC Root: System class / Static field
│
├─ com.example.app.UserManager class
│    Leaking: NO (Static class is never leaking)
│    ↓ static UserManager.currentContext
├─ com.example.app.DetailActivity instance
│    Leaking: YES (Activity has been destroyed: onDestroy() called)
│    Retaining: 24.3 MB across 1,420 objects
╰→ com.example.app.DetailActivity
*/
```

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

Analyzing a heap dump requires inspecting the shortest path of strong references from a GC Root to an instance that has outlived its logical lifecycle. In development, LeakCanary automates this by wrapping destroyed Activities, Fragments, and ViewModels in weak references, waiting five seconds, triggering garbage collection, dumping the HPROF heap, and computing the retained reference chain with its Shark analyzer.

## Interview answer — structured

Memory leak diagnosis centers on isolating objects that survive their terminal lifecycle events due to unintentional retention by a Garbage Collection Root.

LeakCanary streamlines this discovery process in debug builds by hooking into application lifecycle callbacks. When an Activity or Fragment invokes its destruction callback, LeakCanary registers the instance inside an ObjectWatcher using a KeyedWeakReference bound to a ReferenceQueue. If the instance is not reclaimed after a five-second grace period, LeakCanary requests runtime garbage collection. Upon confirming retention, it generates an HPROF heap dump and utilizes the Shark engine to compute the shortest strong reference path.

In production, we inspect the resulting leak trace by locating the transition point where an upstream node is marked Leaking NO while the downstream node is marked Leaking YES. That exact reference edge pinpoints the defect, such as an uncancelled coroutine job, a dangling static reference, or an uncleared listener.

Once the culprit reference is nullified or tied to a proper lifecycle scope, we verify the resolution by repeating the user navigation sequence and validating zero retained instances.


## Interview answer — deep senior

At the Android Runtime level, ART manages object reclamation through generational concurrent copying and concurrent mark-sweep garbage collection algorithms. When an instance is allocated, it is tracked in the managed heap; once unreachable, weak references linked to reference queues are enqueued during finalization. LeakCanary leverages this exact low-level runtime contract. It wraps target objects in KeyedWeakReference instances. When ART performs garbage collection, instances lacking strong paths are moved to the queue. If an object remains unenqueued after five seconds and an explicit runtime GC request, LeakCanary confirms a true leak.
Dumping the heap invokes Debug.dumpHprofData, which pauses application threads via a brief stop-the-world synchronization phase while ART writes the memory snapshot to disk. In production systems, taking full HPROF dumps is forbidden because the pause duration degrades user experience, frequently tripping the system Watchdog and provoking an ANR. Furthermore, raw HPROF dumps expose sensitive user data, including security tokens and personal credentials resident in memory buffers.
To profile memory without client-side pauses, staff engineers rely on Android Studio Profiler, Eclipse Memory Analyzer Tool, or headless Shark analyzers running on secondary processes. Within MAT, we analyze the Dominator Tree, where an object dominates another if all reference paths to the child must pass through the parent. By sorting by Retained Heap rather than Shallow Heap, we immediately expose root owners holding tens of megabytes of nested view hierarchies.
When tracking production memory regressions across large fleets, we collect stripped leak signatures and aggregated telemetry through WorkManager workers. We monitor native memory growth, graphics allocations, and process RSS via proc status and dumpsys meminfo, ensuring that regressions are flagged before triggering low-memory killer terminations.

## How to answer in the interview

- **Why:** Begin with a repeatable destroyed-object boundary.
- **How:** Read the strong path from root to retained instance.
- **Trade-off:** Weak or suppressed reports can conceal real lifetime bugs.
- **Failure case:** Temporary retention may look suspicious in one dump.
- **Production solution:** Fix the first invalid owner edge and rerun rotation checks.

## Deep-dive talking points

Discuss repeatable owner destruction, shallow versus retained size, root path, LeakCanary watch flow, false positives, and heap-data privacy.

## Follow-up questions

- **Interviewer:** "What is the difference between Shallow Size and Retained Size in a heap dump?"
  **Answer:** "Shallow Size is the memory consumed by the object itself (its fields and header). Retained Size is the shallow size plus the memory of all objects that are exclusively reachable from this object and would be reclaimed if this object were garbage collected."

- **Interviewer:** "Why shouldn't LeakCanary's full heap dumping be run in production builds?"
  **Answer:** "Dumping the heap freezes the runtime process (`Stop-The-World`), which degrades user experience and can trigger ANRs. Furthermore, heap dumps contain raw heap memory, which could expose sensitive user PII or credentials."

## Self-check rubric

Reproduce a lifetime boundary, inspect a root path, explain LeakCanary's flow, distinguish retained and shallow size, and verify the fix.

## References and reviewed-on date

- [Android Studio Memory Profiler](https://developer.android.com/studio/profile/memory-profiler) — heap inspection.
- [How LeakCanary works](https://square.github.io/leakcanary/fundamentals-how-leakcanary-works/) — watch, dump, and trace process.
- [Manage app memory](https://developer.android.com/topic/performance/memory/manage-app-memory) — broader memory categories.

Technically reviewed against primary documentation on 2026-10-13.
