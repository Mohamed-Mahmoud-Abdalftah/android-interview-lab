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

Excessive recomposition on keystrokes occurs when a single monolithic `UiState` containing the query string is passed to child composables, invalidating the entire screen on every character. Fix it by decoupling text input state from unrelated UI branches, passing granular stable parameters, and debouncing queries in the ViewModel.

## Interview answer — structured

A screen re-rendering excessively after each keystroke is a classic symptom of poor state granularity and un-hoisted state coupling.

1. **Root Cause**: When a user types a letter, the `TextField` emits `onValueChange`. The ViewModel modifies a property (e.g. `query`) inside a monolithic `ScreenUiState` data class. Because the root composable reads `val state by viewModel.uiState.collectAsStateWithLifecycle()`, the root and every child composable that accepts `state` as a parameter are re-evaluated. If heavy feeds, charts, or lists take `ScreenUiState`, they fail smart skipping and recompose on every typed character, inducing severe keyboard lag.

2. **Diagnosis**: In the Android Studio **Layout Inspector**, I type into the search field and watch the Recomposition counter. If the product list or summary card recomposition count increments alongside the search bar, the state boundary is leaking.

3. **Architectural Fix**:
   - **Granular Parameter Passing**: Do not pass the whole state class to children. Pass only the data each child requires (e.g. `items = state.feedItems`). If `feedItems` has not mutated, Compose skips the feed completely.
   - **State Isolation & Debouncing**: In the ViewModel, decouple raw text typing from query execution using a distinct `MutableStateFlow<String>` with `.debounce(300ms).distinctUntilChanged()` before executing searches.

## Interview answer — deep senior

Under the hood, Kotlin data classes implement structural equality across all fields. When `state.copy(query = "a")` produces a new instance, passing `state` into `HeavyFeedView(state)` passes an object whose `equals()` evaluates to `false` because the `query` field changed, even though `HeavyFeedView` only cares about `items`!

Another critical lever is using **Lambda-based State Readers** when children only need derived calculations. If a child merely needs to check if the query is empty, pass a lambda `isQueryEmpty: () -> Boolean = { query.isEmpty() }`, keeping the state read scoped strictly to the child that needs it.

In Compose Compiler metrics, we ensure all child item parameters are marked `@Immutable` or `ImmutableList` so Strong Skipping can cleanly bypass them while text mutations occur in adjacent branches.

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
