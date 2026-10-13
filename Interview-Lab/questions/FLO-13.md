---
id: "FLO-13"
question: "Compare combine and zip."
topic: "Flow, StateFlow, SharedFlow & Channels"
code: "FLO"
group: "B"
phase: 1
priority: "P1"
order: 126
editorial_status: "reviewed"
---

# FLO-13

## Original interview question

Compare combine and zip.

## What the interviewer evaluates

Compare latest-pair combination with positional pairing.

## Explanation in Arabic

`combine` بيطلع قيمة جديدة لما أي upstream يطلع بعد ما كل مصدر قدّم قيمة أولى؛ يستخدم أحدث قيمة من كل واحد. `zip` يقرن الأولى بالأولى والتانية بالتانية وينتظر pairs؛ لو واحد خلص من غير شريك يقف. UI state من Room + filter غالبًا `combine`؛ pairing خطين من نتائج متطابقة بالترتيب قد يناسب `zip`.

### Practical walkthrough in Egyptian Arabic

لو `priceFlow` و`currencyFlow` بيتغيروا بسرعات مختلفة، `combine` يطلع آخر price مع آخر currency بعد ما الاتنين يطلعوا أول قيمة؛ كل تغيير بعد كده يحدث النتيجة. `zip` يطابق أول مع أول وثاني مع ثاني وينتهي حسب اكتمال أحد المصدرين؛ مناسب pairing محدود، مش شاشة dashboard حية. جرب emissions غير متساوية في test.

## Why it matters and how it works

`combine` can emit many outputs for a burst from one side using latest counterpart; it is not an atomic database snapshot across independent sources. `zip` queues/pairs emissions and completes when pairs cannot continue. Choose based on temporal semantics, not just syntax.

## Worked example

JVM example uses coroutines-core; both streams are typed and the combined result is current UI data.

```kotlin
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.combine
import kotlinx.coroutines.flow.zip

fun visible(items: Flow<List<String>>, query: Flow<String>): Flow<List<String>> =
    items.combine(query) { all, q -> all.filter { it.contains(q, true) } }
fun paired(a: Flow<Int>, b: Flow<Int>): Flow<Pair<Int, Int>> =
    a.zip(b) { x, y -> x to y }
```

## Trade-offs and decision criteria

Combine reacts to independent state changes but may recompute frequently; debounce or distinct state upstream if appropriate. Zip preserves positional pairing but can stall if one side pauses and silently truncate when one completes early.

## Failure modes

Zipping a rapidly changing search query with Room items gives mismatched positional pairs and stale UI. Combining two server responses without version or transaction validation can still create a logically inconsistent composite.

## Production perspective

A catalog screen combines current cached items with text filter state, showing a new list on either change. A backend quote requiring correlated prices uses a server-generated version or transaction ID rather than assuming combine makes independent data atomic.

## Interview answer — short

“combine uses the latest value from each source after both have emitted; zip pairs values by position. I use combine for independent changing UI state and zip only when pair-by-order semantics are truly intended.”

## Interview answer — structured

“`combine` waits for an initial value from each upstream and then emits whenever either changes, using the other’s latest value. That matches a product list combined with a search filter. `zip` pairs the nth value of one flow with the nth of the other and cannot continue once pairing is impossible. I avoid zip for unrelated UI state because a fast source can wait or end unexpectedly. I also do not mistake combine for an atomic snapshot: if cross-source consistency matters, I need versions or one authoritative transaction.”

## Interview answer — deep senior

“The two operators answer different time questions. Combine asks, ‘What is the latest pair now?’ and may recompute repeatedly as either stream changes. Zip asks, ‘What is pair number n?’ and naturally fits coordinated finite sequences, but a slow side backpressures pairing and an early completion ends it. For Android state, combine usually fits Room rows plus a filter or connectivity flag. I control expensive transformations and ensure the UI can represent loading before each source first emits. For price and inventory, the latest independent values may come from different server revisions; a versioned backend aggregate is needed for a consistent checkout. Tests vary source rates and completion order to expose accidental assumptions. I would compare the pairing rule, not just the function names. `combine` waits until each upstream has produced a value, then emits a result whenever either source updates using the latest value from the other. That fits a UI derived from current account and current settings. `zip` pairs the nth value from each source and advances in lockstep, so a fast side waits for the slower side and completion can end the paired stream. It is useful for corresponding finite sequences, not for a long-lived screen that should react whenever either input changes. I would demonstrate with two flows of unequal speed and list the emitted pairs. When one input is StateFlow, combine can use its current value immediately as one side.”

## How to answer in the interview

- **Why:** live UI needs latest combination, finite pairs need matching positions.
- **How:** trace unequal-rate sources.
- **Trade-off:** combine can update often; zip waits.
- **Failure case:** zip leaves dashboard stale.
- **Production solution:** test first emission and completion behavior.

## Deep-dive talking points

Trace emission timelines for both operators and identify where version consistency must be enforced.

## Follow-up questions

- [FLO-14](../flo-14/): Which operator switches inner requests? **Answer:** `flatMapLatest` cancels the previous inner collection.
- [FLO-28](../flo-28/): Does combine make remote/cache atomic? **Answer:** no; the repository still defines source of truth and versions.

## Self-check rubric

Can I draw both timelines, predict completion and state one cross-source consistency limit?

## References and reviewed-on date

- [Kotlin Flow API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-flow/) — combine and zip.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-11; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
