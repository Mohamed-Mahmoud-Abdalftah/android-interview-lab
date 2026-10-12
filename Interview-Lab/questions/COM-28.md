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

## Explanation in Arabic

`derivedStateOf` مفيد عندما source state تتغير كثيرًا لكن القيمة المعروضة نادرًا ما تتغير، مثل `firstVisibleItemIndex > 0` أثناء scroll. لكنه يضيف state object وتتبع dependencies؛ إذا النتيجة تتغير مع كل input أو الحساب بسيط مثل `firstName + lastName`، فالكتابة المباشرة أو `remember` keyed حسب الحالة أوضح وأرخص غالبًا. لا تستخدمه كـcache عام لتحويل بيانات business كبيرة؛ انقل ذلك للـowner المناسب. قِس recomposition/frame cost قبل وبعد، ولا تنسَ صحة dependencies.

## Why it matters and how it works

Derived state observes snapshot inputs and updates consumers when its result changes under equality semantics. It can avoid downstream recomposition for a threshold result that stays the same across many input values. Creating and maintaining that observation has overhead, so if output changes as often as input, little invalidation is saved. If a calculation is expensive but unrelated to fast snapshot reads, another memoization or data-layer strategy may fit better.

## Worked example

While a list scrolls from pixel offset 1 through 200 on the first item, `showTopButton = firstVisibleItemIndex > 0` remains false; a derived state can keep consumers from reacting to every offset. For a full name from two text fields, each edit usually changes the displayed string, so `derivedStateOf` adds tracking without reducing updates. A product search result belongs in a cancelable ViewModel pipeline.

## Trade-offs and decision criteria

Use derived state when measured unnecessary downstream work exceeds observation cost. Direct expression is simpler for cheap, correlated inputs. `remember(inputs)` caches a calculation by explicit keys but has different semantics and can go stale if keys are incomplete. Flow transformations may be better for repository data and asynchronous work.

## Failure modes

Every trivial expression gets wrapped, increasing objects and complexity. A developer assumes `derivedStateOf` performs a background calculation; it does not. The UI stops updating because a remembered derived lambda captures the wrong object. An expensive full-list sort still runs in composition despite the wrapper.

## Production perspective

Use a representative trace and frame benchmark, count actual output transitions relative to input changes, and test correctness under key/source changes. Remove derived state if it adds complexity without measured benefit.

## Interview answer — short

“Avoid `derivedStateOf` when the result changes on nearly every input or is cheap to calculate; its tracking cost only pays when it suppresses meaningful downstream updates.”

## Interview answer — structured

“I reserve it for a fast-changing snapshot input with a slower-changing derived result, such as a scroll threshold. A full name updated on every keystroke does not benefit: output changes every time and the wrapper adds observation overhead. For expensive search or domain work I use an owned pipeline or correctly keyed cache rather than assuming derived state moves work off the main thread. I profile before and after.”

## Interview answer — deep senior

“I ask how often the source changes, how often the derived value changes, and what downstream work is actually avoided. `derivedStateOf` tracks snapshot dependencies and gives observers a value that need not update for every source change. It is useful for a threshold: a list's pixel offset changes rapidly while `showScrollToTop` remains false until the first item boundary is crossed. If both first and last name are edited and the full-name Text changes for nearly every edit, the derived wrapper adds tracking but saves no recomposition. It is also not a background executor; wrapping an expensive sort inside it can still block the UI when inputs invalidate. I would move large search or aggregation to an appropriate ViewModel/data pipeline, or use explicit `remember` keys for a small pure calculation when caching is justified. I measure release frame cost and allocations, and test that changed inputs cannot leave a stale result. The right optimization may be no abstraction at all. A small direct expression is often clearer and faster when there is no mismatch between input and output frequency.”

## Deep-dive talking points

Discuss input/output change ratio, observation overhead, comparison to remember, background-work myth, and profiling.

## Follow-up questions

- Does `derivedStateOf` move calculation off the main thread? **Answer:** no; it controls state observation, not dispatching.
- What is a good threshold example? **Answer:** showing a button only after the first list item is no longer visible.
- Why can full-name concatenation be a bad use? **Answer:** output changes with nearly every edit, so little downstream work is avoided.

## Self-check rubric

Compare two examples, identify tracking cost, and choose a measured alternative.

## References and reviewed-on date

- [Side-effects in Compose](https://developer.android.com/develop/ui/compose/side-effects) — `derivedStateOf` cost and examples.

Technically reviewed against this primary source on 2026-10-11 by automated editorial review. Performance depends on the concrete workload.
