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

كيفية اكتشاف وتحديد عمليات الـ Recomposition الزائدة غير الضرورية (Avoidable Recompositions) ومعالجتها:

1. الأدوات الرسمية لاكتشاف الـ Recomposition المفرط:
   - **Layout Inspector في Android Studio**:
     * يعرض عمودين حاسمين لكل Composable: **Recomposition Count** و **Skip Count**.
     * إذا رأيت الـ Recomposition Count يتزايد باستمرار مع كل حركة بينما الـ Skip Count ثابت عند 0، فهذا مؤشر صريح على وجود Recomposition زائد!
   - **Compose Compiler Metrics**:
     * توليد تقارير الـ HTML والـ Text لمعرفة الدوال المصنفة كـ `restartable` فقط دون `skippable`، وتحديد البارامترات الـ `unstable` بالاسم.

2. الأسباب الشائعة للـ Avoidable Recompositions:
   - **تمرير بارامترات Unstable**: تمرير `List<T>` عادية أو كلاس خارجي.
   - **كتابة كائنات جديدة داخل الـ Composable**: مثل إنشاء `Modifier.padding()` جديد داخل حلقة أو إنشاء كائنات Formatter بدون `remember`.
   - **قراءة الـ State في مرحلة مبكرة جداً**: قراءة حالة سريعة التغير في مرحلة التكوين (Composition Phase) بدلاً من مرحلة الـ Layout/Draw عبر Lambdas.

3. استراتيجية الإصلاح:
   - استخدام `remember` للكائنات الحسابية.
   - استخدام Lambdas لتأجيل قراءة الـ State (`Modifier.offset { ... }`).
   - استخدام `derivedStateOf` لامتصاص الترددات العالية.

## Practical walkthrough

تشخيص وإصلاح Recomposition متكرر أثناء الكتابة في حقل نصي:
```kotlin
// ❌ كود يسبب إعادة تركيب الشاشة بالكامل في كل حرف يُكتب:
@Composable
fun BadSearchScreen() {
    var query by remember { mutableStateOf("") }
    Column {
        TextField(value = query, onValueChange = { query = it })
        // 💥 قراءة query هنا تجبر HeavyResultsList على إعادة التركيب في كل ضغطة مفتاح:
        HeavyResultsList(query = query)
    }
}

// ✅ كود مفصول: عزل الحالة، وإجراء البحث عبر Debounced ViewModel، وتخطي القائمة الثقيلة:
@Composable
fun GoodSearchScreen(viewModel: SearchViewModel = viewModel()) {
    val query by viewModel.query.collectAsStateWithLifecycle()
    val results by viewModel.searchResults.collectAsStateWithLifecycle()

    Column {
        SearchInput(query = query, onQueryChange = viewModel::onQueryChanged)
        // HeavyResultsList يعاد تركيبها فقط عندما تتغير نتائج البحث الفعلية وليس مع كل حرف:
        HeavyResultsList(results = results)
    }
}
```

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

Identify avoidable recomposition using Android Studio Layout Inspector (tracking Recomposition Counts vs Skip Counts) and Compose Compiler Metrics. Fix it by eliminating unstable parameters, wrapping heavy allocations in `remember`, deferring state reads to the layout/draw phases via lambdas, and dampening high-frequency reads with `derivedStateOf`.

## Interview answer — structured

Detecting and eliminating avoidable recompositions is central to maintaining 60/120fps UI fluidity.

1. **Detection Tools**:
   - **Android Studio Layout Inspector**: We enable recomposition highlights and inspect the **Recomposition Count** and **Skip Count** columns in real-time. If interacting with a single widget (e.g. typing in a search bar) increments the recomposition count of distant, unrelated UI elements while their skip count remains zero, a state leak or unstable parameter is present.
   - **Compose Compiler Metrics**: Generating compiler metrics reveals which composables are marked as `unskippable` and highlights exact unstable parameters.

2. **Common Root Causes & Fixes**:
   - **Unstable Parameter Leaks**: Using unstable collections (`List<T>`). Solved with `@Immutable` or `ImmutableList`.
   - **Premature State Reading**: Reading rapidly changing state (like scroll offset) in the *composition phase*. Solved by deferring reads to the *layout or draw phase* using lambda-based modifiers (`Modifier.offset { ... }` or `drawBehind { ... }`).
   - **Unmemoized Allocations**: Creating fresh objects on every recomposition pass without `remember`.

## Interview answer — deep senior

Understanding Compose's three rendering phases—**Composition**, **Layout**, and **Draw**—is the highest-leverage insight for optimization. If a state is read during the Composition phase, any mutation forces the composable function to re-execute from top to bottom. If state is read strictly during the Layout phase (inside `MeasurePolicy` or a layout lambda modifier), Compose **skips composition entirely** and executes only layout measurement. If state is read in the Draw phase (inside `Modifier.drawWithContent { ... }`), Compose skips both composition and layout, jumping directly to the canvas draw pass!

Another critical check is **Lambda Stabilization**. Passing inline lambdas that capture changing values or unstable parent properties invalidates the lambda instance on every pass unless Strong Skipping is enabled or the lambda is hoisted or wrapped in `remember`.

## How to answer in the interview

- **Why:** recomposition counts do not measure duration.
- **How:** locate the phase and expensive call in a trace.
- **Trade-off:** splitting composables can obscure code without fixing the hot path.
- **Failure case:** optimizing stability while image decode causes jank.
- **Production solution:** benchmark a release-like build and compare frames.

## Deep-dive talking points

Cover baseline, release tracing, composition/layout/draw, state-read scope, compiler reports, and correctness regression.

## Follow-up questions

- **Interviewer:** "What is the three-phase pipeline of Jetpack Compose?"
  **Answer:** "The three phases are: 1. Composition (what UI to show - running composable functions), 2. Layout (where to place UI - measure and position nodes), and 3. Drawing (how to render UI - issuing GPU draw calls to Canvas)."

- **Interviewer:** "How does `Modifier.offset { ... }` differ from `Modifier.offset(x, y)`?"
  **Answer:** "`Modifier.offset(x, y)` accepts concrete values and reads state in the Composition phase. `Modifier.offset { IntOffset(...) }` accepts a lambda, deferring state reads to the Layout phase, completely bypassing recomposition."

## Self-check rubric

Describe a baseline, identify the costly phase, propose one narrow fix, and remeasure correctness and frames.

## References and reviewed-on date

- [Diagnose stability issues](https://developer.android.com/develop/ui/compose/performance/stability/diagnose) — reports and Layout Inspector.
- [Compose phases](https://developer.android.com/develop/ui/compose/phases) — distinct render work.

Technically reviewed against primary documentation on 2026-10-13.
