---
id: "FLO-11"
question: "Explain map, filter, transform, onEach, and launchIn."
topic: "Flow, StateFlow, SharedFlow & Channels"
code: "FLO"
group: "B"
phase: 1
priority: "P1"
order: 124
editorial_status: "reviewed"
---

# FLO-11

## Original interview question

Explain map, filter, transform, onEach, and launchIn.

## What the interviewer evaluates

Explain lazy transformations and the terminal nature of launchIn.

## Explanation in Arabic

`map` يحوّل كل value، و`filter` يعدّي اللي يحقق شرط، و`transform` ممكن يطلع صفر أو أكثر لكل input، و`onEach` side effect زي logging من غير تغيير القيمة. كل دول intermediate وlazy في cold Flow. `launchIn(scope)` terminal: يبدأ collection في scope ويرجع Job لازم owner يتحكم فيه.

### Practical walkthrough in Egyptian Arabic

في pipeline منتجات، `map` تحول DTO لـUI model، `filter` تشيل غير المتاح، `transform` ممكن تطلع صفر أو أكتر لكل input، و`onEach` للمراقبة أو side effect صغيرة، لكن لا تبدأ collection. `launchIn(viewModelScope)` terminal operator يبدأ جمع في Job؛ لو كررتها في init مرتين يبقى عندك collectors اتنين. راقب exception والـscope.

## Why it matters and how it works

Operators run when collected, in order, under the flow context unless `flowOn` changes upstream. `onEach` is convenient for side effects but should not become a hidden business mutation. `launchIn(scope)` is shorthand for launching collection in the scope, so failure and cancellation follow that Job tree.

## Worked example

JVM example requires coroutines-core; logger is injected and the returned Job remains owned by the caller.

```kotlin
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Job
import kotlinx.coroutines.flow.*

fun observeCounts(scope: CoroutineScope, source: Flow<List<String>>): Job =
    source.map { it.size }
        .filter { it > 0 }
        .onEach { println("count=$it") }
        .launchIn(scope)
```

## Trade-offs and decision criteria

Use map for one-to-one conversion, transform for variable emissions, filter for selection, onEach for observable effects. Prefer `collect` inside a suspending operation when its completion matters. `launchIn` is convenient for owned long-lived observation but can hide a Job if discarded.

## Failure modes

Calling `launchIn(GlobalScope)` detaches collection. Putting expensive blocking logging in `onEach` can slow upstream and UI. Repeating a cold pipeline with multiple collectors repeats its side effects.

## Production perspective

A ViewModel derives unread counts from Room rows and launches one collection in its scope only if it must update an external observer; usually it exposes a derived StateFlow and lets UI collect with lifecycle awareness.

## Interview answer — short

“map transforms, filter selects, transform can emit multiple outputs, and onEach performs a side effect. They are lazy intermediate operators. launchIn starts collection in a scope and returns a Job that needs ownership.”

## Interview answer — structured

“I treat a Flow chain as a declarative pipeline until a terminal operator runs. `map` maps one input to one output; `filter` drops values; `transform` can emit zero or several; `onEach` observes values for effects such as metrics. `launchIn(scope)` is terminal and starts collection in that scope. In Android I use a ViewModel scope for producer work and lifecycle-aware collection in the UI. I keep side effects lightweight and do not discard the Job when cancellation or errors matter.”

## Interview answer — deep senior

“Operator choice affects both semantics and lifetime. Intermediate operators on a cold Flow do not execute at construction; each collection traverses them. `transform` is more general than `map`, but that flexibility can obscure one-to-many behavior, so I use the narrowest operator that matches the contract. `onEach` preserves values but its block can suspend or throw, affecting the whole stream. `launchIn` starts the pipeline in an explicit scope and returns a Job; it is not fire-and-forget. I choose a scope whose cancellation matches the data need, avoid blocking telemetry in the chain, and test repeated subscriptions for duplicate side effects. If a collector must return a result, a terminal suspend operator may be clearer. I would write the order of operators left to right and say what each does to cardinality. `map` makes one output from each input; `filter` can discard; `transform` can emit zero, one, or many. `onEach` observes each upstream value and is useful for a small side effect, but it does not start a cold flow. `launchIn(scope)` is equivalent to launching a coroutine that collects and is a terminal operation; its Job is tied to that scope. This means placement and ownership matter. A network call in `onEach` can slow the pipeline or repeat for each collector, so business effects need deliberate boundaries. I would test one collector, cancellation, and error propagation, and avoid launching the same pipeline twice in ViewModel initialization.”

## How to answer in the interview

- **Why:** operator order changes values and side effects.
- **How:** explain cardinality and launchIn as terminal collection.
- **Trade-off:** onEach is convenient but can repeat work.
- **Failure case:** duplicate launchIn collectors.
- **Production solution:** named owner scope and cancellation/error tests.

## Deep-dive talking points

Trace laziness, operator cardinality, failure from onEach and Job lifetime from launchIn.

## Follow-up questions

- [FLO-12](../flo-12/): Which terminal operator gets one value? **Answer:** `first` suspends until the first matching value then cancels collection.
- [FLO-17](../flo-17/): Which operators move with flowOn? **Answer:** those upstream of the flowOn boundary.

## Self-check rubric

Can I classify each operator, predict output count and own the returned collection Job?

## References and reviewed-on date

- [Kotlin Flow API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-flow/) — intermediate and terminal operators.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-11; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
