---
id: "FLO-12"
question: "Compare collect, collectLatest, and first."
topic: "Flow, StateFlow, SharedFlow & Channels"
code: "FLO"
group: "B"
phase: 1
priority: "P1"
order: 125
editorial_status: "reviewed"
---

# FLO-12

## Original interview question

Compare collect, collectLatest, and first.

## What the interviewer evaluates

Compare full collection, cancellation of previous action and one-value extraction.

## Explanation in Arabic

`collect` يعالج كل emission بالتتابع لحد ما Flow تخلص أو تتلغى. `collectLatest` لما value جديدة تيجي يلغي processing القديمة ويبدأ الأحدث، فمناسب search preview أو rendering قابل للإلغاء، مش كتابة مالية لازم تكتمل. `first` يستنى أول قيمة تطابق الشرط ويرجعها، وبعدها يوقف collection.

## Why it matters and how it works

`collectLatest` cancels the previous action block, not necessarily a remote side effect already committed. `first()` is terminal and completes after one value; on an empty finite flow it throws unless nullable alternative is chosen. Collection of StateFlow normally remains active until cancelled.

## Worked example

JVM illustration; expensiveRender must cooperate with cancellation for collectLatest to save work.

```kotlin
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.collectLatest
import kotlinx.coroutines.flow.first

suspend fun renderLatest(source: Flow<String>, render: suspend (String) -> Unit) {
    source.collectLatest { render(it) }
}
suspend fun initial(source: Flow<String>): String = source.first()
```

## Trade-offs and decision criteria

Use collect when every element matters, collectLatest when only newest processing matters, and first for one snapshot. If every event represents a required business write, do not use collectLatest to discard it; persist and acknowledge separately.

## Failure modes

`collectLatest` cannot undo a server request already sent by a cancelled action. `first()` on a StateFlow returns current value immediately, which may be Loading rather than data. A forever-running collect in the wrong scope can retain UI work.

## Production perspective

A search screen uses collectLatest to cancel stale preview rendering. A repository uses first with a predicate to await a Ready state when appropriate, under a timeout. Payment events are processed through durable state, not cancellable latest-only actions.

## Interview answer — short

“collect handles every emission, collectLatest cancels the previous action for a newer value, and first returns one value then stops. I use latest-only behavior only when old work can safely be abandoned.”

## Interview answer — structured

“The choice expresses product semantics. `collect` processes the stream sequentially. `collectLatest` cancels an in-progress action when a new value arrives, useful for a search result view where only the newest rendering matters. `first` is a terminal one-shot read and cancels the upstream after a value arrives. I consider what the initial StateFlow value means: `first()` might return Loading. I also do not use collectLatest for payments or durable writes, because cancelling a client action does not roll back an external effect.”

## Interview answer — deep senior

“I distinguish cancellation of local processing from cancellation of upstream or server work. `collectLatest` creates a child action for each emission and cancels the previous action on new data. If that action cooperates, stale CPU/UI work stops; if it already submitted a write, the server may still commit. `collect` is appropriate when each emission must be handled in order, though a slow collector can exert backpressure. `first` extracts one value and ends collection; for a state stream I may use a predicate such as Ready and a deadline so I do not return the initial Loading state or wait forever. Tests inject rapid emissions and verify whether old actions finish or cancel according to the chosen contract.”

## Deep-dive talking points

Trace cancellation boundary, initial StateFlow value, empty Flow behavior and external side effects.

## Follow-up questions

- [FLO-16](../flo-16/): Is collectLatest a buffer? **Answer:** no; it cancels prior collector action.
- [FLO-25](../flo-25/): Why use latest-only search? **Answer:** stale query results no longer match current input.

## Self-check rubric

Can I choose among all/latest/first, explain cancellation limits and test an initial Loading state?

## References and reviewed-on date

- [Kotlin Flow API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-flow/) — terminal operators.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-11; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
