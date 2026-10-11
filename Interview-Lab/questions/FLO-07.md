---
id: "FLO-07"
question: "How do you expose read-only state via asStateFlow()?"
topic: "Flow, StateFlow, SharedFlow & Channels"
code: "FLO"
group: "A"
phase: 1
priority: "P1"
order: 120
editorial_status: "reviewed"
---

# FLO-07

## Original interview question

How do you expose read-only state via asStateFlow()?

## What the interviewer evaluates

Explain read-only exposure without claiming it makes underlying objects immutable.

## Explanation in Arabic

بنخلي `MutableStateFlow` private ونعرّض `StateFlow` عبر `asStateFlow()` علشان المستهلك يقدر يقرأ ويعمل collect لكن ما يقدرش يغيّر `value` مباشرة. الـViewModel يفضل owner للتحديثات. ده بيحمي API surface، لكنه مش بيحوّل list mutable جوه state إلى immutable، ولا يمنع reference قديم من تغيير نفس object.

## Why it matters and how it works

`asStateFlow()` returns a read-only view of the same hot state source; it does not copy data. Use immutable state classes/lists and atomic `update` when concurrent writers may modify state. Keep mutation functions small and domain-specific.

## Worked example

JVM example uses `kotlinx-coroutines-core`; immutable data class state and an atomic transformation.

```kotlin
import kotlinx.coroutines.flow.*

data class CounterState(val value: Int)
class CounterViewModelState {
    private val mutable = MutableStateFlow(CounterState(0))
    val state: StateFlow<CounterState> = mutable.asStateFlow()
    fun increment() { mutable.update { it.copy(value = it.value + 1) } }
}
```

## Trade-offs and decision criteria

Read-only exposure prevents arbitrary callers from assigning state but is not authorization/security isolation. An interface property is also possible; `asStateFlow()` makes the intent explicit. Immutable snapshots and a single source of truth remain important.

## Failure modes

Exposing `MutableStateFlow` lets UI code write values that bypass validation. Returning a read-only StateFlow containing a mutable list still allows in-place list mutation and equality bugs. A non-atomic `state.value = state.value.copy(...)` can race with another writer.

## Production perspective

A checkout ViewModel exposes a read-only price state and methods for quantity changes. Validation and total calculation stay inside the owner; the UI cannot publish arbitrary totals. Business authority still belongs to the backend.

## Interview answer — short

“I keep MutableStateFlow private and expose `asStateFlow()` so consumers can read and collect but not assign values. I also publish immutable snapshots and use `update` for concurrent transformations.”

## Interview answer — structured

“Read-only exposure is an encapsulation boundary. The ViewModel owns the private MutableStateFlow and exposes a StateFlow view via `asStateFlow`, while public methods express allowed state transitions. It is the same underlying stream, not a defensive copy. If the state object contains mutable collections, consumers can still mutate them, so I use immutable data and avoid leaking mutable references. For concurrent writers I prefer `update`, which performs an atomic transformation. Read-only exposure prevents arbitrary callers from assigning state but is not authorization/security isolation. An interface property is also possible; `asStateFlow()` makes the intent explicit. Immutable snapshots and a single source of truth remain important. A checkout ViewModel exposes a read-only price state and methods for quantity changes. Validation and total calculation stay inside the owner; the UI cannot publish arbitrary totals.”

## Interview answer — deep senior

“The read-only type prevents accidental external writes to the flow, but not every form of mutation. `asStateFlow()` delegates to the same source, so a mutable list or object stored as the value can still be changed in place, potentially hiding an update because StateFlow uses equality-based conflation. I design a small transition API, publish fresh immutable snapshots and use atomic `update` when multiple coroutines may modify state. For a payment screen I do not trust UI state as transaction authority: the server and durable repository determine the final status. Tests verify that rapid actions preserve updates and that no caller can bypass the owner’s validation. `asStateFlow()` returns a read-only view of the same hot state source; it does not copy data. Use immutable state classes/lists and atomic `update` when concurrent writers may modify state. Keep mutation functions small and domain-specific. Exposing `MutableStateFlow` lets UI code write values that bypass validation. Returning a read-only StateFlow containing a mutable list still allows in-place list mutation and equality bugs. A non-atomic `state.value = state.value.copy(...)` can race with another writer. A checkout ViewModel exposes a read-only price state and methods for quantity changes. Validation and total calculation stay inside the owner; the UI cannot publish arbitrary totals. Business authority still belongs to the backend.”

## Deep-dive talking points

Contrast API immutability, value immutability and server authority.

## Follow-up questions

- [FLO-06](../flo-06/): Why use immutable values? **Answer:** in-place mutation can prevent meaningful emissions under equality conflation.
- [COR-19](../cor-19/): Does read-only exposure prevent races? **Answer:** no; concurrent owner writes still need atomic updates.

## Self-check rubric

Can I encapsulate mutation, explain shared underlying stream, publish immutable values and handle concurrent updates?

## References and reviewed-on date

- [Kotlin StateFlow API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-state-flow/) — `asStateFlow` and `update`.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-11; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
