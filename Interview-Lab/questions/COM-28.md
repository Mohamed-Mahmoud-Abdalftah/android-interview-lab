---
id: "COM-28"
question: "When should you avoid derivedStateOf because its overhead exceeds the benefit?"
topic: "Jetpack Compose"
code: "COM"
group: "C"
phase: 3
priority: "P1"
order: 257
editorial_status: "reviewed"
---

# COM-28

## Original interview question

When should you avoid derivedStateOf because its overhead exceeds the benefit?

## What the interviewer evaluates

- Explain the intended mismatch between fast input and slow-changing result.
- Recognize that dependency tracking/observation costs time and memory.
- Compare direct calculation, remember, Flow transformation and measurement.

## Concept and technical explanation

While derivedStateOf is a vital optimization tool in Jetpack Compose, it introduces measurable memory and computation overhead that can degrade performance if misused. derivedStateOf should be strictly avoided when the calculated output state mutates at the exact same or higher frequency as the input state, such as performing simple string concatenations or basic uppercase transformations. In these scenarios, derivedStateOf cannot filter out any recompositions, but still incurs the continuous penalty of allocating DerivedSnapshotState objects, maintaining dependency read observers, and performing change comparisons. It should also be avoided when calculating values derived from plain Kotlin variables that are not Compose Snapshot States.

## Practical walkthrough (English)

Contrasting wasteful vs beneficial uses of derivedStateOf:
```kotlin
// ❌ ANTI-PATTERN: Wasteful derivedStateOf! Output changes on EVERY input change!
// When 'query' updates, 'uppercaseQuery' updates simultaneously! Zero recomposition filtering!
// Incurs allocation overhead of DerivedSnapshotState and read tracking for NO benefit!
@Composable
fun BadSearchInput(query: String) {
    // ❌ WRONG: Plain calculation is cheaper than derivedStateOf!
    val uppercaseQuery = remember {
        derivedStateOf { query.uppercase() }
    }
    // ✅ BETTER: Just compute directly or use simple remember(query)!
    // val uppercaseQuery = remember(query) { query.uppercase() }
    Text("Search: ${uppercaseQuery.value}")
}

// ✅ ARCHITECTURAL BEST PRACTICE: High-frequency input -> Low-frequency output!
// Input (scrollOffset) changes hundreds of times per second (every pixel)!
// Output (showScrollToTop) changes ONLY TWICE (false -> true or true -> false)!
// Saves thousands of recomposition passes during scrolling!
@Composable
fun OptimizedScrollToTopButton(listState: LazyListState) {
    val showButton by remember {
        derivedStateOf { listState.firstVisibleItemIndex > 5 }
    }

    if (showButton) {
        FloatingActionButton(onClick = { /* scroll to top */ }) { Icon(Icons.Default.KeyboardArrowUp, "Top") }
    }
}
```

## Explanation in Arabic

متى يجب تجنب استخدام `derivedStateOf` لأن تكلفة استخدامه (Overhead) تتجاوز فائدته؟

1. كيف يعمل `derivedStateOf` وما هي تكلفته الخفية؟
   - دالة `derivedStateOf` تنشئ كائناً خاصاً في الذاكرة يُسجل نفسه في نظام الـ Snapshot System لمراقبة كل الحالات المقروءة بداخله.
   - في كل تعديل لأي حالة، يتم حساب الدالة، ومقارنة الناتج عبر `equals()`، وتحديث الـ Snapshot Records.
   - هذا يعني وجود **تكلفة حجز ذاكرة (Allocation Overhead)** وتكلفة معالجة مستمرة للمراقبة.

2. متى يجب **تجنب** `derivedStateOf` تماماً؟
   - **عندما تتغير الحالة المدخلة بنفس معدل تغير الناتج (1:1 Change Ratio)**:
     * مثال: دمج اسمين `derivedStateOf { "$firstName $lastName" }`.
     * هنا، كلما تغير الاسم سيتغير الناتج حتماً! لا يوجد أي تخميد (Dampening) للتردد! استخدام `remember(firstName, lastName) { "$firstName $lastName" }` أسرع وأخف بمراحل بدون أي Snapshot overhead.
   - **عند العمليات الحسابية البسيطة جداً**: العمليات البدائية (مثل جمع رقمين) لا تستحق إنشاء كائن مراقبة كامل في الـ Heap.

3. متى يكون `derivedStateOf` مفيداً وضرورياً فقط؟
   - **فقط عندما تتغير المدخلات بمعدل أعلى بكثير من تغير الناتج (Many-to-One / Frequency Dampening)**:
     * مثال: موضع التمرير `scrollOffset` يتغير 60 مرة في الثانية (آلاف البكسلات)، ولكن الناتج قيمة منطقية بسيطة: `derivedStateOf { scrollOffset > 100 }` (تتغير مرتين فقط: true أو false).

## Practical walkthrough

المقارنة بين الاستخدام الخاطئ لـ derivedStateOf والاستخدام السليم:
```kotlin
// ❌ استخدام خاطئ: هدر في الذاكرة والمعالج؛ المدخلات تتغير بنفس معدل الناتج:
@Composable
fun BadFullNameDisplay(firstName: String, lastName: String) {
    // 💥 خطأ: derivedStateOf هنا يضيف حجز كائنات ومراقبة snapshots دون أي فائدة!
    val fullName by remember { derivedStateOf { "$firstName $lastName" } }
    Text(fullName)
}

// ✅ الاستخدام الأفضل والأخف لدمج النصوص العادية: استخدام remember العادي:
@Composable
fun GoodFullNameDisplay(firstName: String, lastName: String) {
    val fullName = remember(firstName, lastName) { "$firstName $lastName" }
    Text(fullName)
}

// ✅ الاستخدام المثالي والضروري لـ derivedStateOf: تخميد الترددات العالية (Frequency Dampening):
@Composable
fun ScrollToTopButton(listState: LazyListState) {
    // listState.firstVisibleItemIndex يتغير باستمرار مع السكرول، ولكن النتيجة Boolean تتغير نادراً:
    val showButton by remember {
        derivedStateOf { listState.firstVisibleItemIndex > 0 }
    }
    if (showButton) {
        FloatingActionButton(onClick = { /* سكرول للأعلى */ }) { Text("Top") }
    }
}
```

## Why it matters and how it works

Derived state observes snapshot inputs and updates consumers when its result changes under equality semantics. It can avoid downstream recomposition for a threshold result that stays the same across many input values. Creating and maintaining that observation has overhead, so if output changes as often as input, little invalidation is saved. If a calculation is expensive but unrelated to fast snapshot reads, another memoization or data-layer strategy may fit better.

## Worked example

While a list scrolls from pixel offset 1 through 200 on the first item, `showTopButton = firstVisibleItemIndex > 0` remains false; a derived state can keep consumers from reacting to every offset. For a full name from two text fields, each edit usually changes the displayed string, so `derivedStateOf` adds tracking without reducing updates. A product search result belongs in a cancelable ViewModel pipeline.

### Compose/Kotlin walkthrough

```kotlin
@Composable
fun Profile(first: String, last: String, listState: LazyListState) {
    val fullName = "$first $last" // Direct calculation: changes with an edit.
    val showTop by remember(listState) {
        derivedStateOf { listState.firstVisibleItemIndex > 0 }
    }
    Column {
        Text(fullName)
        if (showTop) Text("Back to top")
    }
}
// Imports: runtime.remember/derivedStateOf/getValue, foundation.lazy.LazyListState.
```

## Trade-offs and decision criteria

Use derived state when measured unnecessary downstream work exceeds observation cost. Direct expression is simpler for cheap, correlated inputs. `remember(inputs)` caches a calculation by explicit keys but has different semantics and can go stale if keys are incomplete. Flow transformations may be better for repository data and asynchronous work.

## Failure modes

Every trivial expression gets wrapped, increasing objects and complexity. A developer assumes `derivedStateOf` performs a background calculation; it does not. The UI stops updating because a remembered derived lambda captures the wrong object. An expensive full-list sort still runs in composition despite the wrapper.

## Production perspective

Use a representative trace and frame benchmark, count actual output transitions relative to input changes, and test correctness under key/source changes. Remove derived state if it adds complexity without measured benefit.

## Interview answer — short

Avoid derivedStateOf when the output changes at the same frequency as the input, such as converting text to uppercase or simple formatting. In these cases, derivedStateOf cannot filter out any recompositions, but still adds the overhead of allocating snapshot state objects and tracking dependency reads. Only use derivedStateOf when the input updates significantly more frequently than the output, like checking a scroll threshold where pixels change constantly but the boolean output changes rarely.

## Interview answer — structured

Understanding when NOT to use derivedStateOf separates junior Compose developers from seasoned performance engineers.
The purpose of derivedStateOf is to act as a recomposition filter: it prevents observers from recomposing when high-frequency input mutations do not alter the final calculated output.
Consequently, applying derivedStateOf is counterproductive in two primary scenarios.
First, avoid derivedStateOf when the derived result mutates at the exact same frequency as the input state.
A classic anti-pattern is writing: derivedStateOf { firstName + " " + lastName } or derivedStateOf { text.uppercase() }.
Every time the input changes, the derived string changes as well.
Because the output changes on every single step, derivedStateOf skips zero recompositions.
However, it still incurs the penalty of allocating a DerivedSnapshotState heap object, registering snapshot read observers, and executing equality comparisons on every frame.
In this case, a plain inline expression or simple remember(key) is vastly faster and consumes less memory.
Second, avoid derivedStateOf when inputs are not Compose Snapshot States.
If the dependencies inside the lambda are standard Kotlin variables or immutable parameters, derivedStateOf cannot observe them, leading to stale or broken UI states.

## Interview answer — deep senior

Under the hood, derivedStateOf instantiates an internal DerivedSnapshotState<T> object, which is significantly more complex and resource-intensive than a standard MutableState primitive.
When a derivedStateOf calculation executes, Compose initializes a calculation scope and attaches an active Snapshot.readObserver.
This observer intercepts every SnapshotMutableState read within the lambda block, constructing a dynamic dependency array stored in the SlotTable.
On every subsequent frame where any state commits in the global Snapshot system, the Compose runtime must traverse these registered dependency arrays to determine if any tracked inputs were modified.
If inputs changed, it executes the calculation lambda, retrieves the new result, and performs an equals() structural equality check against the cached value.
If the output changed, it invalidates downstream RecomposeScopes.
If you apply this machinery to a 1:1 mapping (where input change always produces output change), you force the CPU to perform all this dependency recording, array traversal, and equality diffing without gaining any skipping benefits.
By contrast, a simple remember(key1, key2) { calculation } uses standard compiler bitmask checks: if the keys equal their previous SlotTable slot values, it returns the cached instance in O(1) time with zero read-observer overhead.
Senior engineers reserve derivedStateOf strictly for N:1 reduction scenarios, such as mapping continuous pixel scroll offsets to boolean visibility toggles.

## How to answer in the interview

- **Why:** derived state helps only when output changes less often than input.
- **How:** compare fullName on edits with a scroll threshold.
- **Trade-off:** dependency tracking and equality checks cost work.
- **Failure case:** using it as a generic cache for business searches.
- **Production solution:** keep simple values direct and measure the threshold case.

## Deep-dive talking points

Discuss input/output change ratio, observation overhead, comparison to remember, background-work myth, and profiling.

## Follow-up questions

- **Interviewer:** "What happens if no Compose `State` is read inside a `derivedStateOf` block?"
  **Answer:** "It registers zero snapshot dependencies. If plain parameters change, the derived state will never invalidate or recalculate, producing a stale value indefinitely."

- **Interviewer:** "How does `remember(keys)` differ from `derivedStateOf` in memory footprint?"
  **Answer:** "`remember(keys)` stores only the computed value in the Slot Table and checks parameter equality. `derivedStateOf` allocates a `DerivedSnapshotState` object, dependency tracking sets, and registers a snapshot observer."

## Self-check rubric

Compare two examples, identify tracking cost, and choose a measured alternative.

## References and reviewed-on date

- [Side-effects in Compose](https://developer.android.com/develop/ui/compose/side-effects) — `derivedStateOf` cost and examples.

Technically reviewed against primary documentation on 2026-10-13.
