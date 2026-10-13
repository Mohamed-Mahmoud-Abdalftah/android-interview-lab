---
id: "COM-16"
question: "How do you identify avoidable recomposition?"
topic: "Jetpack Compose"
code: "COM"
group: "B"
phase: 3
priority: "P1"
order: 245
editorial_status: "reviewed"
---

# COM-16

## Original interview question

How do you identify avoidable recomposition?

## What the interviewer evaluates

- Start from observed frame problem and use profiling evidence.
- Separate composition, layout, and draw costs.
- Trace state reads, unstable inputs, and expensive body work before changing code.

## Explanation in Arabic

ابدأ بمشكلة محسوسة: typing متقطع أو scroll jank، ثم قِس frame timing في release build. Android Studio Layout Inspector يبين recomposition/skip counts، وCompose compiler reports تكشف stability، وsystem trace يوضح أين وقت frame. لا تعتبر أي recomposition خطأ: إذا تغير نص ظاهر، تحديثه ضروري. ابحث عن scope واسعة تقرأ state سريعة، calculation ثقيلة داخل body، أو parameters تتغير هويتها بلا سبب. بعد تغيير صغير قِس من جديد وتأكد أن UI ما بقتش قديمة.

### Practical walkthrough in Egyptian Arabic

لو عدّاد recomposition زاد، ده مؤشر للتحقيق مش إثبات bottleneck. سجل trace في release/profileable build، اعرف الوقت رايح composition ولا measure/draw ولا image decode. بعدين شوف compiler stability report والـstate read scope؛ غير حاجة واحدة وقارن frame time ونتيجة UI. مثال sort يوضح إن تكلفة واحدة داخل scope أهم من مئات Text رخيصة. بعد نقل الحساب قارن p95 frame time وتأكد إن ترتيب النتائج لم يتغير.

## Why it matters and how it works

Compose may recompose a parent and skip children; state reads in different phases can cause composition, measure or draw work. Recomposition counts indicate activity but not duration. Compiler reports describe parameter stability and skippability, while traces show actual CPU/frame cost. An avoidable recomposition is meaningful only if eliminating it improves a measured problem without hiding legitimate updates.

## Worked example

On each search keystroke, a root screen reads `query`, rebuilds a sorted 2,000-item list and passes a freshly allocated configuration object to every row. Trace confirms composition takes too long. Move sorting into a ViewModel-backed stream with appropriate cancellation, keep the query read near the result content, and stabilize row inputs; compare frames before and after. If the trace instead shows image decode, fix that stage.

### Compose/Kotlin walkthrough

```kotlin
// A cheap child is not the likely bottleneck; isolate expensive work.
@Composable
fun SearchResults(query: String, results: List<ProductUi>) {
    // Do not sort thousands of rows here on every query edit.
    Text("Results for $query")
    LazyColumn {
        items(results, key = ProductUi::id) { product -> ProductRow(product) }
    }
}
// ViewModel/search pipeline prepares results; trace composition and frame time
// before and after moving the sort.
```

## Trade-offs and decision criteria

Smaller composables and cached calculations can reduce work but add code and memory. Strong skipping may already avoid child calls, so broad `@Stable` annotation is not justified by intuition. Deferring a state read to draw can help some visual updates but may complicate implementation; benchmark a representative device.

## Failure modes

Debug-build timings are treated as production performance. A mutable type is annotated stable to lower counters and UI stops updating. A remembered calculation uses wrong keys and shows stale results. Optimization targets recomposition count while a blocked main thread or layout pass dominates jank.

## Production perspective

Capture baseline frame metrics, relevant traces and UI correctness tests. Change one cause, profile a release build, and keep a regression macrobenchmark for a critical screen if the gain is material.

## Interview answer — short

“I profile a real frame problem, inspect recomposition and skip counts plus compiler reports, trace costly state reads or body work, and verify release-frame improvement after a focused change. Measure frame cost before calling a recomposition avoidable.”

## Interview answer — structured

“I do not label every recomposition waste. I reproduce a user-visible slow path on a release build, inspect Layout Inspector counts and system traces, and ask whether composition, layout or draw actually costs the frame. Then I locate rapidly changing state reads, expensive calculations, or inputs whose identity changes unnecessarily. I narrow or move work and remeasure. If the bottleneck is image decoding, optimizing skip rules would miss it. I use a trace to tell an expensive sort apart from harmless Text recomposition or image decode.”

## Interview answer — deep senior

“My first artifact is a measurable problem: for example p95 frame time while typing into a feed search, not a screenshot of a high recomposition counter. I reproduce it under a realistic list size in release configuration and use a system trace to identify composition, measurement, drawing, or unrelated main-thread work. Layout Inspector and Compose compiler reports help explain which composables re-execute and whether their inputs are considered skippable. I trace the exact state read: a root scope reading every keystroke may cause broad work, while a narrower results component may contain it. I also look for sorting or formatting done in render code and allocations that change child parameter identity. I fix one cause, perhaps move filtering into a cancelable ViewModel pipeline and give rows stable IDs and inputs, then compare frame metrics and behavior. I resist false `@Stable` annotations or incorrectly keyed `remember`, because those can hide updates. If composition time is small but image decode or layout dominates, I change direction. The goal is smoother, correct interaction on target devices, with a benchmark protecting a material improvement. I would compare release frame timing after the targeted change, not celebrate a smaller counter alone.”

## How to answer in the interview

- **Why:** recomposition counts do not measure duration.
- **How:** locate the phase and expensive call in a trace.
- **Trade-off:** splitting composables can obscure code without fixing the hot path.
- **Failure case:** optimizing stability while image decode causes jank.
- **Production solution:** benchmark a release-like build and compare frames.

## Deep-dive talking points

Cover baseline, release tracing, composition/layout/draw, state-read scope, compiler reports, and correctness regression.

## Follow-up questions

- Is a high recomposition count automatically bad? **Answer:** no; it may be cheap and required by changed visible state.
- Why profile a release build? **Answer:** debug overhead and optimizations can distort real frame costs.
- What is the risk of a wrong `remember` key? **Answer:** stale derived content can remain visible despite changed inputs.

## Self-check rubric

Describe a baseline, identify the costly phase, propose one narrow fix, and remeasure correctness and frames.

## References and reviewed-on date

- [Diagnose stability issues](https://developer.android.com/develop/ui/compose/performance/stability/diagnose) — reports and Layout Inspector.
- [Compose phases](https://developer.android.com/develop/ui/compose/phases) — distinct render work.

Technically reviewed against these primary sources on 2026-10-11 by automated editorial review. The performance case is illustrative.
