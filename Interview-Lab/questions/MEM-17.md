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

## Concept and technical explanation

UI jank is the perceived visual stutter, frame drop, or irregularity that occurs when an application fails to deliver a rendered frame within the refresh interval dictated by the display hardware. On standard 60Hz displays, the rendering pipeline must complete within 16.6 milliseconds; on high-refresh-rate 90Hz or 120Hz displays, this window tightens to 11.1ms and 8.33ms respectively. The Android rendering pipeline operates in synchronized phases driven by hardware VSYNC pulses dispatched through the Choreographer. During a frame interval, the Main Thread processes input events, evaluates animations, executes view tree traversals (measure, layout, draw), or executes Jetpack Compose recomposition and layout passes. Once the display list or drawing commands are compiled, they are synchronized to the RenderThread, which submits draw commands to the GPU command buffer. Jank occurs when either the Main Thread or RenderThread overruns the VSYNC deadline. In classic View hierarchies, excessive view depth, nested layouts, and expensive background draws cause jank. In Jetpack Compose, jank is frequently provoked by recomposition storms: when composable functions repeatedly recompose due to unstable parameters, reading rapidly changing observable state during the composition phase rather than deferring it to the layout or draw phases, or allocating heavy objects inside composable bodies.

## Practical walkthrough (English)

Contrasting state reading in Composition vs deferred reading in Layout/Draw:
```kotlin
// ❌ Anti-pattern: Reading scrollState directly in composition causes recomposition on every pixel scroll:
@Composable
fun BadScrollHeader(scrollState: ScrollState) {
    // Recomposition runs on every scroll update, creating massive CPU churn and UI jank:
    val offset = scrollState.value * 0.5f
    Box(modifier = Modifier.offset(y = offset.dp)) {
        HeaderContent()
    }
}

// ✅ Optimal pattern: Deferring state reading to the layout phase via a lambda modifier:
@Composable
fun GoodScrollHeader(scrollState: ScrollState) {
    // Modifier.offset(lambda) skips composition entirely and reads state during the layout/measurement phase:
    Box(modifier = Modifier.offset { IntOffset(x = 0, y = (scrollState.value * 0.5f).roundToInt()) }) {
        HeaderContent()
    }
}
```
In this scenario, `BadScrollHeader` reads `scrollState.value` during the composition phase. Because `scrollState.value` changes with every single touch pixel during scrolling, the entire composable function and its sub-tree are repeatedly recomposed, allocating new modifiers and flooding the Main Looper with frame work that exceeds 16.6ms. By contrast, `GoodScrollHeader` uses `Modifier.offset { ... }`. The lambda delays reading the state until the Layout phase, entirely skipping the Composition phase. The UI tree remains unchanged, recomposition count drops to zero, and the frame renders comfortably under 8ms.

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

UI jank occurs when a frame fails to render within the hardware display deadline (16.6ms at 60Hz or 8.33ms at 120Hz). It is caused by excessive execution on the Main Thread, GC allocation churn, or inefficient UI rendering. In Jetpack Compose, reading observable state during composition instead of deferring to layout or draw causes continuous recomposition storms and severe frame drops.

## Interview answer — structured

UI jank represents dropped or delayed visual frames caused by an application missing the display hardware VSYNC refresh deadline.

The frame rendering pipeline requires strict coordination between the Main Thread, the RenderThread, and the GPU. On a 60Hz display, the system has a budget of 16.6 milliseconds per frame, while a 120Hz display reduces this budget to roughly 8.3 milliseconds. When the Main Thread is encumbered by synchronous computation, large database queries, or excessive view measurement passes, it fails to submit drawing commands to the RenderThread in time.

In production, involving Jetpack Compose, the predominant root cause of jank is uncontrolled recomposition. When unstable parameters or observable state changes force extensive sub-trees to re-execute, the Main Thread spends its entire frame budget executing Kotlin code instead of rendering. A classic failure mode is reading animated scroll state directly during the composition phase rather than deferring the read to the layout or draw phase using lambda modifiers.

Resolving jank requires isolating heavy computation off the Main Thread, marking data classes as Immutable or Stable, utilizing derivedStateOf to throttle emissions, and verifying frame delivery with Macrobenchmark frame timing metrics.


## Interview answer — deep senior

At the low-level rendering architecture, frame production is governed by the Android Choreographer and SurfaceFlinger. The Choreographer coordinates frame dispatching via VSYNC signals received from the hardware composer. When a VSYNC-app pulse arrives, the Choreographer executes callbacks in strict sequence: input handling, animations, traversals (Measure, Layout, Draw), and commit. Once complete, syncFrameState transfers the display list to the RenderThread, which converts primitives into OpenGL ES or Vulkan commands and queues them into the SurfaceFlinger BufferQueue.
When the Main Thread takes 20ms to process a frame, it skips the next VSYNC-sf presentation pulse, causing SurfaceFlinger to re-display the previous buffer. This is classified as a dropped frame. If a frame takes longer than 700ms, Android Vitals registers a frozen frame, severely penalizing the application in Google Play store metrics.
In modern Jetpack Compose architectures, the Compose runtime relies on a Gap Buffer data structure called the Slot Table. During composition, changes in observable state invalidate snapshot scopes, prompting the composer to traverse the slot table and emit UI tree mutations. If an engineer reads a rapidly changing State object (such as scroll offset or touch gestures) in the composition phase, the runtime is forced to execute recomposition on every pixel. By leveraging lambda-based modifiers such as Modifier.offset { ... } or Modifier.drawWithContent { ... }, state reading is postponed to the layout or draw phases, entirely bypassing slot table diffing and composition overhead.
To profile and eliminate jank systematically, senior engineers use Android Studio System Trace and the Compose Compiler metrics report (compilerMetrics and reportsDestination) to audit composable functions for skippability and stability. In CI, we assert on Macrobenchmark FrameTimingMetric across 90th and 99th percentiles, ensuring that scrolling journeys maintain steady 120 FPS rendering across device tiers.

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
