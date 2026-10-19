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

`derivedStateOf` is useful when a rapidly changing Compose state produces a result that changes less often, allowing observers to skip work when the derived value stays equal. It has dependency-tracking overhead, so it is usually unnecessary for simple one-to-one transformations such as joining name fields. A direct expression or keyed `remember` is clearer for ordinary parameters. Be careful with plain parameters captured inside `remember { derivedStateOf { ... } }`: they are not snapshot reads and may remain stale when the parameter changes. The exact runtime cost depends on use and Compose version, so measure before treating this as a performance fix.

## Practical walkthrough (English)

Contrasting wasteful vs beneficial uses of derivedStateOf:
```kotlin
// Avoid this: the plain query parameter can become stale in remember.
// Every query edit normally changes the uppercase result, so little is filtered.
// A direct expression or keyed remember is clearer here.
@Composable
fun BadSearchInput(query: String) {
    // Plain calculation also avoids a stale captured query.
    val uppercaseQuery = remember {
        derivedStateOf { query.uppercase() }
    }
    // ✅ BETTER: Just compute directly or use simple remember(query)!
    // val uppercaseQuery = remember(query) { query.uppercase() }
    Text("Search: ${uppercaseQuery.value}")
}

// Useful case: a changing list position yields a less-changing boolean.
// The first visible item index can change while the boolean stays true.
// The output changes only when the threshold is crossed.
// Profile the screen to establish the actual benefit.
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

`derivedStateOf` مفيدة لما Compose State تتغير بسرعة لكن النتيجة المطلوبة تتغير أقل، فيقدر المستهلك يتجنب شغلاً غير لازم لما القيمة المشتقة تفضل نفسها. تتبع التبعيات له تكلفة، لذلك غالباً لا أحتاجها لعملية واحد لواحد مثل دمج اسمين. تعبير مباشر أو `remember` بمفاتيح واضح أكثر مع Parameters عادية. لازم أنتبه لو `remember { derivedStateOf { ... } }` التقط Parameter عادي: ده مش Snapshot Read وممكن القيمة تفضل قديمة بعد تغير الـ Parameter. تكلفة التنفيذ الدقيقة تعتمد على الاستخدام ونسخة Compose، فالمقياس الفعلي أهم من افتراض تحسن ثابت.

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

I avoid `derivedStateOf` when the result changes whenever its input changes, such as joining two name fields. It adds snapshot tracking without preventing a useful recomposition. A direct expression or `remember` with keys is usually clearer there. I use `derivedStateOf` when rapidly changing Compose state produces a result that changes much less often, like whether a list has scrolled past its first item. I would measure a performance concern rather than assume a universal speedup.

## Interview answer — structured

I reach for `derivedStateOf` when the UI reads a fast-changing state but only needs to react when a simpler result actually changes. A list scroll position can move on every drag, while a “show scroll-to-top button” boolean changes only when the first item crosses a boundary. That is a good fit.

I avoid it for a one-to-one calculation. If I derive `firstName + " " + lastName`, the output changes each time a name changes, so the extra derived state is unlikely to save recompositions. A direct expression is easier to read; `remember(firstName, lastName)` can help if the calculation is expensive and those values are ordinary parameters.

I also check what the lambda reads. `derivedStateOf` tracks Compose snapshot state reads; ordinary values captured without proper keys may become stale. If there is no high-frequency input or no meaningful reduction in downstream updates, I start with simpler code. I would inspect recomposition behavior and measure the screen before claiming the derived state improves performance.

## Interview answer — deep senior

The distinction is between caching a calculation and filtering observations. `remember(keys)` stores a value across recompositions and recalculates when the keys change. `derivedStateOf` creates a snapshot-derived state whose observed value can stay the same while its snapshot inputs change. That lets a composable avoid work when the derived result is unchanged, but dependency tracking has its own cost.

For a scrolling list, I might write `remember { derivedStateOf { listState.firstVisibleItemIndex > 0 } }`. The index may change through many values while the boolean stays true, so consumers do not need to respond to every index change. For a name string, every input edit normally changes the output, so the extra layer buys little. If the calculation reads plain parameters captured in a `remember { ... }` block, I would check whether those captures can change without recreating the derived state; stale captures are a correctness bug, not just a performance issue.

I would not present internal snapshot arrays, a fixed per-frame traversal cost, or a guaranteed memory comparison as the reason. Those details can change between Compose versions and depend on use. Instead I would use the documented behavior, then profile the actual screen when performance matters. Sometimes the right fix is to move a state read lower in the tree or simplify the composition rather than add derived state. The decision is whether the derived value filters enough changes to justify its complexity.

## How to answer in the interview

- **Why:** derived state helps only when output changes less often than input.
- **How:** compare fullName on edits with a scroll threshold.
- **Trade-off:** dependency tracking and equality checks cost work.
- **Failure case:** using it as a generic cache for business searches.
- **Production solution:** keep simple values direct and measure the threshold case.

## Deep-dive talking points

Discuss input/output change ratio, observation overhead, comparison to remember, background-work myth, and profiling.

## Follow-up questions

- **Interviewer:** "Would you use `derivedStateOf` to combine first and last name?"
  **Answer:** "Usually no. Each name edit changes the combined string, so there is little recomposition to filter. I would calculate it directly or use keyed `remember` if the calculation itself is expensive."

- **Interviewer:** "What can go wrong if the lambda captures a plain parameter?"
  **Answer:** "Snapshot tracking observes snapshot state reads, not every ordinary variable. If the derived state is remembered without the right keys, it can keep an old captured value."

- **Interviewer:** "How would you decide whether it helped?"
  **Answer:** "I would inspect the affected composable's recomposition behavior and profile the screen. I would not infer a speedup simply because the code uses `derivedStateOf`."

## Self-check rubric

Compare two examples, identify tracking cost, and choose a measured alternative.

## References and reviewed-on date

- [Side-effects in Compose](https://developer.android.com/develop/ui/compose/side-effects) — `derivedStateOf` cost and examples.

Technically reviewed against the cited primary documentation on 2026-10-19; agent editorial review, not human verification.
