---
id: "COM-12"
question: "What are rememberUpdatedState, derivedStateOf, and snapshotFlow?"
topic: "Jetpack Compose"
code: "COM"
group: "B"
phase: 3
priority: "P1"
order: 241
editorial_status: "reviewed"
---

# COM-12

## Original interview question

What are rememberUpdatedState, derivedStateOf, and snapshotFlow?

## What the interviewer evaluates

- Distinguish latest captured value, derived Compose state, and Flow from snapshots.
- Use each only for the right update frequency and boundary.
- Identify overhead and lifecycle/cancellation requirements.

## Explanation in Arabic

`rememberUpdatedState` تعطي effect طويلة أحدث value/callback بدون إعادة تشغيلها لمجرد أن المرجع تغير. `derivedStateOf` ينتج State مشتقة ويمنع updates عندما المدخلات تتغير كثيرًا لكن النتيجة المهمة لم تتغير؛ له تكلفة، فلا تستخدمه لأي string concatenation بسيطة. `snapshotFlow { ... }` يقرأ snapshot state ويصدرها كـFlow عند التغير، مناسب لتحويل scroll threshold إلى pipeline تحليل أو operators مثل `distinctUntilChanged`. الثلاثة ليست بدائل عامة للـViewModel ولا تخزين دائم؛ افهم أولًا من يقرأ ومن يملك collection.

### Practical walkthrough in Egyptian Arabic

في splash timer، callback ممكن تتغير لكن الـtimer مش لازم يبدأ من الأول؛ `rememberUpdatedState` تحافظ على أحدث callback. في scroll، `derivedStateOf` مناسبة لو القيمة `showTop` بتتغير أقل بكتير من offset. ولو محتاج analytics كـFlow، `snapshotFlow` داخل effect مع `distinctUntilChanged`، والـcollector يتلغي مع الشاشة. `snapshotFlow` مش تخزين دائم؛ لو collector اتلغى، analytics اللحظية ممكن تفوت حسب contract. اختبر threshold وlatest callback وخروج الشاشة، وقِس تكلفة derived state قبل الاحتفاظ بها.

## Why it matters and how it works

An effect's closure can retain an old parameter unless the effect restarts or reads an updated state wrapper. Derived state tracks snapshot inputs and exposes a result whose changes can limit downstream invalidation. `snapshotFlow` bridges snapshot reads into a cold Flow collected by a coroutine; it observes changes relevant to its block and emits values under its documented equality behavior. Collection must be canceled with its owner.

## Worked example

A lifecycle observer is registered once for `lifecycleOwner`; it invokes the latest `onStart` callback via `rememberUpdatedState` without unregistering for every lambda change. A scroll-to-top button uses `derivedStateOf { listState.firstVisibleItemIndex > 0 }` so it only cares when threshold truth changes. Analytics observes `snapshotFlow { listState.firstVisibleItemIndex }` in a `LaunchedEffect(listState)` and applies Flow operators before reporting.

### Compose/Kotlin walkthrough

```kotlin
@Composable
fun ScrollSignals(listState: LazyListState, onPastFirst: () -> Unit) {
    val latestCallback by rememberUpdatedState(onPastFirst)
    val showTop by remember(listState) {
        derivedStateOf { listState.firstVisibleItemIndex > 0 }
    }
    LaunchedEffect(listState) {
        snapshotFlow { listState.firstVisibleItemIndex }
            .map { it > 0 }.distinctUntilChanged().filter { it }
            .collect { latestCallback() }
    }
    if (showTop) Text("Back to top")
}
// Imports: foundation.lazy.LazyListState, runtime.*, kotlinx.coroutines.flow.*.
```

## Trade-offs and decision criteria

`rememberUpdatedState` prevents unnecessary restarts but does not fix a wrong lifecycle owner key. `derivedStateOf` can save recompositions when input changes often and output rarely, but its tracking overhead exceeds direct computation for cheap correlated values. `snapshotFlow` is appropriate when Flow processing is needed; a simple Compose `Text` can read state directly.

## Failure modes

An observer stays attached to an old LifecycleOwner because only the callback was updated. Every string expression is wrapped in `derivedStateOf`, making code slower and harder to read. A `snapshotFlow` collector is launched in a global scope and survives the screen. An analytics event is duplicated after collection restarts without deduplication policy.

## Production perspective

Use keyed effects with accurate owners, measure the derived-state benefit in a real workload, and test scroll threshold transitions and lifecycle restarts. Keep analytics event semantics explicit when reconnection can repeat observations.

## Interview answer — short

“`rememberUpdatedState` gives long-running effects fresh values; `derivedStateOf` tracks a derived Compose result; `snapshotFlow` exposes snapshot reads as a Flow. Use the latest callback wrapper, derived state, and snapshotFlow for three different needs.”

## Interview answer — structured

“I use `rememberUpdatedState` when a registered effect should keep its lifecycle but call a new callback. I use `derivedStateOf` when fast-changing input produces a slower-changing result that the UI reads, such as whether scroll passed the first item. I use `snapshotFlow` when I want Flow operators over Compose state, often for scroll analytics. These choices have costs: derived state is not a free memoization wrapper, and a snapshotFlow collector still needs an owner and cancellation. I would use a scroll threshold to explain derivedStateOf and a Flow of scroll state for analytics.”

## Interview answer — deep senior

“I decide based on the boundary I am crossing. If a `DisposableEffect` registers a lifecycle observer, changing an `onStart` callback should not necessarily tear down the observer. `rememberUpdatedState` lets that listener invoke the latest callback while the observer's actual owner remains a key; if the owner changes, I still restart registration. `derivedStateOf` helps when an input changes frequently but a derived value changes rarely enough that avoiding downstream recomposition pays for dependency tracking. A boolean scroll threshold is a good example; concatenating two names on every edit is not. `snapshotFlow` turns reads of Compose snapshot state into a cold Flow, useful when I need `distinctUntilChanged`, debounce, or other Flow processing before analytics or side effects. I collect it in a keyed `LaunchedEffect` or another owned scope and consider re-subscription effects. None of these APIs solves persistence or business-state ownership. I test key changes, latest callback delivery, threshold crossings, and cancellation on screen exit, then profile if `derivedStateOf` was introduced for performance. The intent should remain obvious to the next engineer. I would not derive a full name just because the API exists; the output changes on each relevant edit.”

## How to answer in the interview

- **Why:** these APIs solve different observation and lifetime problems.
- **How:** identify latest callback, low-frequency derived value, and Flow bridge.
- **Trade-off:** derived tracking has cost.
- **Failure case:** restarting a long effect for every callback change.
- **Production solution:** key by actual work identity and cancel collection on exit.

## Deep-dive talking points

Discuss stale closures, identity keys, derived-state cost, snapshot-to-Flow bridge, and collector cancellation.

## Follow-up questions

- Should callback changes always restart a registered observer? **Answer:** no; `rememberUpdatedState` can supply the latest callback while owner identity remains stable.
- When is `derivedStateOf` wasteful? **Answer:** when direct computation is cheap and output changes as often as inputs.
- Is `snapshotFlow` durable storage? **Answer:** no; it is a Flow view of observed Compose snapshot values.

## Self-check rubric

Match three examples to APIs, name one overhead trap, and explain lifecycle cleanup.

## References and reviewed-on date

- [Side-effects in Compose](https://developer.android.com/develop/ui/compose/side-effects) — all three APIs and examples.

Technically reviewed against this primary source on 2026-10-11 by automated editorial review. Analytics usage is illustrative.
