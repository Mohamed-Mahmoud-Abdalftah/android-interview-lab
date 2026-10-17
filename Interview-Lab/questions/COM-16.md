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

## Concept and technical explanation

Identifying avoidable recomposition in Jetpack Compose involves systematically auditing UI trees using developer tooling, compiler metrics, and runtime profiling. Avoidable recompositions occur when composable functions re-execute despite their visually rendered content remaining unchanged, typically triggered by unstable parameter types, frequent ambient state reads hoisted unnecessarily high, or instantiating unmemoized objects inside composable bodies. Engineers diagnose these regressions using the Android Studio Layout Inspector recomposition counters, Compose Compiler metrics reports, and runtime recomposition highlighting modifiers.

## Practical walkthrough (English)

Diagnosing and eliminating an avoidable recomposition loop:
```kotlin
// ❌ AVOIDABLE RECOMPOSITION: Reading scroll position too early in parent hierarchy!
// The entire ParentScreen recomposes on every single scrolled pixel!
@Composable
fun BadParentScreen(listState: LazyListState) {
    // ❌ ANTI-PATTERN: Reading scroll offset directly causes entire screen to recompose on every pixel!
    val offset = listState.firstVisibleItemScrollOffset

    HeaderView(offset = offset)
    LazyColumn(state = listState) { /* items */ }
}

// ✅ FIXED: Defer state reads using lambda modifiers or derivedStateOf!
@Composable
fun OptimizedParentScreen(listState: LazyListState) {
    // Reading state is deferred directly to the layout phase via a lambda!
    HeaderView(
        modifier = Modifier.offset {
            // State read happens in LAYOUT phase, completely bypassing COMPOSITION phase!
            IntOffset(x = 0, y = listState.firstVisibleItemScrollOffset)
        }
    )
    LazyColumn(state = listState) { /* items */ }
}
```

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

We identify avoidable recompositions using Android Studio Layout Inspector, Compose Compiler metrics reports, and runtime profiling tools. Layout Inspector displays real-time recomposition and skip counts for every node. Compiler metrics generate reports flagging restartable and skippable composables and highlighting unstable parameters. Common fixes include stabilizing data models, wrapping expensive objects in remember, using derivedStateOf, and deferring state reads to the layout phase via lambda modifiers.

## Interview answer — structured

Diagnosing and eliminating avoidable recomposition is a core discipline for senior Android engineers ensuring fluid 60fps or 120fps UI performance.
Avoidable recompositions occur when composables re-run without producing any visual change.
The primary diagnostic tool is Android Studio's Layout Inspector.
When connected to a running debug build, Layout Inspector overlays live Recomposition Count and Skip Count columns beside the component tree.
If a component's recomposition count increments continuously during idle states or simple scrolling while its skip count remains zero, that composable is suffering from avoidable recomposition.
The second essential tool is Compose Compiler Metrics.
By passing compiler flags like reportsDestination in Gradle, the compiler generates text files detailing which composables are skippable versus restartable-only, explicitly listing unstable parameters like standard Lists or third-party classes.
The third diagnostic technique is using debug highlighting modifiers like recomposeHighlighter, which flashes colored bounding boxes around composables as they recompose.
Once identified, engineers resolve these bottlenecks by wrapping collections in @Immutable wrappers, deferring state reads to layout or draw phases, and memoizing lambdas and calculations with remember.

## Interview answer — deep senior

Under the hood, diagnosing recompositions requires understanding Compose's three distinct rendering phases: Composition, Layout, and Draw.
Avoidable recomposition regressions almost always stem from reading high-frequency state during the Composition phase when the read could have been deferred to the Layout or Draw phases.
When you read a SnapshotState primitive (such as scroll offset or animation progress) directly in a composable function body, Compose registers a dependency inside the current RecomposeScope. Every frame tick invalidates that scope, forcing the Compose runtime to re-execute the function, allocate new layout nodes, and reconcile the SlotTable.
By deferring the state read using lambda-based modifiers—such as Modifier.offset { IntOffset(0, state.value) } or Modifier.drawBehind { drawCircle(...) }—the state read is deferred past the Composition phase entirely.
When the state mutates, Compose skips the Composition phase and invalidates only the LayoutNode or RenderNode directly on the hardware canvas, achieving near-zero CPU overhead.
Furthermore, analyzing compiler metrics reports (specifically *-composables.txt and *-classes.txt) reveals stability signatures.
If a function is marked restartable but not skippable, the report pinpoints the exact culprit parameter marked as unstable.
Senior engineers integrate compiler metrics audits into CI pipelines to fail pull requests that introduce accidental stability regressions into critical user journeys. This automated enforcement guarantees that production apps maintain zero-jank UI responsiveness across all supported device tiers.

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
