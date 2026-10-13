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

ابدأ بتحديد هل كل keystroke تعمل jank أم مجرد recomposition counter عالي. سجّل trace وLayout Inspector/Compose compiler reports في build مناسب؛ راقب composition، measure، draw، image decode وmain thread. تتبع أين تقرأ `text`: لو root تقرأه ثم تعيد sorting كبير وتمرير object جديد لكل row، انقل القراءة والحساب إلى حد أضيق أو ViewModel pipeline مع cancellation/debounce حسب الحاجة. لا تجعل `remember` بمفتاح ناقص أو `@Stable` كذابة فيخفي تحديثات. بعد fix قارن frame time ونتائج البحث مع typing سريع.

### Practical walkthrough in Egyptian Arabic

ابدأ بسؤال: هل المشكلة jank فعلًا ولا counter عالي؟ لو trace بينت sorting داخل composition بـ20ms لكل حرف، انقلها لـViewModel pipeline مع `flatMapLatest` أو cancellation؛ خلي text field يستجيب فورًا والنتائج تتحدث لاحقًا. بعد الإصلاح جرّب `a` ثم `ab` بسرعة وتأكد النتيجة الأخيرة صحيحة. لو عملت debounce للـTextField نفسها، الكتابة هتحس إنها بطيئة؛ خلّي النص المحلي فوري وdebounce للبحث فقط. اختبر `a` ثم `ab` ونتيجة قديمة بترجع متأخر.

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

“I measure the keystroke frame, trace where text is read and expensive work runs, narrow or move that work, then remeasure with rapid typing and correct results. Trace the keystroke path, move expensive search work, and verify the latest query wins.”

## Interview answer — structured

“I first separate harmless recomposition from real jank using release traces. If the root reads every keystroke and filters thousands of rows during composition, I move the calculation to a cancelable state pipeline and keep reads near consumers. I inspect row identity and parameter churn but do not annotate types stable blindly. I test that old searches cannot overwrite new text, then compare frame timing and search correctness before and after. A 4,000-row sort in composition is a concrete culprit; I move it to a cancellable search pipeline.”

## Interview answer — deep senior

“The symptom is ‘re-renders excessively,’ but I need to know which work actually costs a frame. I reproduce it with production-sized data and capture a release trace while typing. Layout Inspector gives recomposition and skip clues; compiler reports help with parameter stability; the trace tells me whether composition, layout, draw or some unrelated main-thread step causes jank. I follow the text state read. If the root performs a 4,000-item localized sort on every character, I move search to a ViewModel pipeline, cancel obsolete queries and expose a coherent result state. A narrower composable reads the rapidly changing text, while unrelated headers receive stable inputs. I do not wrap everything in `derivedStateOf` or mark a mutable model `@Stable`; that can add overhead or hide changes. Debounce is a product choice about latency and backend load, so I use it only if appropriate. I test a fast `a` to `ab` sequence for stale-response races and verify the screen still renders the latest query. Finally I compare frame-time distribution and allocations on target devices; an improved counter with unchanged jank is not a fix. I keep the field responsive during debounce and confirm a late result for `a` cannot overwrite `ab`.”

## How to answer in the interview

- **Why:** edits invalidate readers, but expensive sort or IO causes the jank.
- **How:** locate cost in trace, then cancel old search work.
- **Trade-off:** debounce delays results, not local field echo.
- **Failure case:** old results overwrite newer input.
- **Production solution:** compare frame timing and correctness after rapid typing.

## Deep-dive talking points

Explain trace-first diagnosis, state-read scope, async query races, skip reports, and release remeasurement.

## Follow-up questions

- Does a high recomposition count prove jank? **Answer:** no; duration and render phase matter.
- What can go wrong with `remember` around filtering? **Answer:** incomplete keys can show stale results.
- Why cancel prior searches? **Answer:** late old responses must not replace the newest query result.

## Self-check rubric

Give baseline evidence, identify the hot path, make one safe change, and test performance and result ordering.

## References and reviewed-on date

- [Diagnose Compose stability](https://developer.android.com/develop/ui/compose/performance/stability/diagnose) — profiling tools.
- [Compose phases](https://developer.android.com/develop/ui/compose/phases) — phase costs.

Technically reviewed against these primary sources on 2026-10-11 by automated editorial review. The 20 ms measurement is illustrative, not a reported benchmark.
