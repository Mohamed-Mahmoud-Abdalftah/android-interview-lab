---
id: "COM-23"
question: "A Compose screen re-renders excessively after each keystroke. How do you profile and fix it?"
topic: "Jetpack Compose"
code: "COM"
group: "C"
phase: 3
priority: "P1"
order: 252
editorial_status: "reviewed"
---

# COM-23

## Original interview question

A Compose screen re-renders excessively after each keystroke. How do you profile and fix it?

## What the interviewer evaluates

- Investigate the actual user-visible cost and trigger path.
- Propose a targeted refactor without stale state or unsafe stability annotations.
- Verify before/after release behavior and correctness.

## Concept and technical explanation

Excessive recomposition on every keystroke occurs when transient text field state is hoisted unnecessarily high in the composable hierarchy or when state mutations invalidate unskippable sibling composables. Diagnosing this bottleneck involves attaching the Android Studio Layout Inspector to observe recomposition tick counters during typing, alongside running Compose Compiler Metrics to identify unstable parameter types across the view tree. Resolving the regression requires isolating the raw keystroke state locally inside the input component, hoisting only debounced query values to architecture ViewModels, and stabilizing sibling data models using @Immutable wrappers to enable smart compiler skipping.

## Practical walkthrough (English)

Diagnosing and eliminating keystroke-induced recomposition churn:
```kotlin
// ❌ FAULTY ARCHITECTURE: Top-level parent screen observes every single keystroke!
// Typing 1 character causes ParentScreen, Header, HeavyBanner, and ProductGrid to recompose!
@Composable
fun BadSearchScreen(viewModel: BadSearchViewModel) {
    val query by viewModel.queryText.collectAsStateWithLifecycle()
    val products by viewModel.products.collectAsStateWithLifecycle()

    Column {
        HeavyHeader() // Recomposes on every keystroke!
        TextField(value = query, onValueChange = { viewModel.updateQuery(it) })
        ProductGrid(products = products) // Recomposes on every keystroke if products list is unstable!
    }
}

// ✅ ARCHITECTURAL BEST PRACTICE: Isolate keystroke state and debounce upstream events!
@Composable
fun OptimizedSearchScreen(
    productsState: ImmutableProductsState,
    onQuerySubmitted: (String) -> Unit
) {
    Column {
        HeavyHeader() // Skipped! Never recomposes during typing!
        LocalSearchField(onDebouncedQuery = onQuerySubmitted) // Recomposition strictly isolated here!
        ProductGrid(products = productsState) // Skipped! Inputs remain unchanged during typing!
    }
}

@Composable
fun LocalSearchField(onDebouncedQuery: (String) -> Unit) {
    // Keystroke state is isolated to this leaf composable only!
    var localText by remember { mutableStateOf("") }

    LaunchedEffect(localText) {
        delay(300) // Debounce before sending event upstream!
        onDebouncedQuery(localText)
    }

    TextField(
        value = localText,
        onValueChange = { localText = it },
        placeholder = { Text("Search...") }
    )
}
```

## Explanation in Arabic

تشخيص وإصلاح مشكلة إعادة تركيب الشاشة بالكامل (Excessive Recomposition) بعد كل ضغطة مفتاح في حقل الإدخال النصي:

1. كيف تحدث هذه المشكلة الكارثية؟
   - المستخدم يكتب حرفاً في `TextField`.
   - يتم استدعاء `onQueryChange(newText)` ويقوم الـ ViewModel بتحديث كائن الـ `UiState` المجمع للشاشة بالكامل (`ScreenUiState`).
   - إذا كانت الشاشة الرئيسية تقرأ `val uiState by viewModel.uiState.collectAsStateWithLifecycle()` في أعلى دالة الـ Screen وتمرر الـ `uiState` كاملاً إلى كل الدوال الفرعية:
   - في كل ضغطة حرف، يتم اعتبار كل الدوال الفرعية متغيرة، فيُعاد حساب شجرة الـ Views والقوائم والصور بالكامل، مما يسبب بطء الكتابة وتشنج لوحة المفاتيح (Input Latency & Jank)!

2. التشخيص العملي عبر الأدوات:
   - فتح **Layout Inspector**: كتابة نص وملاحظة أن أرقام الـ Recomposition Count لجميع البطاقات والقوائم تتزايد بعد كل حرف!
   - فحص الـ Flame Chart في **CPU Profiler**: رؤية وقت طويل مستهلك في تنفيذ دوال Composable أثناء حدث الـ KeyPress.

3. الحلول المعمارية الثلاثة:
   - **عزل حالة الإدخال (State Localization)**: الاحتفاظ بنص البحث محلياً أو في `StateFlow` منفصل لا يغير الـ UiState العامة للقائمة حتى اكتمال المعالجة.
   - **تمرير الحقول الجزئية (Granular Parameter Passing)**: تمرير الخصائص التي تحتاجها الدالة فقط (`products: ImmutableList<Product>`) بدلاً من تمرير كائن `ScreenUiState` الضخم بالكامل.
   - **تأخير البحث عبر Debounce**: استخدام `debounce(300ms)` في الـ ViewModel حتى لا يتم إرسال طلبات البحث الحسابية في كل حرف بل بعد توقف المستخدم عن الكتابة.

## Practical walkthrough

إصلاح مشكلة الـ Keystroke Recomposition وتطبيق العزل الحبيبي للحالة:
```kotlin
// ❌ كود سيء: يمرر كائن الحالة بالكامل لكل المكونات، مما يعيد تركيب القائمة الثقيلة في كل حرف:
@Composable
fun BadSearchDashboard(viewModel: DashboardViewModel) {
    val state by viewModel.uiState.collectAsStateWithLifecycle()
    Column {
        // كتابة حرف هنا تغير state.query وتجبر HeavyFeedView على إعادة التركيب فوراً!
        SearchInput(state.query, viewModel::onQueryChange)
        HeavyFeedView(state) // 💥 تعيد تركيب 100 عنصر في كل ضغطة مفتاح!
    }
}

// ✅ كود احترافي: تمرير المعاملات المستقلة وعزل الـ Feed عن تغيرات نص البحث:
@Composable
fun GoodSearchDashboard(
    query: String,
    onQueryChange: (String) -> Unit,
    feedItems: ImmutableList<FeedItem>
) {
    Column {
        SearchInput(query = query, onQueryChange = onQueryChange)
        // يتم تخطي HeavyFeedView بنسبة 100% أثناء الكتابة لأن feedItems لم تتغير!
        HeavyFeedView(items = feedItems)
    }
}
```

## Why it matters and how it works

Each edit changes observable text state. The scope that reads it is invalidated; broad parent work can then execute, while eligible children may still be skipped. Expensive calculation during composition consumes frame time even if lazy list rows are efficient. Debounce can reduce backend calls but changes responsiveness and is not a substitute for moving heavy work off the render path.

## Worked example

A catalog root reads `query`, filters 4,000 products and sorts by localized name before drawing a TextField and LazyColumn. A trace shows 20 ms composition on edits. Hoist query to ViewModel, cancel obsolete searches with latest-query semantics, expose result state, and isolate the TextField from unrelated header content. Test `a` → `ab` quickly and ensure old `a` results never replace `ab`.

### Compose/Kotlin walkthrough

```kotlin
// Inside ViewModel: query is StateFlow<String>; repository.search(String)
// returns Flow<List<ProductUi>> and cancels cooperatively.
val results: StateFlow<List<ProductUi>> = query
    .debounce(250)
    .distinctUntilChanged()
    .flatMapLatest(repository::search)
    .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), emptyList())
// Screen renders current query immediately and results separately.
// Imports: kotlinx.coroutines.flow.*; search returns Flow<List<ProductUi>>.
// Opt in to FlowPreview/ExperimentalCoroutinesApi if required by the
// project's coroutines version for debounce/flatMapLatest.
```

## Trade-offs and decision criteria

Moving filtering to a background dispatcher avoids main-thread blocking but can spend CPU on canceled work if algorithm is not cooperative. Debounce reduces calls but delays results. Memoization saves repeat computation only with complete keys and bounded memory. If trace shows layout or images instead, fix those stages.

## Failure modes

Optimizing counter values while frame time remains bad. A broad root recomposes on each character. A stale `remember` result ignores locale or dataset change. Old async results overwrite a new query. A fake `@Stable` annotation leaves the UI stuck at prior text.

## Production perspective

Capture a representative typing trace and p95 frame metric, make one targeted change, and rerun with realistic data and images. Add a rapid-query race test plus a UI assertion that text and results remain consistent.

## Interview answer — short

We diagnose excessive keystroke recomposition using Layout Inspector recomposition counters and Compose Compiler metrics. The primary root cause is hoisting raw keystroke state to the top-level parent, which forces unskippable siblings to re-execute on every character. We fix this by isolating local text state within the search bar component, debouncing updates sent to the ViewModel, and ensuring sibling components receive @Immutable data classes so they are skipped completely during input.

## Interview answer — structured

Diagnosing and curing excessive recomposition triggered by user keystrokes is a classic real-world Android performance problem.
When a user types in a text field, every single character change produces a state update.
If the application suffers from flawed state architecture, typing a single letter causes the entire screen—including heavy image carousels, complex lists, and navigation headers—to recompose continuously, producing noticeable typing lag and burning CPU cycles.
To profile this regression, we open Android Studio Layout Inspector while typing in a debug build.
Layout Inspector reveals the exact composables whose recomposition counters increment with every key press.
We then consult Compose Compiler Metrics to inspect the stability of the affected sibling composables.
The root cause is almost always dual-faceted: raw keystroke state was hoisted all the way to the top-level screen container, and sibling components accept unstable parameter types like raw standard Lists.
We apply a three-step architectural fix.
First, we isolate the raw text state locally inside a dedicated SearchBar composable so that only the text input node recomposes on keystrokes.
Second, we apply a debounce operator (such as delay(300)) before propagating the query upstream to the ViewModel.
Third, we ensure all sibling composables accept strictly @Immutable data models, allowing the Compose runtime to skip them entirely during input.

## Interview answer — deep senior

Under the hood, this performance degradation is governed by RecomposeScope invalidation boundaries and SlotTable dependency tracking.
When a composable reads a SnapshotState primitive—such as collecting a query StateFlow at the root screen level—the Compose compiler associates that state read with the root composable's RecomposeScope.
Every keystroke commits a new snapshot to the global Snapshot system.
The snapshot commit notifies the root RecomposeScope that its dependencies mutated, triggering an immediate invalidation of that scope.
During the subsequent composition pass, the Composer executes the root function body from top to bottom.
If child composables accept unstable parameters (such as standard Kotlin List<Product> or lambdas capturing mutable outer variables), the compiler's synthetic changed bitmask evaluates to UNCERTAIN.
Because the arguments cannot be guaranteed stable, the compiler is prohibited from executing early-return skipping, forcing every child composable to re-execute its layout logic, re-allocate modifier nodes, and reconcile slot intervals.
By moving the mutable state read into a localized leaf composable (LocalSearchField), the root RecomposeScope never reads the active keystroke state.
Consequently, snapshot commits invalidate only the localized leaf scope, leaving the parent and all sibling scopes completely un-invalidated.
Furthermore, debouncing the upstream event using Kotlin Coroutines prevents rapid network calls and database queries from interrupting the main thread during typing, securing rock-solid 120fps input fluidity.

## How to answer in the interview

- **Why:** edits invalidate readers, but expensive sort or IO causes the jank.
- **How:** locate cost in trace, then cancel old search work.
- **Trade-off:** debounce delays results, not local field echo.
- **Failure case:** old results overwrite newer input.
- **Production solution:** compare frame timing and correctness after rapid typing.

## Deep-dive talking points

Explain trace-first diagnosis, state-read scope, async query races, skip reports, and release remeasurement.

## Follow-up questions

- **Interviewer:** "Why is passing a monolithic `ScreenUiState` to child composables risky for performance?"
  **Answer:** "Because mutating any single property (like a typing query or transient error) produces a new `ScreenUiState` instance, causing every child that receives the whole object to fail equality checks and force recomposition."

- **Interviewer:** "How does `debounce(300)` in the ViewModel prevent search stutter?"
  **Answer:** "`debounce(300)` buffers high-frequency keystrokes, waiting until the user stops typing for 300 milliseconds before firing expensive filtering, repository, or network operations."

## Self-check rubric

Give baseline evidence, identify the hot path, make one safe change, and test performance and result ordering.

## References and reviewed-on date

- [Diagnose Compose stability](https://developer.android.com/develop/ui/compose/performance/stability/diagnose) — profiling tools.
- [Compose phases](https://developer.android.com/develop/ui/compose/phases) — phase costs.

Technically reviewed against primary documentation on 2026-10-13.
