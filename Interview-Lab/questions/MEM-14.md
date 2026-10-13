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

LeakCanary detects leaks automatically in debug builds by tracking destroyed Activities/Fragments via `WeakReference`, prompting a heap dump, and parsing the HPROF file with Shark. Analyzing a heap dump in Android Studio Profiler or LeakCanary involves identifying the GC Root, following the retained reference chain, and determining which reference prevented legitimate garbage collection.

## Interview answer — structured

Analyzing memory leaks requires capturing a heap dump (.hprof file) and finding the shortest strong reference path from a GC Root to a destroyed object.

In development, **LeakCanary** automates this entire workflow:
1. It hooks into lifecycle callbacks (`ActivityLifecycleCallbacks`, `FragmentManager`).
2. When `onDestroy()` occurs, it passes the instance to an `ObjectWatcher` wrapped in a `KeyedWeakReference` with an associated reference queue.
3. If the reference is not cleared after 5 seconds, LeakCanary triggers a GC. If the object persists, it is flagged as *retained*.
4. Once a threshold is reached, it dumps the heap and invokes **Shark** (Square's high-speed Kotlin HPROF parser) on a background thread to compute the leak trace.

When analyzing the leak trace, we focus on the transition from `Leaking: NO` to `Leaking: YES`. That exact boundary points to the field or closure holding the rogue reference, allowing us to nullify the reference or unbind the lifecycle observer.

## Interview answer — deep senior

In complex production scenarios where LeakCanary is impractical due to heap dump overhead (dumping the heap pauses the process for hundreds of milliseconds), we analyze heap dumps offline using Android Studio Profiler or Eclipse Memory Analyzer Tool (MAT).

In MAT, we run the **Dominator Tree** and **Leak Suspects** report. The Dominator Tree groups objects such that object A dominates object B if every path from a GC Root to B must pass through A. Looking at the **Retained Size** (the total memory that would be freed if an object were collected) immediately reveals culprit classes holding dozens of megabytes.

To monitor leaks in production, we can use LeakCanary's Shark library paired with WorkManager to upload stripped, deduplicated leak signatures without transmitting sensitive user PII from the full memory dump.

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
