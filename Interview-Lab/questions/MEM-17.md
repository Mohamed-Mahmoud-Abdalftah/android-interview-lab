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

ما هو الـ UI Jank؟ وشرح توقيت الفريمات (Frame Timing)، وإعادة التركيب المفرطة في Compose (Excessive Recompositions)، وثقل العمل على الـ Main Thread:

1. ما هو الـ UI Jank؟
   - الشاشة القياسية تعمل بمعدل تحديث 60Hz (أو 90Hz/120Hz في الشاشات الحديثة ذات التقنية العالية).
   - في شاشة 60Hz، يمتلك التطبيق مهلة قدرها **16.6 مللي ثانية (ms)** لإنجاز كل شيء خاص بالفريم: قياس الـ Layout، الرسم، والمعالجة.
   - في شاشة 120Hz، تنخفض المهلة إلى **8.3 مللي ثانية (ms)** فقط!
   - إذا تأخر الـ Main Thread أو الـ RenderThread في تسليم الفريم في الوقت المحدد لـ `VSYNC`، يسقط الفريم (Dropped Frame) ويتكرر الفريم السابق، مما يظهر للمستخدم كتشنج وتقطيع في الحركة يسمى **Jank**.

2. أسباب الـ Jank في الـ Views التقليدية:
   - إجهاد الـ Main Thread بعمليات I/O أو معالجة نصوص أو حجز كائنات (Memory Churn -> GC Pauses).
   - تعقيد شجرة الواجهة (Deep View Hierarchy) مما يسبب قياسات متداخلة وبطيئة (Multi-pass measure/layout).

3. أسباب الـ Jank في Jetpack Compose (Excessive Recompositions):
   - تمرير كائنات غير مستقرة (Unstable Parameters مثل `List<T>` العادية بدلاً من `ImmutableList`).
   - قراءة الـ State في مرحلة التكوين (Composition Phase) بدلاً من مرحلة الرسم (Draw Phase أو Layout Phase عبر Lambdas مثل `Modifier.offset { ... }`).
   - تكرار استدعاء دوال الحسابات داخل الـ Composable دون تغليفها بـ `remember { ... }`.

## Practical walkthrough

مقارنة عملية لتجنب الـ Jank في Jetpack Compose:
```kotlin
// ❌ كود يسبب Recomposition مستمر في كل بكسل سكرول (Jank مؤكد):
@Composable
fun BadScrollHeader(scrollState: ScrollState) {
    // قراءة scrollState.value مباشرة في مرحلة الـ Composition تجبر إعادة بناء الدالة كلها في كل حركة:
    val offset = scrollState.value * 0.5f
    Box(modifier = Modifier.offset(y = offset.dp)) {
        HeaderContent()
    }
}

// ✅ كود فائق السلاسة: تأجيل قراءة الـ State إلى مرحلة الـ Layout عبر Lambda Modifier:
@Composable
fun GoodScrollHeader(scrollState: ScrollState) {
    // Modifier.offset(lambda) يؤجل قراءة الـ State إلى مرحلة القياس والرسم، متخطياً الـ Recomposition بالكامل:
    Box(modifier = Modifier.offset { IntOffset(x = 0, y = (scrollState.value * 0.5f).roundToInt()) }) {
        HeaderContent()
    }
}
```

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

UI jank occurs when a frame fails to render within the hardware VSYNC window (16.6ms for 60Hz, 8.3ms for 120Hz), causing dropped frames. Causes include heavy work on the main thread, layout thrashing, frequent GC pauses, and excessive recompositions in Compose caused by unstable types or reading states during the composition phase instead of layout/draw phases.

## Interview answer — structured

UI jank is the visual stutter experienced by users when the application fails to produce a frame in time for the display's VSYNC signal.

Displays refresh at fixed intervals: 60Hz displays require rendering within **16.6ms**, while modern 120Hz panels allow just **8.3ms**. A frame pipeline consists of three sequential phases: Application Main Thread (handling input, animating, measuring, and recording draw commands), RenderThread (uploading GPU commands), and SurfaceFlinger (compositing onto the hardware frame buffer).

If any phase exceeds its budget, the system misses the VSYNC deadline and repeats the previous frame. In legacy Views, jank stems from nested layout passes, costly `onDraw()` operations, and GC pauses from allocation churn.

In Jetpack Compose, the most common jank source is **excessive recompositions** during scrolling. Passing unstable parameters triggers unnecessary recompositions of large composable subtrees. Furthermore, reading rapidly changing state (like scroll position) during the *Composition* phase rather than deferring it to the *Layout* or *Draw* phase via lambda modifiers forces full tree recomposition on every pixel movement.

## Interview answer — deep senior

To deeply diagnose jank, we examine the Choreographer logs and Perfetto traces. The `Choreographer` class coordinates timing, scheduling callbacks for Input, Animation, Traversal, and Commit. When logs report `Skipped 30 frames! The application may be doing too much work on its main thread`, Choreographer detected that multiple VSYNC ticks elapsed before the message queue returned to idle.

In Compose, we profile recomposition counts using the **Layout Inspector** and Compose Compiler Metrics (`reportsDestination`). Marking data classes with `@Immutable` or wrapping unstable collections with Kotlinx Immutable Collections (`ImmutableList`) enables the compiler to mark composables as `skippable`.

Another critical lever is using `derivedStateOf { ... }`. When a state changes continuously (e.g. `scrollState.firstVisibleItemIndex`), using `derivedStateOf` ensures observers only recompose when a calculated boolean or threshold actually changes.

## How to answer in the interview

- **Why:** Define jank by missed presentation deadlines.
- **How:** Trace frame timeline and Main computation.
- **Trade-off:** Memoization trades CPU for retained memory.
- **Failure case:** Counting recompositions alone misdiagnoses jank.
- **Production solution:** Move heavy transforms and compare frame-tail distribution.

## Deep-dive talking points

Discuss refresh-rate-dependent deadlines, Main versus RenderThread/GPU, Compose skipping, expensive state derivation, and tail frame metrics.

## Follow-up questions

- **Interviewer:** "How does `derivedStateOf` prevent recomposition jank during scrolling?"
  **Answer:** "`derivedStateOf` acts as a dampener: it buffers high-frequency state updates (like scroll offsets changing every millisecond) and only triggers recomposition when the resulting derived calculation (like `index > 0`) changes its boolean or discrete output value."

- **Interviewer:** "What is the role of RenderThread in modern Android?"
  **Answer:** "Introduced in Android 5.0, the RenderThread offloads the actual GPU rendering commands (OpenGL/Vulkan) from the Main thread, handling animations like ripples independently even if the Main thread is temporarily busy."

## Self-check rubric

Define a missed frame, describe two pipeline causes, explain Compose recomposition limits, and plan a traced before/after test.

## References and reviewed-on date

- [Measure app performance](https://developer.android.com/topic/performance/measuring-performance) — frame timing and Compose tracing.
- [System tracing overview](https://developer.android.com/topic/performance/tracing) — device-wide timing.
- [Compose performance](https://developer.android.com/develop/ui/compose/performance) — recomposition and UI optimization.

Technically reviewed against primary documentation on 2026-10-13.
